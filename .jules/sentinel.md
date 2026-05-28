
## 2026-05-20 - [Network Timeout Implementation]
**Learning:** External network calls via `urllib.request.urlopen` without a timeout can lead to indefinite hanging of the application, potentially causing denial-of-service scenarios or resource exhaustion.
**Action:** Implemented a standard 30-second timeout for all `urllib.request.urlopen` calls in `analyzer.py` to ensure the tool remains responsive and handles network issues gracefully.

## 2026-05-27 - [Isolated Test Execution]
**Learning:** Dynamically executing user-provided Python modules using `importlib` or `exec()` in the same process as the main application creates a critical security vulnerability. It allows arbitrary code execution and access to the application's memory, state, and secrets (like API keys).
**Action:** Replaced in-process `exec_module` with `subprocess.run` to execute test files in an isolated process. Used `python -m unittest` to ensure compatibility and `coverage json` for secure data extraction.
