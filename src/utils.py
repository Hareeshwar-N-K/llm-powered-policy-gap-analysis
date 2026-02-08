"""
Enhanced utilities for policy analysis
Includes scoring, export, and summary generation
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


class ComplianceScorer:
    """
    Calculates compliance scores based on gap analysis results.
    """
    
    @staticmethod
    def calculate_score(gap_analysis_text: str) -> Dict:
        """
        Calculate compliance score from gap analysis text.
        
        Args:
            gap_analysis_text: The gap analysis output from LLM
            
        Returns:
            Dictionary with scoring metrics
        """
        # Keywords indicating different severity levels
        critical_keywords = ['critical', 'severe', 'urgent', 'missing', 'absent', 'mandatory']
        high_keywords = ['high risk', 'significant', 'important', 'required']
        medium_keywords = ['medium', 'moderate', 'should', 'recommended']
        low_keywords = ['low', 'minor', 'optional', 'suggested']
        
        text_lower = gap_analysis_text.lower()
        
        # Count occurrences
        critical_count = sum(text_lower.count(kw) for kw in critical_keywords)
        high_count = sum(text_lower.count(kw) for kw in high_keywords)
        medium_count = sum(text_lower.count(kw) for kw in medium_keywords)
        low_count = sum(text_lower.count(kw) for kw in low_keywords)
        
        # Calculate weighted score (100 = perfect compliance, 0 = no compliance)
        total_issues = critical_count + high_count + medium_count + low_count
        
        if total_issues == 0:
            compliance_score = 100
        else:
            # Weighted deduction
            deduction = (
                critical_count * 10 +
                high_count * 5 +
                medium_count * 2 +
                low_count * 1
            )
            compliance_score = max(0, 100 - deduction)
        
        return {
            'compliance_score': compliance_score,
            'compliance_percentage': f"{compliance_score}%",
            'total_gaps': total_issues,
            'breakdown': {
                'critical': critical_count,
                'high': high_count,
                'medium': medium_count,
                'low': low_count
            },
            'risk_level': _get_risk_level(compliance_score)
        }
    
    @staticmethod
    def display_score(score_data: Dict):
        """Display compliance score in a nice format."""
        score = score_data['compliance_score']
        
        # Color based on score
        if score >= 80:
            color = "green"
            emoji = "✓"
        elif score >= 60:
            color = "yellow"
            emoji = "⚠"
        else:
            color = "red"
            emoji = "✗"
        
        # Create table
        table = Table(title="Compliance Score", show_header=True, header_style="bold cyan")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style=color)
        
        table.add_row("Overall Compliance", f"{emoji} {score_data['compliance_percentage']}")
        table.add_row("Risk Level", score_data['risk_level'])
        table.add_row("Total Gaps Found", str(score_data['total_gaps']))
        table.add_row("  • Critical", str(score_data['breakdown']['critical']))
        table.add_row("  • High", str(score_data['breakdown']['high']))
        table.add_row("  • Medium", str(score_data['breakdown']['medium']))
        table.add_row("  • Low", str(score_data['breakdown']['low']))
        
        console.print(table)


class ResultExporter:
    """
    Export analysis results in multiple formats.
    """
    
    @staticmethod
    def export_to_json(results: Dict, output_path: Path):
        """
        Export results to JSON format.
        
        Args:
            results: Analysis results dictionary
            output_path: Path to save JSON file
        """
        try:
            # Add timestamp
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                **results
            }
            
            output_path.write_text(json.dumps(export_data, indent=2, ensure_ascii=False))
            console.print(f"[green]✓ JSON exported to:[/green] {output_path}")
            
        except Exception as e:
            console.print(f"[red]Error exporting JSON: {str(e)}[/red]")
    
    @staticmethod
    def export_to_markdown(results: Dict, output_path: Path, include_score: bool = True):
        """
        Export results to enhanced Markdown format.
        
        Args:
            results: Analysis results dictionary
            output_path: Path to save markdown file
            include_score: Whether to include compliance scoring
        """
        try:
            content = []
            content.append(f"# Policy Gap Analysis Report\n")
            content.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            if 'framework' in results:
                content.append(f"**Framework:** {results['framework']}\n")
            if 'model_used' in results:
                content.append(f"**AI Model:** {results['model_used']}\n")
            
            content.append("\n---\n\n")
            
            # Add compliance score if available
            if include_score and 'compliance_score' in results:
                score_data = results['compliance_score']
                content.append("## Compliance Score\n\n")
                content.append(f"- **Overall Compliance:** {score_data['compliance_percentage']}\n")
                content.append(f"- **Risk Level:** {score_data['risk_level']}\n")
                content.append(f"- **Total Gaps:** {score_data['total_gaps']}\n")
                content.append(f"  - Critical: {score_data['breakdown']['critical']}\n")
                content.append(f"  - High: {score_data['breakdown']['high']}\n")
                content.append(f"  - Medium: {score_data['breakdown']['medium']}\n")
                content.append(f"  - Low: {score_data['breakdown']['low']}\n\n")
                content.append("---\n\n")
            
            # Add analysis content
            if 'analysis' in results:
                content.append("## Gap Analysis\n\n")
                content.append(results['analysis'])
                content.append("\n\n")
            
            if 'remediation' in results:
                content.append("## Remediation Plan\n\n")
                content.append(results['remediation'])
                content.append("\n\n")
            
            # Add footer
            content.append("\n---\n\n")
            content.append("*Generated by Policy Gap Analysis Tool - HACK IITK 2026*\n")
            
            output_path.write_text(''.join(content), encoding='utf-8')
            console.print(f"[green]✓ Markdown exported to:[/green] {output_path}")
            
        except Exception as e:
            console.print(f"[red]Error exporting Markdown: {str(e)}[/red]")


class ExecutiveSummary:
    """
    Generate executive summaries from analysis results.
    """
    
    @staticmethod
    def generate(gap_analysis: str, compliance_score: Dict) -> str:
        """
        Generate an executive summary from gap analysis.
        
        Args:
            gap_analysis: Gap analysis text
            compliance_score: Compliance score data
            
        Returns:
            Executive summary text
        """
        summary = []
        
        summary.append("# EXECUTIVE SUMMARY\n")
        summary.append(f"**Date:** {datetime.now().strftime('%B %d, %Y')}\n\n")
        
        # Overall assessment
        score = compliance_score['compliance_score']
        if score >= 80:
            assessment = "Your organization's cybersecurity policy demonstrates strong compliance with industry standards."
        elif score >= 60:
            assessment = "Your organization's cybersecurity policy shows moderate compliance but requires significant improvements."
        else:
            assessment = "Your organization's cybersecurity policy has critical gaps that expose you to substantial security risks."
        
        summary.append(f"## Overall Assessment\n\n{assessment}\n\n")
        
        # Key metrics
        summary.append("## Key Metrics\n\n")
        summary.append(f"- **Compliance Score:** {compliance_score['compliance_percentage']}\n")
        summary.append(f"- **Risk Level:** {compliance_score['risk_level']}\n")
        summary.append(f"- **Total Gaps Identified:** {compliance_score['total_gaps']}\n")
        summary.append(f"- **Critical Issues:** {compliance_score['breakdown']['critical']}\n\n")
        
        # Recommendations
        summary.append("## Priority Recommendations\n\n")
        if 'top 5' in gap_analysis.lower() or 'priority' in gap_analysis.lower():
            summary.append("Critical gaps requiring immediate attention have been identified. ")
        
        summary.append("Please refer to the detailed gap analysis and remediation plan for specific actions.\n\n")
        
        # Timeline
        summary.append("## Recommended Timeline\n\n")
        if compliance_score['breakdown']['critical'] > 0:
            summary.append("- **Immediate (0-30 days):** Address critical security gaps\n")
        if compliance_score['breakdown']['high'] > 0:
            summary.append("- **Short-term (1-3 months):** Implement high-priority improvements\n")
        if compliance_score['breakdown']['medium'] > 0:
            summary.append("- **Medium-term (3-6 months):** Complete medium-priority enhancements\n")
        summary.append("- **Long-term (6-12 months):** Continuous improvement and monitoring\n\n")
        
        return ''.join(summary)


def _get_risk_level(score: int) -> str:
    """Get risk level string based on compliance score."""
    if score >= 90:
        return "Very Low"
    elif score >= 80:
        return "Low"
    elif score >= 70:
        return "Moderate"
    elif score >= 60:
        return "High"
    else:
        return "Critical"


# Testing
if __name__ == "__main__":
    # Test compliance scoring
    sample_analysis = """
    CRITICAL GAPS:
    1. Missing multi-factor authentication - CRITICAL
    2. No incident response plan - CRITICAL
    3. Weak password policy - HIGH RISK
    4. Backup encryption not mentioned - HIGH
    5. Security training not mandatory - MEDIUM
    """
    
    scorer = ComplianceScorer()
    score = scorer.calculate_score(sample_analysis)
    scorer.display_score(score)
    
    # Test executive summary
    summary_gen = ExecutiveSummary()
    summary = summary_gen.generate(sample_analysis, score)
    console.print(Panel(summary, title="Executive Summary", border_style="cyan"))
