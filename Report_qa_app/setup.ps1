<#
setup.ps1 - Project setup helper for CEERISK Report QA

Usage (run from repo root):

# Interactive (creates venv, installs deps, downloads spaCy model):
#   .\setup.ps1

# Train subjectivity model after deps are installed:
#   .\setup.ps1 -TrainModel
#   .\setup.ps1 -TrainModel -CsvPath "path\to\labels.csv"

This script is safe to re-run (idempotent) and will:
- Create a virtual environment at .\.venv if missing
- Activate the venv for the script session
- Upgrade pip and install packages from requirements.txt
- Download spaCy `en_core_web_sm`
- Optionally train the subjectivity model (built-in examples or CSV)

#>
Param(
    [switch]$TrainModel,
    [string]$CsvPath = ""
)

try {
    $ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
    Set-Location $ScriptDir
} catch {
    Write-Error "Unable to determine script directory. Run this script from the repository root."
    exit 1
}

Write-Host "Setting execution policy for this process..."
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python not found in PATH. Please install Python 3.10+ and re-run this script."
    exit 1
}

if (-Not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment .venv..."
    python -m venv .venv
} else {
    Write-Host ".venv already exists."
}

Write-Host "Activating virtual environment for this session..."
. .\.venv\Scripts\Activate.ps1

Write-Host "Upgrading pip and installing dependencies from requirements.txt..."
python -m pip install --upgrade pip
if (Test-Path "requirements.txt") {
    pip install -r requirements.txt
} else {
    Write-Warning "requirements.txt not found in repository root. Skipping dependency install."
}

Write-Host "Note: spaCy-based grammar checks were removed from the pipeline; skipping spaCy download."

if ($TrainModel) {
    if ($CsvPath -ne "") {
        Write-Host "Training subjectivity model from CSV: $CsvPath"
        python train_subjectivity_model.py --csv "$CsvPath"
    } else {
        Write-Host "Training subjectivity model using built-in examples..."
        python train_subjectivity_model.py
    }
}

Write-Host "Setup finished."
Write-Host "To activate the virtual environment in your interactive session run:" -ForegroundColor Cyan
Write-Host "    . .\.venv\Scripts\Activate.ps1" -ForegroundColor Yellow
Write-Host "Then start the app with:" -ForegroundColor Cyan
Write-Host "    streamlit run app.py" -ForegroundColor Yellow
