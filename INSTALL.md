# Installation & Setup Guide

## Quick Install (Recommended)

### Option 1: Automated Setup (Windows)

```powershell
# Navigate to project
cd "F:\04 All_Projects\Hackathons\06 IITK Hackathon\PS1"

# Run automated setup
.\setup.bat
```

This will:
- ✅ Check Python installation
- ✅ Create virtual environment
- ✅ Install all dependencies
- ✅ Check for Ollama

---

### Option 2: Manual Setup

#### Step 1: Install Ollama

**Windows:**
```powershell
# Method 1: Windows Package Manager
winget install Ollama.Ollama

# Method 2: Manual Download
# Download from https://ollama.ai/download
```

**Verify Installation:**
```powershell
ollama --version
# Should show: ollama version is 0.15.5 (or higher)
```

#### Step 2: Pull AI Model

```powershell
# Recommended for hackathon (fast, 2GB)
ollama pull llama3.2:3b

# OR: Better quality, slower (4.7GB)
ollama pull llama3.1:8b

# OR: Alternative
ollama pull mistral:7b
```

**Verify Model:**
```powershell
ollama list
# Should show your downloaded model
```

#### Step 3: Start Ollama Server

```powershell
# Start in background (keeps running)
ollama serve

# You should see:
# "Ollama is running"
```

**Note:** Keep this terminal open! Ollama must be running for the tool to work.

#### Step 4: Setup Python Environment

```powershell
# Navigate to project
cd "F:\04 All_Projects\Hackathons\06 IITK Hackathon\PS1"

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# You should see (venv) in your prompt
```

#### Step 5: Install Python Dependencies

```powershell
# Upgrade pip first
pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt
```

**Expected packages:**
- langchain & langchain-community (LLM framework)
- ollama (Python client)
- pymupdf (PDF processing)
- rich (terminal UI)
- pydantic (data validation)

---

## Troubleshooting Installation

### Issue: "Python is not recognized"

**Solution:**
```powershell
# Download Python 3.10+ from python.org
# During installation, CHECK "Add Python to PATH"

# Verify:
python --version
# Should show: Python 3.x.x
```

### Issue: "ollama is not recognized"

**Solution 1:** Restart your terminal after installing Ollama

**Solution 2:** Manual PATH add
```powershell
# Find Ollama installation (usually):
# C:\Users\YourName\AppData\Local\Programs\Ollama

# Add to PATH via System Environment Variables
```

### Issue: "ModuleNotFoundError: No module named 'fitz'"

**Cause:** Virtual environment not activated OR dependencies not installed

**Solution:**
```powershell
# Make sure venv is active (you should see (venv) in prompt)
.\venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "Connection refused" when running tool

**Cause:** Ollama server not running

**Solution:**
```powershell
# In a SEPARATE terminal window:
ollama serve

# Then run your tool in the original window
```

### Issue: "Model not found"

**Cause:** Model not downloaded

**Solution:**
```powershell
ollama pull llama3.2:3b
```

### Issue: "Out of memory" during analysis

**Solutions:**
1. Use smaller model:
   ```powershell
   ollama pull llama3.2:1b
   ```
2. Edit `config.py`:
   ```python
   OLLAMA_MODEL = "llama3.2:1b"
   LLM_MAX_TOKENS = 2048  # Reduce from 4096
   ```
3. Close other applications to free RAM

### Issue: "PDF extraction failed"

**Possible causes:**
- File doesn't exist at specified path
- PDF is password-protected
- PDF is corrupted

**Solution:**
```powershell
# Test with sample file first
python src/document_loader.py data/reference/SAMPLE_NIST_REFERENCE.md

# If that works, check your PDF path
```

---

## Verifying Installation

### Test 1: Python Setup
```powershell
python --version
# Expected: Python 3.10 or higher
```

### Test 2: Virtual Environment
```powershell
# Should show (venv) in prompt:
(venv) PS F:\...\PS1>
```

### Test 3: Dependencies
```powershell
pip list
# Should include: langchain, ollama, pymupdf, rich, pydantic
```

### Test 4: Ollama
```powershell
ollama list
# Should show at least one model (llama3.2:3b, etc.)

