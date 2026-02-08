"""
Module 2: LLM Judge - Gap Analysis Engine
Uses local Ollama LLM to analyze policy gaps against NIST standards
"""
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing import Optional, Dict
import config

console = Console()


class PolicyJudge:
    """
    LLM-powered judge that analyzes organizational policies against
    cybersecurity frameworks and identifies gaps.
    """
    
    def __init__(
        self,
        model_name: str = config.OLLAMA_MODEL,
        base_url: str = config.OLLAMA_BASE_URL,
        temperature: float = config.LLM_TEMPERATURE,
        verbose: bool = True
    ):
        """
        Initialize the Policy Judge with local Ollama LLM.
        
        Args:
            model_name: Name of the Ollama model to use
            base_url: Base URL for Ollama API
            temperature: LLM temperature (lower = more deterministic)
            verbose: Enable detailed console output
        """
        self.model_name = model_name
        self.base_url = base_url
        self.temperature = temperature
        self.verbose = verbose
        self.llm = None
        
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize connection to local Ollama instance."""
        try:
            if self.verbose:
                console.print(f"[cyan]Connecting to Ollama at {self.base_url}...[/cyan]")
            
            self.llm = Ollama(
                model=self.model_name,
                base_url=self.base_url,
                temperature=self.temperature,
                timeout=config.LLM_TIMEOUT
            )
            
            if self.verbose:
                console.print(f"[green]✓ Connected to Ollama model: {self.model_name}[/green]")
                
        except Exception as e:
            console.print(f"[red]Error connecting to Ollama: {str(e)}[/red]")
            console.print("[yellow]Make sure Ollama is running: 'ollama serve'[/yellow]")
            raise
    
    def analyze_gaps(
        self,
        user_policy_text: str,
        reference_standard_text: str,
        framework_name: str = config.REFERENCE_FRAMEWORK
    ) -> Optional[Dict[str, str]]:
        """
        Perform comprehensive gap analysis between user policy and reference standard.
        
        Args:
            user_policy_text: The organization's current policy document
            reference_standard_text: The reference framework (e.g., NIST CSF)
            framework_name: Name of the reference framework
            
        Returns:
            Dictionary containing gap analysis results
        """
        if self.verbose:
            console.print(f"\n[bold cyan]Starting Gap Analysis[/bold cyan]")
            console.print(f"Framework: {framework_name}\n")
        
        # Create the gap analysis prompt
        gap_prompt_template = self._create_gap_analysis_prompt()
        
        prompt = PromptTemplate(
            input_variables=["user_policy", "reference_standard", "framework_name"],
            template=gap_prompt_template
        )
        
        # Create LangChain chain
        chain = LLMChain(llm=self.llm, prompt=prompt)
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=False
            ) as progress:
                task = progress.add_task(
                    f"[cyan]Analyzing policy against {framework_name}...",
                    total=None
                )
                
                # Run the analysis
                response = chain.invoke({
                    "user_policy": user_policy_text,
                    "reference_standard": reference_standard_text,
                    "framework_name": framework_name
                })
                
                progress.update(task, completed=True)
            
            analysis_text = response['text']
            
            if self.verbose:
                console.print("\n[green]✓ Gap Analysis Complete[/green]\n")
                console.print(Panel(
                    analysis_text,
                    title="[bold]Gap Analysis Results[/bold]",
                    border_style="green"
                ))
            
            return {
                'framework': framework_name,
                'analysis': analysis_text,
                'model_used': self.model_name
            }
            
        except Exception as e:
            console.print(f"[red]Error during gap analysis: {str(e)}[/red]")
            return None
    
    def generate_remediation(
        self,
        user_policy_text: str,
        gap_analysis: str,
        framework_name: str = config.REFERENCE_FRAMEWORK
    ) -> Optional[Dict[str, str]]:
        """
        Generate remediation recommendations and revised policy sections.
        
        Args:
            user_policy_text: Original policy text
            gap_analysis: Results from gap analysis
            framework_name: Name of reference framework
            
        Returns:
            Dictionary containing remediation recommendations
        """
        if self.verbose:
            console.print(f"\n[bold cyan]Generating Remediation Plan[/bold cyan]\n")
        
        remediation_prompt_template = self._create_remediation_prompt()
        
        prompt = PromptTemplate(
            input_variables=["user_policy", "gap_analysis", "framework_name"],
            template=remediation_prompt_template
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=False
            ) as progress:
                task = progress.add_task(
                    "[cyan]Generating remediation recommendations...",
                    total=None
                )
                
                response = chain.invoke({
                    "user_policy": user_policy_text,
                    "gap_analysis": gap_analysis,
                    "framework_name": framework_name
                })
                
                progress.update(task, completed=True)
            
            remediation_text = response['text']
            
            if self.verbose:
                console.print("\n[green]✓ Remediation Plan Generated[/green]\n")
                console.print(Panel(
                    remediation_text,
                    title="[bold]Remediation Recommendations[/bold]",
                    border_style="blue"
                ))
            
            return {
                'framework': framework_name,
                'remediation': remediation_text,
                'model_used': self.model_name
            }
            
        except Exception as e:
            console.print(f"[red]Error generating remediation: {str(e)}[/red]")
            return None
    
    def _create_gap_analysis_prompt(self) -> str:
        """
        Create the prompt template for gap analysis.
        This is the core logic that guides the LLM's analysis.
        """
        return """You are an expert cybersecurity policy analyst specializing in {framework_name}.

