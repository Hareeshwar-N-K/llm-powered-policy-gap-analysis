"""
PDF Document Loader - Legacy Compatibility Wrapper
Use document_loader.py for enhanced multi-format support
"""
# Import the enhanced loader for backward compatibility
from .document_loader import DocumentLoader

# Backward compatibility alias
PDFLoader = DocumentLoader

# For direct usage
console = DocumentLoader().console if hasattr(DocumentLoader(), 'console') else None


# Legacy class for compatibility (delegates to DocumentLoader)
class PDFLoaderLegacy:
    """
    Handles extraction of text content from PDF files.
    Optimized for policy documents with proper error handling.
    """
    
    def __init__(self, verbose: bool = True):
        """
        Initialize the PDF loader.
        
        Args:
            verbose: Enable detailed console output
        """
        self.verbose = verbose
        
    def extract_text(self, pdf_path: str | Path) -> Optional[str]:
        """
        Extract all text content from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text content or None if extraction fails
        """
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            console.print(f"[red]Error: File not found: {pdf_path}[/red]")
            return None
            
        if not pdf_path.suffix.lower() == '.pdf':
            console.print(f"[red]Error: File is not a PDF: {pdf_path}[/red]")
            return None
        
        try:
            if self.verbose:
                console.print(f"[cyan]Loading PDF:[/cyan] {pdf_path.name}")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True
            ) as progress:
                task = progress.add_task("Extracting text...", total=None)
                
                # Open the PDF
                doc = fitz.open(pdf_path)
                text_content = []
                page_count = len(doc)  # Store page count before closing
                
                # Extract text from each page
                for page_num in range(page_count):
                    page = doc[page_num]
                    text_content.append(page.get_text())
                
                doc.close()
                progress.update(task, completed=True)
            
            # Combine all pages
            full_text = "\n\n".join(text_content)
            
            # Clean up the text
            full_text = self._clean_text(full_text)
            
            if self.verbose:
                word_count = len(full_text.split())
                char_count = len(full_text)
                console.print(f"[green]✓ Extracted {page_count} pages, {word_count:,} words, {char_count:,} characters[/green]")
            
            return full_text
            
        except Exception as e:
            console.print(f"[red]Error extracting PDF: {str(e)}[/red]")
            return None
    
    def _clean_text(self, text: str) -> str:
        """
        Clean extracted text by removing excessive whitespace and artifacts.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        # Remove multiple consecutive blank lines
        lines = text.split('\n')
        cleaned_lines = []
        prev_blank = False
        
        for line in lines:
            line = line.strip()
            if line:
                cleaned_lines.append(line)
                prev_blank = False
            elif not prev_blank:
                cleaned_lines.append('')
                prev_blank = True
        
        return '\n'.join(cleaned_lines)
    
    def extract_with_metadata(self, pdf_path: str | Path) -> Optional[dict]:
        """
        Extract text along with document metadata.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing text and metadata
        """
        pdf_path = Path(pdf_path)
        text = self.extract_text(pdf_path)
        
        if text is None:
            return None
        
        try:
            doc = fitz.open(pdf_path)
            metadata = {
                'filename': pdf_path.name,
                'page_count': len(doc),
                'title': doc.metadata.get('title', 'Unknown'),
                'author': doc.metadata.get('author', 'Unknown'),
                'subject': doc.metadata.get('subject', ''),
                'text': text,
                'word_count': len(text.split()),
                'char_count': len(text)
            }
            doc.close()
            return metadata
        except Exception as e:
            console.print(f"[yellow]Warning: Could not extract metadata: {str(e)}[/yellow]")
            return {
                'filename': pdf_path.name,
                'text': text,
                'word_count': len(text.split()),
                'char_count': len(text)
            }


# Standalone testing functionality
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        console.print("[yellow]Usage: python pdf_loader.py <path_to_pdf>[/yellow]")
        console.print("[yellow]Example: python pdf_loader.py data/input/policy.pdf[/yellow]")
        sys.exit(1)
    
    loader = PDFLoader(verbose=True)
    pdf_file = sys.argv[1]
    
    console.print(f"\n[bold]Testing PDF Loader[/bold]\n")
    result = loader.extract_with_metadata(pdf_file)
    
    if result:
        console.print("\n[bold green]Extraction Successful![/bold green]")
        console.print(f"\nMetadata:")
        for key, value in result.items():
            if key != 'text':
                console.print(f"  {key}: {value}")
        
        console.print(f"\n[bold]First 500 characters of extracted text:[/bold]")
        console.print(result['text'][:500])
    else:
        console.print("[red]Extraction failed![/red]")