ollama ps
# Shows running models (may be empty, that's OK)
```

### Test 5: Document Loader
```powershell
python src/document_loader.py data/reference/SAMPLE_NIST_REFERENCE.md
# Should extract and display text
```

### Test 6: LLM Connection
```powershell
python src/llm_judge.py
# Should connect to Ollama and run sample analysis
```

### Test 7: Full Tool
```powershell
python main.py
# Should start interactive mode without errors
```

---

## Installation Checklist

Before running the tool, verify:

- [ ] Python 3.10+ installed and in PATH
- [ ] Virtual environment created and activated
- [ ] All Python packages installed (`pip list` shows them)
- [ ] Ollama installed (`ollama --version` works)
- [ ] At least one model downloaded (`ollama list` shows it)
- [ ] Ollama server running (`ollama serve` in separate terminal)
- [ ] Test files in `data/` directory
- [ ] No import errors when running `python main.py`

---

## Post-Installation Setup

### Prepare Your Documents

1. **Place your organization's policy:**
   ```
   data/input/your_policy.pdf
   # OR
   data/input/your_policy.txt
   # OR
   data/input/your_policy.md
   ```

2. **Reference framework is included:**
   ```
   data/reference/SAMPLE_NIST_REFERENCE.md
   ```

### Configure Model (Optional)

Edit `config.py` if you want to use a different model:

```python
# Change this line:
OLLAMA_MODEL = "llama3.2:3b"

# To one of:
OLLAMA_MODEL = "llama3.1:8b"  # Better quality, slower
OLLAMA_MODEL = "mistral:7b"   # Alternative
OLLAMA_MODEL = "gemma3:4b"    # If you already have it
```

---

## Running the Tool

### Interactive Mode (Recommended)
```powershell
python main.py
```

Follow the prompts:
1. Enter your policy file path (or press Enter for default)
2. Enter reference framework path (or press Enter for default)
3. Confirm gap analysis
4. Confirm remediation
5. Confirm export

### Batch Mode
```powershell
python main.py --batch \
  --user-policy "data/input/policy.pdf" \
  --reference "data/reference/SAMPLE_NIST_REFERENCE.md"
```

### Custom Model
```powershell
python main.py --model mistral:7b
```

---

## Uninstallation

### Remove Python Packages
```powershell
# Deactivate virtual environment
deactivate

# Delete virtual environment folder
Remove-Item -Recurse -Force venv
```

### Remove Ollama
```powershell
# Windows uninstall
winget uninstall Ollama.Ollama

# OR use Windows Settings > Apps > Ollama
```

### Remove Models
```powershell
# List models
ollama list

# Remove specific model
ollama rm llama3.2:3b
ollama rm mistral:7b
```

---

## System Requirements

### Minimum:
- **OS:** Windows 10/11
- **RAM:** 8GB
- **Storage:** 10GB free
- **Python:** 3.10+
- **Internet:** For initial download only

### Recommended:
- **OS:** Windows 11
- **RAM:** 16GB
- **Storage:** 20GB free (for multiple models)
- **Python:** 3.11+
- **GPU:** NVIDIA GPU (optional, for faster inference)

---

## Getting Help

### Documentation
- [README.md](README.md) - Complete guide
- [QUICKSTART.md](QUICKSTART.md) - 5-minute setup
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical details
- [TESTING_CHECKLIST.md](TESTING_CHECKLIST.md) - Testing guide
- [CHANGELOG.md](CHANGELOG.md) - What's new

### Common Commands Reference
```powershell
# Activate environment
.\venv\Scripts\activate

# Deactivate environment
deactivate

# Check Ollama status
ollama ps

# List models
ollama list

# Pull model
ollama pull llama3.2:3b

# Start Ollama
ollama serve

# Run tool
python main.py

# Test module
python src/document_loader.py <file>
```

---

**Installation complete! You're ready to analyze policies! 🚀**
