"""
Enhanced Google Drive to GCS Migration Script with ZIP Extraction
Handles ZIP files by extracting and uploading contents to same folder
Version: 2.0 - No BigQuery
"""

import os
import json
import zipfile
import tempfile
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.cloud import storage
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import logging
from datetime import datetime, timezone
from pathlib import Path

import time
import random
from googleapiclient.errors import HttpError

# Configuration
SCOPES = [
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/cloud-platform'
]
SERVICE_ACCOUNT_FILE = os.environ.get('SERVICE_ACCOUNT_FILE', 'service-account-key.json')
DRIVE_FOLDER_ID = os.environ.get('DRIVE_FOLDER_ID')
GCS_BUCKET_NAME = os.environ.get('GCS_BUCKET_NAME')
PROJECT_ID = os.environ.get('PROJECT_ID')

# State File Configuration
STATE_FILE_BUCKET = os.environ.get('STATE_FILE_BUCKET', GCS_BUCKET_NAME)  # Can be same or different bucket
STATE_FILE_NAME = os.environ.get('STATE_FILE_NAME', 'migration_state.json')

# Rate Limiting Configuration
MAX_RETRIES = 5
INITIAL_BACKOFF = 1  # seconds

# Performance Configuration
STATE_SAVE_BATCH_SIZE = 10  # Save state every N files

def retry_on_rate_limit(func):
    """Decorator to retry API calls on rate limit errors with exponential backoff"""
    def wrapper(*args, **kwargs):
        retries = 0
        while retries <= MAX_RETRIES:
            try:
                return func(*args, **kwargs)
            except (HttpError, Exception) as e:
                # Catch SSL and Network issues common in Cloud Shell
                is_retryable = False
                error_str = str(e).lower()
                
                if isinstance(e, HttpError) and e.resp.status in [403, 429]:
                    is_retryable = True
                elif any(msg in error_str for msg in [
                    "decryption failed", "wrong version number", "connection reset", 
                    "broken pipe", "temporary failure in name resolution", 
                    "remote end closed connection", "internal error", "read operation timed out",
                    "bad record mac"
                ]):
                    is_retryable = True
                
                if is_retryable:
                    # Longer backoff for network/SSL issues
                    sleep_time = (INITIAL_BACKOFF * (2.5 ** retries)) + random.uniform(1, 3)
                    logging.warning(f"Connection/Network error: {error_str[:100]}. Retrying in {sleep_time:.2f}s...")
                    time.sleep(sleep_time)
                    retries += 1
                else:
                    raise e
        raise Exception("Max retries exceeded for Drive API call")
    return wrapper

# ZIP Extraction Configuration
ZIP_CONFIG = {
    'extract_zips': os.environ.get('EXTRACT_ZIPS', 'true').lower() == 'true',
    'delete_original_zip': os.environ.get('DELETE_ORIGINAL_ZIP', 'false').lower() == 'true',
    'max_zip_size_gb': float(os.environ.get('MAX_ZIP_SIZE_GB', '5')),
    'extract_nested_zips': os.environ.get('EXTRACT_NESTED_ZIPS', 'true').lower() == 'true',
    'upload_to_same_folder': True,
}

