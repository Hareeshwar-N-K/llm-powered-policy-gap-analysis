"""
Main Orchestration Script - Policy Gap Analysis Tool
Coordinates the entire gap analysis and remediation workflow
"""
import sys
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich import box
from rich.prompt import Prompt, Confirm

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.document_loader import DocumentLoader
from src.llm_judge import PolicyJudge
from src.utils import ComplianceScorer, ResultExporter, ExecutiveSummary
import config
import json

console = Console()


class PolicyAnalysisPipeline:
    """
    Main pipeline orchestrating the complete policy gap analysis workflow.
    """
    
    def __init__(self):
        """Initialize the analysis pipeline."""
        # Use enhanced DocumentLoader with smart path searching
        self.doc_loader = DocumentLoader(
            verbose=config.VERBOSE,
            search_dirs=[config.INPUT_DIR, config.REFERENCE_DIR, Path.cwd()]
        )
        self.judge = None  # Initialized when needed
        self.results = {}
        self.scorer = ComplianceScorer()
        self.exporter = ResultExporter()
    
    def run_interactive(self):
        """Run the tool in interactive mode."""
        console.print(Panel.fit(
            "[bold cyan]HACK IITK 2026 - Policy Gap Analysis Tool[/bold cyan]\n"
            "[white]Local LLM Powered Cybersecurity Analysis[/white]\n"
            f"[dim]Model: {config.OLLAMA_MODEL} | Framework: {config.REFERENCE_FRAMEWORK}[/dim]",
            border_style="cyan",
            box=box.DOUBLE
        ))
        
        # Step 1: Load user policy
        console.print("\n[bold]Step 1: Load Your Organization's Policy[/bold]")
        console.print("[dim]Supported formats: PDF, TXT, MD[/dim]")
        user_policy_path = Prompt.ask(
            "Enter path to your policy file",
            default=str(config.INPUT_DIR / "user_policy.pdf")
        )
        
        user_policy_text = self.doc_loader.extract_text(user_policy_path)
        if not user_policy_text:
            console.print("[red]Failed to load user policy. Exiting.[/red]")
            return
        
        # Step 2: Load reference standard
        console.print("\n[bold]Step 2: Load Reference Standard[/bold]")
        console.print("[dim]Supported formats: PDF, TXT, MD[/dim]")
        reference_path = Prompt.ask(
            "Enter path to reference framework file",
            default=str(config.REFERENCE_DIR / "SAMPLE_NIST_REFERENCE.md")
        )
        
        reference_text = self.doc_loader.extract_text(reference_path)
        if not reference_text:
            console.print("[red]Failed to load reference framework. Exiting.[/red]")
            return
        
        # Step 3: Initialize LLM Judge
        console.print("\n[bold]Step 3: Initialize Local LLM[/bold]")
        try:
            self.judge = PolicyJudge(verbose=config.VERBOSE)
        except Exception as e:
            console.print(f"[red]Failed to initialize LLM: {str(e)}[/red]")
            return
        
        # Step 4: Gap Analysis
        if Confirm.ask("\n[bold]Proceed with Gap Analysis?[/bold]", default=True):
            console.print("\n" + "="*70)
            gap_result = self.judge.analyze_gaps(
                user_policy_text=user_policy_text,
                reference_standard_text=reference_text,
                framework_name=config.REFERENCE_FRAMEWORK
            )
            
            if gap_result:
                self.results['gap_analysis'] = gap_result
                
                # Calculate compliance score
                console.print("\n[cyan]Calculating compliance score...[/cyan]")
                score = self.scorer.calculate_score(gap_result['analysis'])
                self.results['compliance_score'] = score
                self.scorer.display_score(score)
                
                # Generate executive summary
                console.print("\n[cyan]Generating executive summary...[/cyan]")
                exec_summary = ExecutiveSummary.generate(gap_result['analysis'], score)
                self.results['executive_summary'] = exec_summary
                
                self._save_results(gap_result, "gap_analysis")
        
        # Step 5: Remediation
        if 'gap_analysis' in self.results and Confirm.ask("\n[bold]Generate Remediation Plan?[/bold]", default=True):
            console.print("\n" + "="*70)
            remediation_result = self.judge.generate_remediation(
                user_policy_text=user_policy_text,
                gap_analysis=self.results['gap_analysis']['analysis'],
                framework_name=config.REFERENCE_FRAMEWORK
            )
            
            if remediation_result:
                self.results['remediation'] = remediation_result
                self._save_results(remediation_result, "remediation")
        
        # Step 6: Export options
        if self.results and Confirm.ask("\n[bold]Export complete report (Markdown + JSON)?[/bold]", default=True):
            self._export_complete_report()
        
        # Summary
        self._print_summary()
    
    def run_batch(self, user_policy_path: str, reference_path: str):
        """
        Run the tool in batch mode (non-interactive).
        
        Args:
            user_policy_path: Path to user's policy PDF
            reference_path: Path to reference framework PDF
        """
        console.print(Panel.fit(
            "[bold cyan]Policy Gap Analysis - Batch Mode[/bold cyan]",
            border_style="cyan"
        ))
        
        # Load documents
        console.print("\n[bold]Loading Documents...[/bold]")
        user_policy_text = self.doc_loader.extract_text(user_policy_path)
        reference_text = self.doc_loader.extract_text(reference_path)
        
        if not user_policy_text or not reference_text:
            console.print("[red]Failed to load documents. Exiting.[/red]")
            return False
        
        # Initialize LLM
        try:
            self.judge = PolicyJudge(verbose=config.VERBOSE)
        except Exception as e:
            console.print(f"[red]Failed to initialize LLM: {str(e)}[/red]")
            return False
        
        # Run analysis
        gap_result = self.judge.analyze_gaps(
            user_policy_text=user_policy_text,
            reference_standard_text=reference_text,
            framework_name=config.REFERENCE_FRAMEWORK
        )
        
        if gap_result:
            self.results['gap_analysis'] = gap_result
            
            # Calculate compliance score
            score = self.scorer.calculate_score(gap_result['analysis'])
            self.results['compliance_score'] = score
            self.scorer.display_score(score)
            
            # Generate executive summary
            exec_summary = ExecutiveSummary.generate(gap_result['analysis'], score)
            self.results['executive_summary'] = exec_summary
            
            self._save_results(gap_result, "gap_analysis")
        else:
            return False
        
        # Run remediation
        # Export complete report
        self._export_complete_report()
        
        remediation_result = self.judge.generate_remediation(
            user_policy_text=user_policy_text,
            gap_analysis=gap_result['analysis'],
            framework_name=config.REFERENCE_FRAMEWORK
        )
        
        if remediation_result:
            self.results['remediation'] = remediation_result
            self._save_results(remediation_result, "remediation")
        
        self._print_summary()
        return True
    
    def _save_results(self, result: dict, result_type: str):
        """
        Save analysis results to output directory.
        
        Args:
            result: Result dictionary from analysis
            result_type: Type of result ('gap_analysis' or 'remediation')
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{result_type}_{timestamp}.md"
        output_path = config.OUTPUT_DIR / filename
        
        content = f"""# {result_type.replace('_', ' ').title()}
        
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Framework:** {result['framework']}  
**Model Used:** {result['model_used']}

