# Policy Gap Analysis Tool 🔒

**HACK IITK 2026 - Cybersecurity Hackathon**  
**Problem Statement 1: Local LLM Powered Policy Gap Analysis**

A Python-based cybersecurity tool that uses **local LLMs** (via Ollama) to analyze organizational security policies against industry standards like the CIS MS-ISAC NIST Cybersecurity Framework.

## 🎯 Features

- **100% Offline**: No cloud APIs required - runs entirely on your local machine
- **Gap Analysis**: Identifies missing provisions and weak areas in security policies
- **Automated Remediation**: Generates revised policy sections to fix identified gaps
- **PDF Support**: Extracts and analyzes text from PDF policy documents
- **Rich Terminal UI**: Beautiful, professional console output
- **Configurable**: Easy to switch between different Ollama models

## 🏗️ Architecture

```
PS1/
├── src/
│   ├── pdf_loader.py      # Module 1: PDF text extraction
│   └── llm_judge.py       # Module 2: LLM-powered gap analysis
├── data/
│   ├── input/             # Place your policy PDFs here
│   ├── reference/         # Place NIST framework PDFs here
│   └── output/            # Analysis results saved here
├── config.py              # Configuration settings
├── main.py                # Main orchestration script
└── requirements.txt       # Python dependencies
```

## 🚀 Quick Start

### Prerequisites

1. **Install Ollama**
   ```powershell
   # Download from: https://ollama.ai
   # Or use winget (Windows 11)
   winget install Ollama.Ollama
   ```

2. **Pull an LLM Model**
   ```powershell
   ollama pull llama3
   # OR
   ollama pull mistral
   ```

3. **Start Ollama Server**
   ```powershell
   ollama serve
   ```

### Installation

1. **Clone/Navigate to Project**
   ```powershell
   cd "f:\04 All_Projects\Hackathons\06 IITK Hackathon\PS1"
   ```

2. **Create Virtual Environment**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate
   ```

3. **Install Dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

### Usage

#### Interactive Mode (Recommended)
```powershell
python main.py
```
Follow the prompts to:
1. Load your organization's policy (PDF)
2. Load the reference framework (PDF)
3. Run gap analysis
4. Generate remediation plan

#### Batch Mode
```powershell
python main.py --batch --user-policy "data/input/user_policy.pdf" --reference "data/reference/nist_framework.pdf"
```

#### Using Different Models
```powershell
python main.py --model mistral
```

## 📝 Example Workflow

1. **Prepare Your Documents**
   - Place your organization's security policy in `data/input/user_policy.pdf`
   - Place NIST framework PDF in `data/reference/nist_framework.pdf`

2. **Run Analysis**
   ```powershell
   python main.py
   ```

3. **Review Results**
   - Gap analysis saved to `data/output/gap_analysis_TIMESTAMP.md`
   - Remediation plan saved to `data/output/remediation_TIMESTAMP.md`

## 🧪 Testing Individual Modules

### Test PDF Loader
```powershell
python src/pdf_loader.py data/input/user_policy.pdf
```

### Test LLM Judge
```powershell
python src/llm_judge.py
```
*Note: Requires Ollama to be running*

## ⚙️ Configuration

Edit `config.py` to customize:

```python
# Change the LLM model
OLLAMA_MODEL = "mistral"  # or "llama3", "codellama", etc.

# Adjust LLM parameters
LLM_TEMPERATURE = 0.1  # Lower = more deterministic
LLM_MAX_TOKENS = 4096
LLM_TIMEOUT = 300  # seconds

# Ollama connection
OLLAMA_BASE_URL = "http://localhost:11434"
```

## 📦 Dependencies

- **langchain**: LLM orchestration framework
- **ollama**: Python client for Ollama
- **pymupdf**: Fast PDF text extraction
- **rich**: Beautiful terminal formatting
- **pydantic**: Data validation

## 🎓 How It Works

### Gap Analysis Prompt Engineering
The tool uses sophisticated prompts to guide the LLM:

```python
"""You are an expert cybersecurity policy analyst...

Compare organization's policy against reference framework:
1. Identify MISSING PROVISIONS
2. Find WEAK/INCOMPLETE AREAS  
3. List COMPLIANCE GAPS
4. Assess RISK LEVELS
5. Prioritize TOP 5 CRITICAL GAPS
"""
```

### Remediation Generation
After gap analysis, the tool generates:
- Executive summary
- Specific recommendations with priorities
- Draft policy text (ready to copy-paste)
- Implementation roadmap
- Compliance validation checkpoints

## 🔧 Troubleshooting

**Error: "Could not connect to Ollama"**
```powershell
# Make sure Ollama is running
ollama serve

# Verify it's working
ollama list
```

**Error: "Model not found"**
```powershell
# Pull the model first
ollama pull llama3
```

**PDF extraction failed**
- Ensure PDF is not password-protected
- Check file path is correct
- Verify file is a valid PDF

## 🏆 Hackathon Compliance

✅ **100% Offline** - No cloud APIs  
✅ **Local LLM** - Uses Ollama  
✅ **Gap Analysis** - Task 1 implemented  
✅ **Remediation** - Task 2 implemented  
✅ **PDF Support** - Handles policy documents  
✅ **NIST Framework** - Reference standard integration

## 📄 License

MIT License - Built for HACK IITK 2026

## 👨‍💻 Development

Built with:
- Python 3.10+
- Ollama (local LLM runtime)
- LangChain (LLM orchestration)
- Rich (terminal UI)

---

**Built for HACK IITK 2026 Cybersecurity Hackathon**  
*Empowering organizations to strengthen their security posture with AI*
