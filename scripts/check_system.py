"""
Quick System Check - Verify environment is ready for training
"""

import sys

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    print(f"✓ Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major != 3 or version.minor not in [9, 10, 11]:
        print("  ⚠️ Warning: Python 3.9-3.11 recommended")
        return False
    return True

def check_imports():
    """Check if required packages are installed"""
    
    packages = {
        "torch": "PyTorch",
        "torchaudio": "TorchAudio", 
        "TTS": "Coqui TTS",
        "librosa": "Librosa",
        "soundfile": "SoundFile",
        "noisereduce": "NoiseReduce",
        "numpy": "NumPy",
        "pandas": "Pandas",
    }
    
    all_ok = True
    
    for package, name in packages.items():
        try:
            mod = __import__(package)
            version = getattr(mod, "__version__", "unknown")
            print(f"✓ {name}: {version}")
        except ImportError:
            print(f"✗ {name}: NOT INSTALLED")
            all_ok = False
    
    return all_ok

def check_cuda():
    """Check CUDA availability"""
    
    try:
        import torch
        
        if torch.cuda.is_available():
            print(f"✓ CUDA available: {torch.version.cuda}")
            print(f"✓ GPU: {torch.cuda.get_device_name(0)}")
            print(f"✓ GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
            return True
        else:
            print("✗ CUDA not available")
            return False
            
    except ImportError:
        print("✗ PyTorch not installed")
        return False

def check_paths():
    """Check if required directories exist"""
    
    from pathlib import Path
    
    paths = {
        "source_clips": Path("f:/CODE/tts-2/source_clips"),
        "processed_clips": Path("f:/CODE/tts-2/processed_clips"),
        "dataset": Path("f:/CODE/tts-2/dataset"),
        "output": Path("f:/CODE/tts-2/output"),
        "scripts": Path("f:/CODE/tts-2/scripts"),
    }
    
    all_ok = True
    
    for name, path in paths.items():
        if path.exists():
            print(f"✓ {name}: {path}")
        else:
            print(f"✗ {name}: NOT FOUND - {path}")
            all_ok = False
    
    return all_ok

def main():
    print("=" * 60)
    print("István Vágó XTTS-v2 - System Check")
    print("=" * 60)
    print()
    
    print("1. Python Version")
    print("-" * 60)
    py_ok = check_python_version()
    print()
    
    print("2. Required Packages")
    print("-" * 60)
    pkg_ok = check_imports()
    print()
    
    print("3. CUDA/GPU")
    print("-" * 60)
    cuda_ok = check_cuda()
    print()
    
    print("4. Directory Structure")
    print("-" * 60)
    path_ok = check_paths()
    print()
    
    print("=" * 60)
    if py_ok and pkg_ok and cuda_ok and path_ok:
        print("✅ All checks passed! System is ready.")
    else:
        print("⚠️ Some checks failed. Please review above.")
    print("=" * 60)

if __name__ == "__main__":
    main()