---

"""
        
        if result_type == "gap_analysis":
            content += result['analysis']
        else:
            content += result['remediation']
        
        output_path.write_text(content, encoding='utf-8')
        console.print(f"\n[green]✓ Results saved to:[/green] [cyan]{output_path}[/cyan]")
    
    def _export_complete_report(self):
        """Export complete analysis report in multiple formats."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Prepare complete results
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'framework': config.REFERENCE_FRAMEWORK,
            'model': config.OLLAMA_MODEL,
            **self.results
        }
        
        # Export to JSON
        json_path = config.OUTPUT_DIR / f"complete_report_{timestamp}.json"
        self.exporter.export_to_json(export_data, json_path)
        
        # Export enhanced markdown with all sections
        md_path = config.OUTPUT_DIR / f"complete_report_{timestamp}.md"
        self.exporter.export_to_markdown(export_data, md_path, include_score=True)
        
        # Save executive summary separately
        if 'executive_summary' in self.results:
            exec_path = config.OUTPUT_DIR / f"executive_summary_{timestamp}.md"
            exec_path.write_text(self.results['executive_summary'], encoding='utf-8')
            console.print(f"[green]✓ Executive summary saved to:[/green] [cyan]{exec_path}[/cyan]")
    
    def _print_summary(self):
        """Print final summary of the analysis."""
        console.print("\n" + "="*70)
        
        summary_text = "[bold green]Analysis Complete![/bold green]\n\n"
        summary_text += f"[white]Gap Analysis: [/white]{'✓' if 'gap_analysis' in self.results else '✗'}\n"
        
        if 'compliance_score' in self.results:
            score = self.results['compliance_score']['compliance_percentage']
            summary_text += f"[white]Compliance Score: [/white]{score}\n"
        
        summary_text += f"[white]Remediation: [/white]{'✓' if 'remediation' in self.results else '✗'}\n"
        summary_text += f"[white]Executive Summary: [/white]{'✓' if 'executive_summary' in self.results else '✗'}\n\n"
        summary_text += f"[dim]Results saved to: {config.OUTPUT_DIR}[/dim]"
        
        console.print(Panel.fit(
            summary_text,
            border_style="green",
            box=box.DOUBLE
        ))


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Policy Gap Analysis Tool - Local LLM Powered",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--user-policy',
        type=str,
        help='Path to user policy PDF file'
    )
    
    parser.add_argument(
        '--reference',
        type=str,
        help='Path to reference framework PDF file'
    )
    
    parser.add_argument(
        '--batch',
        action='store_true',
        help='Run in batch mode (non-interactive)'
    )
    
    parser.add_argument(
        '--model',
        type=str,
        default=config.OLLAMA_MODEL,
        help=f'Ollama model to use (default: {config.OLLAMA_MODEL})'
    )
    
    args = parser.parse_args()
    
    # Update model if specified
    if args.model:
        config.OLLAMA_MODEL = args.model
    
    # Create pipeline
    pipeline = PolicyAnalysisPipeline()
    
    # Run in appropriate mode
    if args.batch and args.user_policy and args.reference:
        pipeline.run_batch(args.user_policy, args.reference)
    else:
        pipeline.run_interactive()


if __name__ == "__main__":
    main()
