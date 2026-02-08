"""
Quick Test Script - Verify All Fixes Are Working
Run this BEFORE the main tool to ensure everything is set up correctly
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from rich.console import Console
from rich.panel import Panel

console = Console()

def test_imports():
    """Test if all required modules can be imported."""
    console.print("\n[bold cyan]Testing imports...[/bold cyan]")
    
    try:
        from src.document_loader import DocumentLoader
        console.print("✓ DocumentLoader imported successfully")
    except Exception as e:
        console.print(f"[red]✗ DocumentLoader import failed: {e}[/red]")
        return False
    
    try:
        from src.llm_judge import PolicyJudge
        console.print("✓ PolicyJudge imported successfully")
    except Exception as e:
        console.print(f"[red]✗ PolicyJudge import failed: {e}[/red]")
        return False
    
    try:
        from src.utils import ComplianceScorer, ResultExporter, ExecutiveSummary
        console.print("✓ Utils (ComplianceScorer, ResultExporter, ExecutiveSummary) imported successfully")
    except Exception as e:
        console.print(f"[red]✗ Utils import failed: {e}[/red]")
        return False
    
    try:
        import config
        console.print("✓ Config imported successfully")
    except Exception as e:
        console.print(f"[red]✗ Config import failed: {e}[/red]")
        return False
    
    return True

def test_document_loader():
    """Test the document loader with sample file."""
    console.print("\n[bold cyan]Testing DocumentLoader...[/bold cyan]")
    
    try:
        from src.document_loader import DocumentLoader
        import config
        
        loader = DocumentLoader(
            verbose=False,
            search_dirs=[config.INPUT_DIR, config.REFERENCE_DIR]
        )
        
        # Test with the sample NIST reference
        sample_file = config.REFERENCE_DIR / "SAMPLE_NIST_REFERENCE.md"
        if sample_file.exists():
            text = loader.extract_text(sample_file)
            if text:
                console.print(f"✓ Successfully loaded {sample_file.name}")
                console.print(f"  Extracted {len(text.split())} words")
                return True
            else:
                console.print("[red]✗ Failed to extract text[/red]")
                return False
        else:
            console.print(f"[yellow]⚠ Sample file not found: {sample_file}[/yellow]")
            console.print("[yellow]  This is OK - just place your files in data/input/[/yellow]")
            return True
            
    except Exception as e:
        console.print(f"[red]✗ DocumentLoader test failed: {e}[/red]")
        import traceback
        traceback.print_exc()
        return False

def test_ollama_connection():
    """Test connection to Ollama."""
    console.print("\n[bold cyan]Testing Ollama connection...[/bold cyan]")
    
    try:
        from langchain_community.llms import Ollama
        import config
        
        llm = Ollama(
            model=config.OLLAMA_MODEL,
            base_url=config.OLLAMA_BASE_URL,
            temperature=0.1
        )
        
        # Simple test
        result = llm.invoke("Say 'test successful' and nothing else.")
        console.print(f"✓ Ollama connection successful")
        console.print(f"  Model: {config.OLLAMA_MODEL}")
        console.print(f"  Response: {result [:50]}...")
        return True
        
    except Exception as e:
        console.print(f"[red]✗ Ollama connection failed: {e}[/red]")
        console.print("[yellow]Make sure Ollama is running: ollama serve[/yellow]")
        console.print(f"[yellow]And model is downloaded: ollama pull {config.OLLAMA_MODEL}[/yellow]")
        return False

def test_compliance_scorer():
    """Test the compliance scoring system."""
    console.print("\n[bold cyan]Testing ComplianceScorer...[/bold cyan]")
    
    try:
        from src.utils import ComplianceScorer
        
        scorer = ComplianceScorer()
        sample_analysis = "Critical gap: Missing MFA. High risk: Weak passwords. Medium: Training needed."
        
        score = scorer.calculate_score(sample_analysis)
        console.print(f"✓ ComplianceScorer working")
        console.print(f"  Sample score: {score['compliance_percentage']}")
        return True
        
    except Exception as e:
        console.print(f"[red]✗ ComplianceScorer test failed: {e}[/red]")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    console.print(Panel.fit(
        "[bold]Quick Test Suite - Policy Gap Analysis Tool[/bold]\n"
        "[dim]Verifying all components are working correctly[/dim]",
        border_style="cyan"
    ))
    
    results = []
    
    # Test 1: Imports
    results.append(("Imports", test_imports()))
    
    # Test 2: Document Loader
    results.append(("DocumentLoader", test_document_loader()))
    
    # Test 3: Compliance Scorer
    results.append(("ComplianceScorer", test_compliance_scorer()))
    
    # Test 4: Ollama (optional, may fail if not running)
    results.append(("Ollama Connection", test_ollama_connection()))
    
    # Summary
    console.print("\n" + "="*70)
    console.print("\n[bold]Test Results Summary:[/bold]\n")
    
    for test_name, result in results:
        icon = "✓" if result else "✗"
        color = "green" if result else "red"
        console.print(f"[{color}]{icon} {test_name}[/{color}]")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    console.print(f"\n[bold]Passed: {passed}/{total}[/bold]")
    
    if passed == total:
        console.print(Panel.fit(
            "[bold green]All tests passed! ✓[/bold green]\n"
            "[white]You're ready to run:[/white] [cyan]python main.py[/cyan]",
            border_style="green"
        ))
    elif passed >= total - 1:  # Allow Ollama to fail
        console.print(Panel.fit(
            "[bold yellow]Most tests passed! ⚠[/bold yellow]\n"
            "[white]Make sure Ollama is running:[/white]\n"
            "[cyan]  1. ollama serve\n  2. ollama pull llama3.2:3b[/cyan]\n"
            "[white]Then run:[/white] [cyan]python main.py[/cyan]",
            border_style="yellow"
        ))
    else:
        console.print(Panel.fit(
            "[bold red]Some tests failed![/bold red]\n"
            "[white]Install dependencies:[/white] [cyan]pip install -r requirements.txt[/cyan]\n"
            "[white]Then try again:[/white] [cyan]python test_setup.py[/cyan]",
            border_style="red"
        ))
    
    console.print()

if __name__ == "__main__":
    main()
