# István Vágó XTTS-v2 Environment Setup Script
# Windows PowerShell script for setting up the training environment

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "István Vágó Voice Cloning - Environment Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "[1/8] Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
Write-Host "Found: $pythonVersion" -ForegroundColor Green

if (-not ($pythonVersion -match "Python 3\.(9|10|11)")) {
    Write-Host "ERROR: Python 3.9, 3.10, or 3.11 required!" -ForegroundColor Red
    exit 1
}

# Check CUDA
Write-Host "[2/8] Checking CUDA availability..." -ForegroundColor Yellow
try {
    $nvidiaSmi = nvidia-smi 2>&1
    Write-Host "NVIDIA GPU detected" -ForegroundColor Green
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
} catch {
    Write-Host "WARNING: NVIDIA GPU not detected. Training will be very slow!" -ForegroundColor Red
}

# Create virtual environment
Write-Host "[3/8] Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "xtts_env") {
    Write-Host "Virtual environment already exists. Skipping..." -ForegroundColor Yellow
} else {
    python -m venv xtts_env
    Write-Host "Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "[4/8] Activating virtual environment..." -ForegroundColor Yellow
& .\xtts_env\Scripts\Activate.ps1

# Upgrade pip
Write-Host "[5/8] Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install PyTorch with CUDA support first
Write-Host "[6/8] Installing PyTorch with CUDA 11.8 support..." -ForegroundColor Yellow
pip install torch==2.1.0+cu118 torchaudio==2.1.0+cu118 --extra-index-url https://download.pytorch.org/whl/cu118

# Install other requirements
Write-Host "[7/8] Installing remaining dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Verify installation
Write-Host "[8/8] Verifying installation..." -ForegroundColor Yellow
python -c "import torch; print(f'PyTorch version: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA version: {torch.version.cuda}'); print(f'GPU count: {torch.cuda.device_count()}'); print(f'GPU name: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Prepare your dataset: python scripts\prepare_dataset.py" -ForegroundColor White
Write-Host "2. Start training: python scripts\train_xtts.py" -ForegroundColor White
Write-Host ""
Write-Host "To activate environment in future sessions:" -ForegroundColor Yellow
Write-Host "  .\xtts_env\Scripts\Activate.ps1" -ForegroundColor White
