# Quick Start Guide

## Setup (5 minutes)

### 1. Install Ollama
```powershell
# Download from https://ollama.ai
# Or use winget
winget install Ollama.Ollama
```

### 2. Pull a Model
```powershell
ollama pull llama3
```

### 3. Start Ollama
```powershell
ollama serve
```

### 4. Install Python Dependencies
```powershell
# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate

# Install packages
pip install -r requirements.txt
```

## Running the Tool

### Interactive Mode (Easiest)
```powershell
python main.py
```
Then follow the prompts!

### Batch Mode
```powershell
python main.py --batch \
  --user-policy "data/input/user_policy.pdf" \
  --reference "data/reference/nist_framework.pdf"
```

## Testing Individual Components

### Test PDF Extraction
```powershell
python src/pdf_loader.py data/input/user_policy.pdf
```

### Test LLM Connection
```powershell
python src/llm_judge.py
```

## Common Issues

**"Cannot connect to Ollama"**
→ Run `ollama serve` in a separate terminal

**"Model not found"**
→ Run `ollama pull llama3`

**"PDF extraction failed"**
→ Check PDF path and ensure it's not password-protected

## Next Steps

1. Place your policy PDF in `data/input/`
2. Place NIST framework PDF in `data/reference/`
3. Run `python main.py`
4. Check results in `data/output/`

Happy hacking! 🚀
