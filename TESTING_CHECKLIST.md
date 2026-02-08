# Testing Checklist for HACK IITK 2026

## Pre-Testing Setup

- [ ] Python 3.10+ installed
- [ ] Ollama installed and running (`ollama serve`)
- [ ] Model downloaded (`ollama pull llama3`)
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)

## Component Testing

### 1. Test PDF Loader
```powershell
# Create a test PDF first or use any existing PDF
python src/pdf_loader.py data/input/test.pdf
```

**Expected Output**:
- ✓ Green success message
- Display of page count, word count, character count
- First 500 characters of extracted text

**Pass Criteria**:
- No errors
- Text extracted successfully
- Metadata displayed correctly

---

### 2. Test LLM Judge (Standalone)
```powershell
python src/llm_judge.py
```

**Expected Output**:
- ✓ Connection to Ollama confirmed
- Green "Connected to Ollama model: llama3"
- Sample gap analysis results displayed in a panel
- ✓ "Gap analysis test completed successfully!"

**Pass Criteria**:
- No connection errors
- LLM responds with coherent analysis
- Results displayed in Rich panel

---

### 3. Test Interactive Mode
```powershell
python main.py
```

**Steps**:
1. Enter path to user policy PDF (or use default)
2. Enter path to reference framework PDF (or use default)
3. Confirm gap analysis
4. Confirm remediation generation

**Expected Output**:
- Beautiful cyan header panel
- Progress spinners during processing
- Gap analysis results in green panel
- Remediation results in blue panel
- Success message with output file paths
- Final summary panel

**Pass Criteria**:
- All steps complete without errors
- Files created in `data/output/`:
  - `gap_analysis_YYYYMMDD_HHMMSS.md`
  - `remediation_YYYYMMDD_HHMMSS.md`
- Output files contain detailed analysis

---

### 4. Test Batch Mode
```powershell
python main.py --batch --user-policy "data/input/user_policy.pdf" --reference "data/reference/SAMPLE_NIST_REFERENCE.md"
```

**Expected Output**:
- Non-interactive processing
- Progress indicators
- Results saved automatically
- Summary displayed at end

**Pass Criteria**:
- Runs without user interaction
- Produces valid output files
- No errors in terminal

---

### 5. Test Different Models
```powershell
# First pull another model
ollama pull mistral

# Then test with mistral
python main.py --model mistral
```

**Expected Output**:
- Connects to Mistral model instead of Llama3
- Analysis completes successfully
- Results may differ slightly due to model differences

**Pass Criteria**:
- Model switching works
- Different models produce valid output
- No compatibility errors

---

## Integration Testing

### Full Workflow Test

#### Scenario: Analyze a weak security policy

**Test Policy** (create as `test_weak_policy.md`):
```
Our Information Security Policy

1. Passwords
   - Users must use passwords
   - Passwords should be changed sometimes

2. Data Backup
   - We backup important files
   - Backups stored on external drive

3. Access Control
   - Employees get access to systems they need
   - Managers approve access requests
```

**Steps**:
1. Save above as `data/input/test_weak_policy.md` (convert to PDF or use markdown)
2. Use provided `data/reference/SAMPLE_NIST_REFERENCE.md`
3. Run: `python main.py`

**Expected Gap Analysis Should Identify**:
- ✓ Missing multi-factor authentication
- ✓ Weak password policy (no complexity requirements)
- ✓ No encryption mentioned for backups
- ✓ Missing incident response plan
- ✓ No security awareness training
- ✓ No vulnerability management
- ✓ Missing continuous monitoring

**Expected Remediation Should Include**:
- ✓ Draft policy text for MFA implementation
- ✓ Specific password complexity requirements
- ✓ Backup encryption requirements
- ✓ Incident response procedures
- ✓ Security training requirements

**Pass Criteria**:
- All major gaps identified
- Remediation includes specific, actionable text
- Output is professionally formatted

---

## Performance Testing

### Test with Different Document Sizes

#### Small Document (5-10 pages)
- **Expected Time**: 3-5 minutes total
- **Memory Usage**: < 2GB

#### Medium Document (50-100 pages)
- **Expected Time**: 5-10 minutes total
- **Memory Usage**: 2-4GB

#### Large Document (200+ pages)
- **Expected Time**: 15-30 minutes total
- **Memory Usage**: 4-8GB

**Monitoring**:
```powershell
# Watch Ollama logs in separate terminal
ollama serve
```