MAX_WORKERS = 8       # Increased for better performance (was 4)
CHUNK_SIZE = 50 * 1024 * 1024  # 50MB chunks (Stable for GDrive/GCS)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration_with_zip.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DriveToGCSWithZipExtraction:
    """Enhanced migrator with ZIP extraction support"""
    
    def __init__(self):
        # Store credentials for thread-local initialization
        self.credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
        
        # Thread-local storage for Drive + GCS clients
        self.thread_local = threading.local()
        
        self.stats = {
            'total_files': 0,
            'total_bytes': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'zips_extracted': 0,
            'zip_files_extracted': 0
        }
        
        # State management for resumable migrations
        self.processed_files = set()
        self.state_file_path = STATE_FILE_NAME
        self.load_state()
        
        logger.info("✓ Migration initialized (BigQuery tracking: Disabled)")
    
    def get_drive_service(self):
        """Get or create a thread-local Drive service instance"""
        if not hasattr(self.thread_local, "drive_service"):
            self.thread_local.drive_service = build('drive', 'v3', credentials=self.credentials, cache_discovery=False)
        return self.thread_local.drive_service

    def get_gcs_bucket(self):
        """Get or create a thread-local GCS bucket instance"""
        if not hasattr(self.thread_local, "storage_client"):
            self.thread_local.storage_client = storage.Client.from_service_account_json(SERVICE_ACCOUNT_FILE)
            self.thread_local.bucket = self.thread_local.storage_client.bucket(GCS_BUCKET_NAME)
        return self.thread_local.bucket
    
    def get_state_bucket(self):
        """Get GCS bucket for state file storage"""
        if not hasattr(self.thread_local, "state_storage_client"):
            self.thread_local.state_storage_client = storage.Client.from_service_account_json(SERVICE_ACCOUNT_FILE)
            self.thread_local.state_bucket = self.thread_local.state_storage_client.bucket(STATE_FILE_BUCKET)
        return self.thread_local.state_bucket
    
    def load_state(self):
        """Load state from GCS if it exists, otherwise initialize empty state"""
        try:
            state_bucket = self.get_state_bucket()
            blob = state_bucket.blob(self.state_file_path)
            
            if blob.exists():
                logger.info(f"📂 Loading existing state file from gs://{STATE_FILE_BUCKET}/{self.state_file_path}")
                state_data = blob.download_as_text()
                state = json.loads(state_data)
                
                self.processed_files = set(state.get('processed_files', []))
                self.stats = state.get('stats', self.stats)
                
                logger.info(f"✓ Loaded state: {len(self.processed_files)} files already processed")
            else:
                logger.info(f"📝 No existing state file found. Creating new state file on first save.")
                self.processed_files = set()
                
        except Exception as e:
            logger.warning(f"⚠️ Could not load state file: {e}. Starting fresh migration.")
            self.processed_files = set()
    
    def save_state(self):
        """Save current state to GCS"""
        try:
            state = {
                'processed_files': list(self.processed_files),
                'stats': self.stats,
                'last_updated': datetime.now(timezone.utc).isoformat()
            }
            
            state_bucket = self.get_state_bucket()
            blob = state_bucket.blob(self.state_file_path)
            blob.upload_from_string(
                json.dumps(state, indent=2),
                content_type='application/json'
            )
            
            logger.debug(f"💾 State saved: {len(self.processed_files)} files tracked")
            
        except Exception as e:
            logger.error(f"❌ Failed to save state: {e}")
    
    def is_file_processed(self, file_id):
        """Check if a file has already been processed"""
        return file_id in self.processed_files
    
    def mark_file_processed(self, file_id, force_save=False):
        """Mark a file as processed and save state in batches"""
        self.processed_files.add(file_id)
        
        # Only save state every N files or when forced
        if force_save or len(self.processed_files) % STATE_SAVE_BATCH_SIZE == 0:
            self.save_state()
    
    def is_zip_file(self, filename):
        """Check if file is a ZIP archive"""
        zip_extensions = ['.zip', '.ZIP', '.rar', '.7z', '.tar.gz', '.tar', '.gz']
        return any(filename.lower().endswith(ext) for ext in zip_extensions)
    
    @retry_on_rate_limit
    def download_zip_chunk(self, downloader):
        return downloader.next_chunk()

    def extract_and_upload_zip(self, file_info, folder_path):
        """Download ZIP, extract, and upload contents to GCS"""
        file_id = file_info['id']
        zip_name = file_info['name']
        zip_size = file_info['size']
        
        start_time = datetime.now(timezone.utc)
        
        # Check size limit
        zip_size_gb = zip_size / (1024 ** 3)
        if zip_size_gb > ZIP_CONFIG['max_zip_size_gb']:
            logger.warning(f"ZIP too large ({zip_size_gb:.2f}GB): {zip_name}. Uploading as-is.")
            return self.transfer_file(file_info, folder_path)
        
        tmp_zip_path = None
        try:
            logger.info(f"📦 Processing ZIP (Disk-based): {zip_name} ({zip_size_gb:.2f}GB)")
            
            # Use a temporary file on disk instead of RAM to prevent malloc errors
            with tempfile.NamedTemporaryFile(delete=False) as tmp_zip:
                tmp_zip_path = tmp_zip.name
                
                # Download ZIP from Drive
                request = self.get_drive_service().files().get_media(
                    fileId=file_id,
                    supportsAllDrives=True
                )
                downloader = MediaIoBaseDownload(tmp_zip, request, chunksize=CHUNK_SIZE)
                
                done = False
                while not done:
                    status, done = self.download_zip_chunk(downloader)
                    if status:
                        logger.info(f"  Download progress: {int(status.progress() * 100)}%")

            # Extract ZIP from disk
            extracted_files = []
            extracted_size = 0  # FIXED: Now properly tracked
            
            with zipfile.ZipFile(tmp_zip_path, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                logger.info(f"  Extracting {len(file_list)} files...")
                
                for zip_file_path in file_list:
                    if zip_file_path.endswith('/'):
                        continue
                    
                    # Stream file from ZIP directly to GCS (Prevents malloc memory crashes)
                    zip_folder = Path(zip_name).stem
                    gcs_path = f"{folder_path}/{zip_folder}/{zip_file_path}" if folder_path else f"{zip_folder}/{zip_file_path}"
                    
                    with zip_ref.open(zip_file_path) as extracted_file:
                        bucket = self.get_gcs_bucket()
                        blob = bucket.blob(gcs_path)
                        # upload_from_file streams the data without loading it all into RAM
                        blob.upload_from_file(extracted_file)
                        
                        blob.metadata = {
                            'source': 'google_drive_zip',
                            'original_zip': zip_name,
                            'extracted_at': datetime.now(timezone.utc).isoformat()
                        }
                        blob.patch()
                        extracted_files.append(gcs_path)
                        
                        # FIXED: Track extracted size
                        file_info_obj = zip_ref.getinfo(zip_file_path)
                        extracted_size += file_info_obj.file_size
                        
                        logger.info(f"    ✓ Extracted and Streamed: {zip_file_path}")

            # Optionally upload original ZIP
            if not ZIP_CONFIG['delete_original_zip']:
                zip_gcs_path = f"{folder_path}/{zip_name}" if folder_path else zip_name
                bucket = self.get_gcs_bucket()
                blob = bucket.blob(zip_gcs_path)
                blob.upload_from_filename(tmp_zip_path)
                logger.info(f"  ✓ Uploaded original ZIP: {zip_gcs_path}")
            
            # Cleanup temp file
            if tmp_zip_path and os.path.exists(tmp_zip_path):
                os.remove(tmp_zip_path)
            
            # Calculate duration
            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()
            
            logger.info(f"✅ ZIP extraction complete: {zip_name} ({len(extracted_files)} files, {extracted_size / (1024**2):.1f}MB, {duration:.1f}s)")
            
            self.stats['zips_extracted'] += 1
            self.stats['zip_files_extracted'] += len(extracted_files)
            self.stats['successful'] += 1
            
            return True
            
        except zipfile.BadZipFile:
            logger.error(f"❌ Corrupted ZIP: {zip_name}")
            # Upload original ZIP as fallback
            return self.transfer_file(file_info, folder_path)
            
        except Exception as e:
            logger.error(f"❌ ZIP extraction failed: {zip_name} - {str(e)}")
            # Cleanup temp file
            if tmp_zip_path and os.path.exists(tmp_zip_path):
                try:
                    os.remove(tmp_zip_path)
                except OSError as cleanup_error:
                    logger.debug(f"Failed to remove temp file: {cleanup_error}")
            
            # Upload original ZIP as fallback
            return self.transfer_file(file_info, folder_path)
    

    
    @retry_on_rate_limit
    def download_file_chunk(self, downloader):
        return downloader.next_chunk()

    def transfer_file(self, file_info, folder_path):
        """Transfer regular file from Drive to GCS using disk-based staging for stability"""
        file_id = file_info['id']
        file_name = file_info['name']
        gcs_path = f"{folder_path}/{file_name}" if folder_path else file_name
        tmp_file_path = None
        
        try:
            # Check if exists
            bucket = self.get_gcs_bucket()
            blob = bucket.blob(gcs_path)
            if blob.exists():
                logger.info(f"Skipping (exists): {gcs_path}")
                self.stats['skipped'] += 1
                return True
            
            # Download to disk (Much more stable in Cloud Shell)
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file_path = tmp_file.name
                request = self.get_drive_service().files().get_media(
                    fileId=file_id,
                    supportsAllDrives=True
                )
                downloader = MediaIoBaseDownload(tmp_file, request, chunksize=CHUNK_SIZE)
                
                done = False
                while not done:
                    status, done = self.download_file_chunk(downloader)

            # Upload from disk
            blob.upload_from_filename(tmp_file_path, content_type=file_info['mimeType'])
            
            blob.metadata = {
                'source': 'google_drive',
                'drive_file_id': file_id,
                'migrated_at': datetime.now(timezone.utc).isoformat()
            }
            blob.patch()
            
            logger.info(f"✓ Uploaded: {gcs_path}")
            self.stats['successful'] += 1
            return True
            
        except Exception as e:
            logger.error(f"✗ Failed: {gcs_path} - {str(e)}")
            self.stats['failed'] += 1
            return False
        finally:
            # FIXED: Replaced bare except with OSError
            if tmp_file_path and os.path.exists(tmp_file_path):
                try:
                    os.remove(tmp_file_path)
                except OSError as cleanup_error:
                    logger.debug(f"Failed to remove temp file: {cleanup_error}")
    
    @retry_on_rate_limit
    def process_file(self, file_info, folder_path=''):
        """Process file - extract if ZIP, otherwise upload"""
        file_id = file_info['id']
        file_name = file_info['name']
        
        # Check if already processed
        if self.is_file_processed(file_id):
            logger.info(f"⏭️  Skipping (already processed): {file_name}")
            self.stats['skipped'] += 1
            return True
        
        # Process the file
        result = False
        if ZIP_CONFIG['extract_zips'] and self.is_zip_file(file_name):
            result = self.extract_and_upload_zip(file_info, folder_path)
        else:
            result = self.transfer_file(file_info, folder_path)
        
        # Mark as processed if successful
        if result:
            self.mark_file_processed(file_id)
        
        return result
    
    @retry_on_rate_limit
    def list_files_page(self, query, page_token):
        return self.get_drive_service().files().list(
            q=query,
            spaces='drive',
            fields='nextPageToken, files(id, name, mimeType, size, parents)',
            pageToken=page_token,
            pageSize=1000,
            supportsAllDrives=True,
            includeItemsFromAllDrives=True
        ).execute()

    def list_files_recursive(self, folder_id, path=''):
        """Recursively list all files in Drive folder"""
        query = f"'{folder_id}' in parents and trashed=false"
        page_token = None
        files_list = []
        
        while True:
            try:
                response = self.list_files_page(query, page_token)
                
                for file in response.get('files', []):
                    file_path = f"{path}/{file['name']}" if path else file['name']
                    
                    if file['mimeType'] == 'application/vnd.google-apps.folder':
                        logger.info(f"📁 Scanning folder: {file_path}")
                        files_list.extend(self.list_files_recursive(file['id'], file_path))
                    else:
                        if not file['mimeType'].startswith('application/vnd.google-apps'):
                            files_list.append({
                                'id': file['id'],
                                'name': file['name'],
                                'path': path,
                                'size': int(file.get('size', 0)),
                                'mimeType': file['mimeType']
                            })
                
                page_token = response.get('nextPageToken')
                if not page_token:
                    break
                    
            except Exception as e:
                logger.error(f"Error listing files: {e}")
                break
        
        return files_list
    
    def migrate(self):
        """Main migration orchestrator with ZIP extraction"""
        start_time = datetime.now(timezone.utc)
        logger.info("=" * 80)
        logger.info("Starting Migration with ZIP Extraction")
        logger.info(f"ZIP Extraction: {'Enabled' if ZIP_CONFIG['extract_zips'] else 'Disabled'}")
        logger.info(f"Delete Original ZIPs: {'Yes' if ZIP_CONFIG['delete_original_zip'] else 'No'}")
        logger.info(f"State File: gs://{STATE_FILE_BUCKET}/{STATE_FILE_NAME}")
        logger.info(f"Previously Processed: {len(self.processed_files)} files")
        logger.info("=" * 80)
        
        # List files
        logger.info("Phase 1: Scanning Drive...")
        files = self.list_files_recursive(DRIVE_FOLDER_ID)
        self.stats['total_files'] = len(files)
        
        zip_files = [f for f in files if self.is_zip_file(f['name'])]
        regular_files = [f for f in files if not self.is_zip_file(f['name'])]
        
        logger.info(f"Found {len(files)} files:")
        logger.info(f"  - Regular files: {len(regular_files)}")
        logger.info(f"  - ZIP files: {len(zip_files)}")
        
        # Process files
        logger.info(f"Phase 2: Processing files...")
        
        # Filter out already-processed files to avoid unnecessary work
        files_to_process = [f for f in files if not self.is_file_processed(f['id'])]
        logger.info(f"Files remaining to process: {len(files_to_process)} (skipping {len(files) - len(files_to_process)} already processed)")
        
        if MAX_WORKERS > 1:
            futures = {}
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                for file in files_to_process:
                    futures[executor.submit(self.process_file, file, file['path'])] = file
                
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        logger.error(f"Unexpected error: {str(e)}")
        else:
            # Pure sequential processing for maximum stability in Cloud Shell
            for i, file in enumerate(files_to_process):
                try:
                    logger.info(f"[{i+1}/{len(files_to_process)}] Processing...")
                    self.process_file(file, file['path'])
                except Exception as e:
                    logger.error(f"Unexpected error on file {file['name']}: {str(e)}")
        
        # Final report
        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()
        
        # Save final state to ensure all files are tracked
        logger.info("Saving final state...")
        self.save_state()
        
        logger.info("=" * 80)
        logger.info("Migration Complete!")
        logger.info(f"Total Files: {self.stats['total_files']}")
        logger.info(f"Successful: {self.stats['successful']}")
        logger.info(f"Failed: {self.stats['failed']}")
        logger.info(f"Skipped: {self.stats['skipped']}")
        logger.info(f"ZIPs Extracted: {self.stats['zips_extracted']}")
        logger.info(f"Files from ZIPs: {self.stats['zip_files_extracted']}")
        logger.info(f"Duration: {duration / 3600:.2f} hours")
        logger.info("=" * 80)


if __name__ == "__main__":
    migrator = DriveToGCSWithZipExtraction()
    migrator.migrate()  # FIXED: Removed trailing period
