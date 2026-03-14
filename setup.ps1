
# MediaCompressorPro - Automatic Environment Setup
# Run in PowerShell from the project root:
#    .\setup.ps1

Write-Host ""
Write-Host "MediaCompressorPro environment setup starting..." -ForegroundColor Cyan
Write-Host ""

# Check Python
try {
    $pythonVersion = python --version
    Write-Host "Python detected: $pythonVersion"
} catch {
    Write-Host "Python not found. Install Python 3.10+ and try again." -ForegroundColor Red
    exit 1
}

# Create venv if it doesn't exist
if (!(Test-Path ".venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
} else {
    Write-Host "Virtual environment already exists."
}

# Activate venv
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
. .\.venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install dependencies
if (Test-Path "requirements.txt") {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
} else {
    Write-Host "requirements.txt not found. Skipping dependency installation." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Setup completed successfully." -ForegroundColor Green
Write-Host ""
Write-Host "To run the application:"
Write-Host "    cd src"
Write-Host "    python -m app"
Write-Host ""
