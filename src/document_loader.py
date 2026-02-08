"""
Enhanced Document Loader - Supports PDF, TXT, MD files
Replaces basic PDF loader with multi-format support
"""
import fitz  # PyMuPDF
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


class DocumentLoader:
    """
    Enhanced document loader supporting multiple formats:
    - PDF (.pdf)
    - Text files (.txt)
    - Markdown (.md)
    """
    
    def __init__(self, verbose: bool = True, search_dirs: list[Path] = None):
        """
        Initialize the document loader.
        
        Args:
            verbose: Enable detailed console output
            search_dirs: Directories to search for files if not found at given path
        """
        self.verbose = verbose
        self.search_dirs = search_dirs or []
        
    def extract_text(self, file_path: str | Path) -> Optional[str]:
        """
        Extract text content from PDF, TXT, or MD file with smart path resolution.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Extracted text content or None if extraction fails
        """
        # Resolve the file path
        resolved_path = self._resolve_path(file_path)
        
        if not resolved_path:
            console.print(f"[red]Error: File not found: {file_path}[/red]")
            if self.search_dirs:
                console.print(f"[yellow]Searched in: {', '.join(str(d) for d in self.search_dirs)}[/yellow]")
            return None
        
        file_path = resolved_path
        suffix = file_path.suffix.lower()
        
        # Route to appropriate extractor
        if suffix == '.pdf':
            return self._extract_pdf(file_path)
        elif suffix in ['.txt', '.md', '.markdown']:
            return self._extract_text_file(file_path)
        else:
            console.print(f"[red]Error: Unsupported file format: {suffix}[/red]")
            console.print(f"[yellow]Supported formats: .pdf, .txt, .md[/yellow]")
            return None
    
    def _resolve_path(self, file_path: str | Path) -> Optional[Path]:
        """
        Resolve file path with smart searching in configured directories.
        
        Args:
            file_path: Original file path
            
        Returns:
            Resolved Path object or None if not found
        """
        file_path = Path(file_path)
        
        # If absolute path and exists, use it
        if file_path.is_absolute() and file_path.exists():
            return file_path
        
        # If relative path exists from current directory
        if file_path.exists():
            return file_path
        
        # Search in configured directories
        for search_dir in self.search_dirs:
            candidate = search_dir / file_path.name
            if candidate.exists():
                if self.verbose:
                    console.print(f"[cyan]Found file in:[/cyan] {search_dir}")
                return candidate
        
        return None
    
    def _extract_pdf(self, pdf_path: Path) -> Optional[str]:
        """Extract text from PDF file using PyMuPDF."""
        try:
            if self.verbose:
                console.print(f"[cyan]Loading PDF:[/cyan] {pdf_path.name}")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True
            ) as progress:
                task = progress.add_task("Extracting text from PDF...", total=None)
                
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
    
    def _extract_text_file(self, file_path: Path) -> Optional[str]:
        """Extract text from TXT or MD file."""
        try:
            if self.verbose:
                console.print(f"[cyan]Loading text file:[/cyan] {file_path.name}")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True
            ) as progress:
                task = progress.add_task("Reading text file...", total=None)
                
                # Read with UTF-8 encoding
                text = file_path.read_text(encoding='utf-8')
                progress.update(task, completed=True)
            
            # Clean up the text
            text = self._clean_text(text)
            
            if self.verbose:
                word_count = len(text.split())
                char_count = len(text)
                console.print(f"[green]✓ Loaded {word_count:,} words, {char_count:,} characters[/green]")
            
            return text
            
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                text = file_path.read_text(encoding='latin-1')
                text = self._clean_text(text)
                if self.verbose:
                    console.print(f"[yellow]⚠ Used latin-1 encoding[/yellow]")
                return text
            except Exception as e:
                console.print(f"[red]Error reading text file: {str(e)}[/red]")
                return None
        except Exception as e:
            console.print(f"[red]Error reading text file: {str(e)}[/red]")
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
    
    def extract_with_metadata(self, file_path: str | Path) -> Optional[dict]:
        """
        Extract text along with document metadata.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Dictionary containing text and metadata
        """
        resolved_path = self._resolve_path(file_path)
        if not resolved_path:
            return None
        
        text = self.extract_text(resolved_path)
        
        if text is None:
            return None
        
        metadata = {
            'filename': resolved_path.name,
            'format': resolved_path.suffix.lower(),
            'text': text,
            'word_count': len(text.split()),
            'char_count': len(text),
            'file_size_kb': resolved_path.stat().st_size / 1024
        }
        
        # Add PDF-specific metadata if applicable
        if resolved_path.suffix.lower() == '.pdf':
            try:
                doc = fitz.open(resolved_path)
                metadata.update({
                    'page_count': len(doc),
                    'title': doc.metadata.get('title', 'Unknown'),
                    'author': doc.metadata.get('author', 'Unknown'),
                    'subject': doc.metadata.get('subject', ''),
                })
                doc.close()
            except Exception:
                pass  # Silently fail for metadata
        
        return metadata


# Backward compatibility alias
PDFLoader = DocumentLoader


# Standalone testing functionality
if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    if len(sys.argv) < 2:
        console.print("[yellow]Usage: python document_loader.py <path_to_file>[/yellow]")
        console.print("[yellow]Supported formats: .pdf, .txt, .md[/yellow]")
        console.print("[yellow]Example: python document_loader.py policy.pdf[/yellow]")
        sys.exit(1)
    
    # Get search directories from config if available
    try:
        import config
        search_dirs = [config.INPUT_DIR, config.REFERENCE_DIR]
    except:
        search_dirs = [Path.cwd()]
    
    loader = DocumentLoader(verbose=True, search_dirs=search_dirs)
    file_path = sys.argv[1]
    
    console.print(f"\n[bold]Testing Document Loader[/bold]\n")
    result = loader.extract_with_metadata(file_path)
    
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