**Pass Criteria**:
- Completes without crashes
- Memory usage remains stable
- No timeout errors

---

## Error Handling Testing

### Test Invalid PDF Path
```powershell
python main.py --batch --user-policy "nonexistent.pdf" --reference "data/reference/SAMPLE_NIST_REFERENCE.md"
```

**Expected**:
- ❌ Red error message: "File not found"
- Graceful exit, no crash

---

### Test Ollama Not Running
```powershell
# Stop Ollama first, then:
python src/llm_judge.py
```

**Expected**:
- ❌ Red error message: "Error connecting to Ollama"
- 💡 Yellow hint: "Make sure Ollama is running: 'ollama serve'"
- Graceful exit, no crash

---

### Test Missing Model
```powershell
python main.py --model nonexistent-model
```

**Expected**:
- ❌ Error about model not found
- Program exits gracefully

---

## Demo Preparation (For Hackathon Judges)

### Pre-Demo Setup
- [ ] Terminal cleared and ready
- [ ] Sample policy PDF prepared
- [ ] Ollama running (`ollama serve`)
- [ ] Virtual environment activated
- [ ] Working directory: `PS1/`

### Demo Script (5 minutes)

**Minute 1**: Introduction
```
"This is a local LLM-powered policy gap analysis tool.
It compares your security policy against NIST standards,
completely offline, using Ollama."
```

**Minute 2**: Show Interactive Mode
```powershell
python main.py
```
- Quick walkthrough of prompts
- Show progress indicators

**Minute 3**: Show Results
- Open `data/output/gap_analysis_*.md`
- Highlight identified gaps
- Show risk severity ratings

**Minute 4**: Show Remediation
- Open `data/output/remediation_*.md`
- Point out drafted policy text
- Show implementation roadmap

**Minute 5**: Technical Deep Dive
- Open `src/llm_judge.py`
- Show prompt engineering
- Explain offline architecture

### Backup Demo (If Issues)
- Have pre-generated output files ready
- Screenshots of successful runs
- Video recording of working demo

---

## Acceptance Criteria (Hackathon Requirements)

### ✅ Task 1: Gap Analysis
- [x] Ingests user policy (PDF/Text)
- [x] Ingests NIST framework (PDF/Text)
- [x] Uses local LLM (Ollama)
- [x] Identifies missing provisions
- [x] Identifies weak areas
- [x] Produces structured report

### ✅ Task 2: Remediation
- [x] Analyzes identified gaps
- [x] Generates specific recommendations
- [x] Produces revised policy text
- [x] Provides implementation guidance
- [x] Saves results to file

### ✅ Technical Constraints
- [x] 100% Offline (no cloud APIs)
- [x] Local LLM (Ollama with llama3/mistral)
- [x] Uses langchain
- [x] Uses pymupdf for PDF parsing
- [x] Uses rich for terminal output

---

## Final Pre-Submission Checklist

- [ ] All code files have proper docstrings
- [ ] README.md is complete and accurate
- [ ] QUICKSTART.md tested step-by-step
- [ ] ARCHITECTURE.md explains system design
- [ ] requirements.txt contains all dependencies
- [ ] .gitignore prevents committing sensitive data
- [ ] Sample reference document included
- [ ] All modules have standalone testing
- [ ] Error messages are helpful
- [ ] Output formatting is professional
- [ ] Code follows PEP 8 style guide
- [ ] No hardcoded secrets or API keys
- [ ] Works on fresh Windows installation

---

## Debugging Commands

### Check Ollama Status
```powershell
ollama list  # Show installed models
ollama ps    # Show running models
curl http://localhost:11434/api/tags  # API check
```

### Check Python Environment
```powershell
python --version
pip list  # Show installed packages
where python  # Verify venv active
```

### Verbose Logging
```python
# In config.py, set:
VERBOSE = True
```

### Test LangChain Connection
```powershell
python -c "from langchain_community.llms import Ollama; llm = Ollama(model='llama3'); print(llm.invoke('test'))"
```

---

## Success Metrics

**How to know everything works**:

1. ✅ No import errors when running any module
2. ✅ PDF extraction completes in < 10 seconds
3. ✅ Ollama connection establishes immediately
4. ✅ Gap analysis produces detailed, relevant output
5. ✅ Remediation includes actual policy text drafts
6. ✅ Output files are well-formatted markdown
7. ✅ Terminal UI is clean and professional
8. ✅ Error messages are clear and actionable

**If all the above pass, you're ready for the hackathon demo! 🚀**