Your task is to perform a comprehensive gap analysis by comparing the organization's current policy against the reference cybersecurity framework.

**REFERENCE FRAMEWORK ({framework_name}):**
{reference_standard}

**ORGANIZATION'S CURRENT POLICY:**
{user_policy}

**YOUR ANALYSIS MUST INCLUDE:**

1. **MISSING PROVISIONS**: Identify critical security controls, policies, or procedures that are present in the reference framework but completely absent from the organization's policy.

2. **WEAK OR INCOMPLETE AREAS**: Highlight sections where the organization's policy exists but is insufficient, vague, or less comprehensive than the framework requirements.

3. **COMPLIANCE GAPS**: List specific framework requirements that are not adequately addressed.

4. **RISK ASSESSMENT**: Evaluate the severity of each gap (Critical, High, Medium, Low) and explain the potential security risks.

5. **PRIORITY AREAS**: Identify the top 5 most critical gaps that should be addressed immediately.

**OUTPUT FORMAT:**
Provide a structured analysis with clear headings and bullet points. Be specific, citing exact sections from both documents when possible.

Begin your analysis:"""
    
    def _create_remediation_prompt(self) -> str:
        """
        Create the prompt template for remediation generation.
        """
        return """You are an expert cybersecurity policy writer and consultant.

Based on the gap analysis performed against {framework_name}, you must now generate specific remediation recommendations and draft revised policy sections.

**ORIGINAL POLICY:**
{user_policy}

**GAP ANALYSIS FINDINGS:**
{gap_analysis}

**YOUR REMEDIATION PLAN MUST INCLUDE:**

1. **EXECUTIVE SUMMARY**: Brief overview of required changes (2-3 paragraphs).

2. **SPECIFIC RECOMMENDATIONS**: For each identified gap, provide:
   - Clear description of what needs to be added/changed
   - Rationale based on the framework
   - Implementation priority (Immediate, Short-term, Long-term)

3. **REVISED POLICY SECTIONS**: Draft the actual policy text that should be added or modified. Write this in professional policy language, ready to be inserted into the organization's policy document.

4. **IMPLEMENTATION ROADMAP**: Suggest a phased approach for implementing these changes.

5. **COMPLIANCE VALIDATION**: List specific checkpoints to verify compliance after implementation.

**OUTPUT FORMAT:**
Provide a structured remediation plan with clear sections. Draft policy text should be clearly marked and ready for copy-paste into the organization's policy documents.

Begin your remediation plan:"""


# Standalone testing functionality
if __name__ == "__main__":
    console.print("\n[bold]Testing LLM Judge Module[/bold]\n")
    
    # Sample test data
    sample_policy = """
    Our company uses passwords for authentication. 
    We back up data weekly.
    Employees must not share credentials.
    """
    
    sample_standard = """
    NIST Cybersecurity Framework Requirements:
    - Multi-factor authentication must be implemented for all users
    - Data backups must be encrypted and tested quarterly
    - Access control policies must include least privilege principle
    - Incident response plan must be documented and tested annually
    - Security awareness training required for all personnel
    """
    
    try:
        judge = PolicyJudge(verbose=True)
        
        # Test gap analysis
        result = judge.analyze_gaps(
            user_policy_text=sample_policy,
            reference_standard_text=sample_standard,
            framework_name="NIST CSF (Sample)"
        )
        
        if result:
            console.print("\n[green]Gap analysis test completed successfully![/green]")
        
    except Exception as e:
        console.print(f"\n[red]Test failed: {str(e)}[/red]")
        console.print("[yellow]Ensure Ollama is running with: ollama serve[/yellow]")
