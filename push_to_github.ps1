# Push to GitHub Script
# This script will help you push the Code Quality Analyzer to GitHub

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Push Code Quality Analyzer to GitHub" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check current directory
$currentDir = Get-Location
Write-Host "Current directory: $currentDir" -ForegroundColor Yellow

# Check git status
Write-Host ""
Write-Host "Checking git status..." -ForegroundColor Yellow
git status

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Ready to push to GitHub!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Repository: https://github.com/icharshal/Code_Quality_Analyzer.git" -ForegroundColor Yellow
Write-Host ""
Write-Host "To push, you have 3 options:" -ForegroundColor Yellow
Write-Host ""
Write-Host "Option 1: Use GitHub Desktop (Easiest)" -ForegroundColor Green
Write-Host "  - Open GitHub Desktop"
Write-Host "  - Add this repository"
Write-Host "  - Click 'Push origin'"
Write-Host ""
Write-Host "Option 2: Use Personal Access Token" -ForegroundColor Green
Write-Host "  1. Go to: https://github.com/settings/tokens"
Write-Host "  2. Generate new token (classic)"
Write-Host "  3. Select 'repo' scope"
Write-Host "  4. Copy the token"
Write-Host "  5. Run: git push https://YOUR_TOKEN@github.com/icharshal/Code_Quality_Analyzer.git main"
Write-Host ""
Write-Host "Option 3: Configure Git Credential Manager" -ForegroundColor Green
Write-Host "  Run: git push origin main"
Write-Host "  A browser window will open for authentication"
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Ask user which option they want
Write-Host "Which option would you like to use? (1/2/3): " -NoNewline -ForegroundColor Yellow
$choice = Read-Host

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Opening GitHub Desktop..." -ForegroundColor Green
        Write-Host "Please add this repository and push from there." -ForegroundColor Yellow
        Start-Process "github://openRepo/$(Get-Location)"
    }
    "2" {
        Write-Host ""
        Write-Host "Please enter your Personal Access Token: " -NoNewline -ForegroundColor Yellow
        $token = Read-Host -AsSecureString
        $tokenPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($token))
        
        Write-Host ""
        Write-Host "Pushing to GitHub..." -ForegroundColor Green
        git push "https://$tokenPlain@github.com/icharshal/Code_Quality_Analyzer.git" main
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "✅ Successfully pushed to GitHub!" -ForegroundColor Green
            Write-Host "View at: https://github.com/icharshal/Code_Quality_Analyzer" -ForegroundColor Cyan
        }
        else {
            Write-Host ""
            Write-Host "❌ Push failed. Please check your token and try again." -ForegroundColor Red
        }
    }
    "3" {
        Write-Host ""
        Write-Host "Attempting to push..." -ForegroundColor Green
        Write-Host "A browser window may open for authentication." -ForegroundColor Yellow
        Write-Host ""
        git push origin main
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "✅ Successfully pushed to GitHub!" -ForegroundColor Green
            Write-Host "View at: https://github.com/icharshal/Code_Quality_Analyzer" -ForegroundColor Cyan
        }
        else {
            Write-Host ""
            Write-Host "❌ Push failed. Please try Option 1 or 2." -ForegroundColor Red
        }
    }
    default {
        Write-Host ""
        Write-Host "Invalid option. Please run the script again and choose 1, 2, or 3." -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
