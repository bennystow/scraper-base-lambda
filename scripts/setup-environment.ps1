<#
.SYNOPSIS
    Sets up the Python development environment for the project on Windows.
.DESCRIPTION
    This script performs the following actions:
    1. Checks for and removes any existing '.venv' virtual environment directory.
    2. Creates a new Python virtual environment using the specified Python version via the 'py.exe' launcher.
    3. Installs all required project dependencies, including test and linting tools, from 'pyproject.toml'.
    4. Provides the command to activate the environment upon completion.
    It is designed to be idempotent, ensuring a clean and consistent setup every time it is run.
    Requires the Python Launcher for Windows ('py.exe') to be installed and in the system's PATH.
#>

# Stop script execution on any error
$ErrorActionPreference = "Stop"

# --- Configuration ---
$VenvDir = ".venv"
$PythonVersion = "3.12"

# 1. Delete environment if it exists in .venv folder
if (Test-Path -Path $VenvDir -PathType Container) {
    Write-Host "Found existing virtual environment. Removing..."
    Remove-Item -Path $VenvDir -Recurse -Force
}

# 2. Create python environment
Write-Host "Creating Python $PythonVersion virtual environment..."
# Use the py.exe launcher, which is standard on Windows for managing multiple Python versions.
py "-$PythonVersion" -m venv $VenvDir

# 3. Install dependencies from pyproject.toml
Write-Host "Installing project dependencies..."
$PipExecutable = Join-Path -Path $VenvDir -ChildPath "Scripts\pip.exe"
& $PipExecutable install -e ".[test,lint]"

Write-Host ""
Write-Host "Environment setup complete!" -ForegroundColor Green
Write-Host "To activate the virtual environment, run: .\$VenvDir\Scripts\Activate.ps1"
