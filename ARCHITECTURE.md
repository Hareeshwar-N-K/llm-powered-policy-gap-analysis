# Project Architecture & Technical Documentation

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interaction Layer                    │
│                        (main.py)                             │
│  • Interactive CLI with Rich UI                             │
│  • Batch processing mode                                    │
│  • Command-line argument parsing                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Document Processing Layer                  │
│                   (src/pdf_loader.py)                       │
│  • PDF text extraction (PyMuPDF/fitz)                       │
│  • Text cleaning and normalization                          │
│  • Metadata extraction                                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    AI Analysis Layer                         │
│                   (src/llm_judge.py)                        │
│  • Local LLM integration via Ollama                         │
│  • Prompt engineering for gap analysis                      │
│  • Remediation generation                                   │
│  • LangChain orchestration                                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Local LLM Runtime (Ollama)                  │
│  • Llama 3 / Mistral / Other models                         │
│  • Runs on localhost:11434                                  │
│  • 100% offline inference                                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Output Layer                            │
│  • Markdown formatted reports                               │
│  • Timestamped file generation                              │
│  • Saved to data/output/                                    │
└─────────────────────────────────────────────────────────────┘
```

## Component Breakdown

### 1. PDF Loader (`src/pdf_loader.py`)

**Purpose**: Extract text content from policy PDF documents

**Key Features**:
- Uses PyMuPDF (fitz) for fast, reliable PDF parsing
- Cleans extracted text (removes artifacts, normalizes whitespace)
- Provides metadata extraction (page count, author, title)
- Progress indicators using Rich library
- Standalone testing capability

**Class: `PDFLoader`**
```python
Methods:
  - extract_text(pdf_path) → str
  - extract_with_metadata(pdf_path) → dict
  - _clean_text(text) → str  # Internal
```

**Usage Example**:
```python
loader = PDFLoader(verbose=True)
text = loader.extract_text("policy.pdf")
```

### 2. LLM Judge (`src/llm_judge.py`)

**Purpose**: AI-powered policy analysis using local LLMs

**Key Features**:
- Connects to local Ollama instance
- Implements sophisticated prompt engineering
- Two-phase analysis: Gap Detection → Remediation
- Uses LangChain for LLM orchestration
- Configurable temperature and timeout

**Class: `PolicyJudge`**
```python
Methods:
  - analyze_gaps(user_policy, reference_standard) → dict
  - generate_remediation(user_policy, gap_analysis) → dict
  - _create_gap_analysis_prompt() → str  # Internal
  - _create_remediation_prompt() → str   # Internal
```

**Prompt Engineering Strategy**:

**Gap Analysis Prompt**:
- Instructs LLM to act as cybersecurity policy expert
- Defines clear output structure: Missing Provisions, Weak Areas, Compliance Gaps
- Requests risk severity ratings (Critical/High/Medium/Low)
- Asks for prioritized top 5 critical gaps

**Remediation Prompt**:
- Generates executive summary
- Provides specific, actionable recommendations
- Drafts actual policy text ready for insertion
- Creates implementation roadmap
- Defines compliance validation checkpoints

### 3. Main Orchestrator (`main.py`)

**Purpose**: Coordinates the complete workflow

**Key Features**:
- Interactive mode with prompts
- Batch mode for automation
- Results persistence (Markdown output)
- Command-line argument parsing
- Beautiful terminal UI

**Class: `PolicyAnalysisPipeline`**
```python
Methods:
  - run_interactive()  # Step-by-step user interaction
  - run_batch(user_policy_path, reference_path)  # Automated
  - _save_results(result, result_type)
  - _print_summary()
```

**Workflow**:
1. Load user policy (PDF → text)
2. Load reference standard (PDF → text)
3. Initialize LLM connection
4. Run gap analysis
5. Generate remediation
6. Save results with timestamps

### 4. Configuration (`config.py`)

**Purpose**: Centralized settings management

**Key Settings**:
```python
# Paths
PROJECT_ROOT, DATA_DIR, INPUT_DIR, OUTPUT_DIR, REFERENCE_DIR

# Ollama
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3"

# LLM Parameters
LLM_TEMPERATURE = 0.1  # Low for factual analysis
LLM_MAX_TOKENS = 4096
LLM_TIMEOUT = 300  # 5 minutes

# Reference
REFERENCE_FRAMEWORK = "CIS MS-ISAC NIST Cybersecurity Framework"
```

## Data Flow

```
[User Policy PDF] ──┐
                    ├──► [PDF Loader] ──► [Text Extract]
[NIST Framework] ───┘                           │
                                                ▼
                                    [PolicyJudge.__init__]
                                         Connect to Ollama
                                                │
                    ┌───────────────────────────┴──────────────────┐
                    ▼                                              ▼
         [analyze_gaps()]                            [generate_remediation()]
    Prompt: Gap Analysis                         Prompt: Remediation Plan
                    │                                              │
                    ▼                                              ▼
         [Ollama LLM Inference]                     [Ollama LLM Inference]
         Model: llama3/mistral                      Model: llama3/mistral
                    │                                              │
                    ▼                                              ▼
         [Gap Analysis Report]                      [Remediation Report]
                    │                                              │
                    └───────────────────┬──────────────────────────┘
                                        ▼
                            [Save to data/output/]
                        gap_analysis_TIMESTAMP.md
                        remediation_TIMESTAMP.md
