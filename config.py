"""
Configuration settings for the Policy Gap Analysis Tool
"""
import os
from pathlib import Path

# Project Paths
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
INPUT_DIR = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"
REFERENCE_DIR = DATA_DIR / "reference"

# Ensure directories exist
for directory in [DATA_DIR, INPUT_DIR, OUTPUT_DIR, REFERENCE_DIR]:
    directory.mkdir(exist_ok=True, parents=True)

# Ollama Configuration
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2:3b"  # Can be changed to "mistral" or other models

# LLM Parameters
LLM_TEMPERATURE = 0.1  # Low temperature for consistent, factual analysis
LLM_MAX_TOKENS = 4096
LLM_TIMEOUT = 300  # 5 minutes timeout

# Reference Standard
REFERENCE_FRAMEWORK = "CIS MS-ISAC NIST Cybersecurity Framework"

# Output Settings
OUTPUT_FORMAT = "markdown"  # or "json", "pdf"
VERBOSE = True