```

## Dependency Graph

```
main.py
  ├── src.pdf_loader.PDFLoader
  │     └── fitz (PyMuPDF)
  │           └── rich (Progress UI)
  │
  ├── src.llm_judge.PolicyJudge
  │     ├── langchain_community.llms.Ollama
  │     ├── langchain.prompts.PromptTemplate
  │     ├── langchain.chains.LLMChain
  │     └── rich (Console, Panel, Progress)
  │
  └── config
        └── pathlib, os
```

## Prompt Engineering Deep Dive

### Gap Analysis Prompt Template

```
System Role: "You are an expert cybersecurity policy analyst"

Context: 
  - Reference Framework: {NIST CSF text}
  - User Policy: {Extracted policy text}

Task Instructions:
  1. Identify MISSING PROVISIONS
  2. Identify WEAK/INCOMPLETE AREAS
  3. List COMPLIANCE GAPS
  4. Assess RISK LEVELS (Critical/High/Medium/Low)
  5. Prioritize TOP 5 CRITICAL GAPS

Output Format: Structured markdown with clear headings
```

**Temperature: 0.1** (Very low for consistent, factual analysis)

### Remediation Prompt Template

```
System Role: "You are an expert cybersecurity policy writer"

Context:
  - Original Policy: {User policy}
  - Gap Analysis: {Previous analysis results}

Task Instructions:
  1. Executive Summary (2-3 paragraphs)
  2. Specific Recommendations (with priorities)
  3. REVISED POLICY SECTIONS (ready to copy-paste)
  4. Implementation Roadmap (phased approach)
  5. Compliance Validation Checkpoints

Output Format: Professional policy language
```

**Temperature: 0.1** (Consistent professional tone)

## Security & Privacy Considerations

✅ **100% Offline**: No data leaves your machine  
✅ **No Cloud APIs**: All processing local  
✅ **Data Sovereignty**: Your policies stay private  
✅ **Reproducible**: Same input → same output (low temperature)  
✅ **Auditable**: All prompts visible in source code  

## Performance Characteristics

### PDF Processing
- **Speed**: ~500 pages/second (PyMuPDF)
- **Memory**: ~50MB for 1000-page document
- **Formats**: Standard PDF, scanned PDFs with OCR

### LLM Inference
- **Speed**: 10-50 tokens/second (depends on hardware)
- **Memory**: 4-8GB RAM for llama3 (8B model)
- **Latency**: 
  - Gap Analysis: 1-3 minutes
  - Remediation: 2-5 minutes

### Total Workflow Time
- Small policy (10 pages): ~3-5 minutes
- Medium policy (50 pages): ~5-10 minutes
- Large policy (200+ pages): ~10-20 minutes

*Times assume local machine with 16GB RAM, modern CPU*

## Extension Points

### Adding New Models
```python
# In config.py
OLLAMA_MODEL = "mistral"  # or "codellama", "llama2", etc.
```

### Custom Prompts
Edit `src/llm_judge.py`:
- `_create_gap_analysis_prompt()` - Modify gap analysis logic
- `_create_remediation_prompt()` - Modify remediation style

### Output Formats
Currently: Markdown  
Future: JSON, PDF, HTML (extend `_save_results()`)

### Additional Analysis Types
Extend `PolicyJudge` class:
- Add `assess_compliance_score()` method
- Add `generate_executive_summary()` method
- Add `compare_multiple_frameworks()` method

## Testing Strategy

### Unit Tests (Future)
```python
tests/
  ├── test_pdf_loader.py
  ├── test_llm_judge.py
  └── test_integration.py
```

### Manual Testing
```powershell
# Test PDF loader
python src/pdf_loader.py data/input/test_policy.pdf

# Test LLM connection
python src/llm_judge.py

# Test full pipeline
python main.py --batch --user-policy test.pdf --reference nist.pdf
```

## Troubleshooting Guide

### Issue: "Connection refused to Ollama"
**Cause**: Ollama server not running  
**Fix**: Run `ollama serve` in separate terminal

### Issue: "Model not found"
**Cause**: Model not downloaded  
**Fix**: Run `ollama pull llama3`

### Issue: "Out of memory"
**Cause**: LLM model too large for RAM  
**Fix**: Use smaller model like `ollama pull llama3.2` or increase swap

### Issue: "PDF extraction returns empty text"
**Cause**: PDF is image-based (scanned) without OCR  
**Fix**: Run OCR preprocessing or use text-based PDF

### Issue: "Analysis takes too long"
**Cause**: Large policy documents  
**Fix**: 
1. Reduce `LLM_MAX_TOKENS` in config
2. Split policy into sections
3. Use faster model (mistral vs llama3)

## Development Roadmap

### Phase 1: Core Functionality ✅
- PDF extraction
- LLM integration
- Gap analysis
- Remediation generation

### Phase 2: Enhancements (Future)
- Multi-framework support (ISO 27001, PCI-DSS, etc.)
- Compliance scoring metrics
- Interactive web UI (Streamlit/Gradio)
- Batch processing for multiple policies

### Phase 3: Advanced Features (Future)
- Policy version comparison
- Automated policy generator from scratch
- Integration with GRC tools
- Real-time collaborative editing

---

**Built for HACK IITK 2026**  
*Enterprise-grade architecture, hackathon delivery speed* 🚀
