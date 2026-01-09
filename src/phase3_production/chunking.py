"""
Intelligent Code Chunking for Large Files

Splits large Python files into logical chunks based on:
- Function definitions
- Class definitions
- Top-level code blocks

Ensures chunks are meaningful and can be documented independently.
"""
import ast
import logging
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CodeChunk:
    """Represents a logical chunk of code."""
    chunk_id: int
    start_line: int
    end_line: int
    content: str
    type: str  # 'function', 'class', 'module_level', 'mixed'
    elements: List[str]  # Names of functions/classes in this chunk
    
    def size(self) -> int:
        """Get number of lines in chunk."""
        return self.end_line - self.start_line + 1


class IntelligentChunker:
    """
    Intelligently splits Python code into processable chunks.
    
    Strategy:
    1. Parse AST to find function/class boundaries
    2. Group related code together
    3. Ensure chunks are under max_lines threshold
    4. Keep logical units intact (don't split mid-function)
    """
    
    def __init__(
        self, 
        max_chunk_lines: int = 2000,
        min_chunk_lines: int = 500,
        overlap_lines: int = 50
    ):
        """
        Initialize chunker.
        
        Args:
            max_chunk_lines: Maximum lines per chunk (default: 2000)
            min_chunk_lines: Minimum lines per chunk (default: 500)
            overlap_lines: Lines to overlap between chunks for context (default: 50)
        """
        self.max_chunk_lines = max_chunk_lines
        self.min_chunk_lines = min_chunk_lines
        self.overlap_lines = overlap_lines
    
    def should_chunk(self, content: str) -> bool:
        """
        Determine if file needs chunking.
        
        Args:
            content: File content
            
        Returns:
            True if file should be chunked, False otherwise
        """
        lines = content.split('\n')
        total_lines = len(lines)
        
        # Chunk if file is larger than max_chunk_lines
        should_chunk = total_lines > self.max_chunk_lines
        
        if should_chunk:
            logger.info(f"File has {total_lines} lines, will chunk (threshold: {self.max_chunk_lines})")
        else:
            logger.info(f"File has {total_lines} lines, no chunking needed")
        
        return should_chunk
    
    def chunk_file(self, file_path: str, content: str) -> List[CodeChunk]:
        """
        Split file into logical chunks.
        
        Args:
            file_path: Path to the file
            content: File content
            
        Returns:
            List of CodeChunk objects
        """
        logger.info(f"Chunking file: {file_path}")
        
        lines = content.split('\n')
        total_lines = len(lines)
        
        # Try to parse AST
        try:
            tree = ast.parse(content)
            chunks = self._chunk_by_ast(tree, lines, file_path)
        except SyntaxError as e:
            logger.warning(f"Syntax error, falling back to line-based chunking: {e}")
            chunks = self._chunk_by_lines(lines, file_path)
        
        logger.info(f"Created {len(chunks)} chunks for {total_lines} lines")
        
        return chunks
    
    def _chunk_by_ast(self, tree: ast.AST, lines: List[str], file_path: str) -> List[CodeChunk]:
        """
        Chunk file based on AST structure (intelligent).
        
        Keeps functions and classes intact.
        """
        chunks = []
        
        # Extract top-level elements (functions, classes)
        elements = []
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                elements.append({
                    'type': 'function' if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) else 'class',
                    'name': node.name,
                    'start_line': node.lineno,
                    'end_line': node.end_lineno or node.lineno
                })
        
        # Sort by start line
        elements.sort(key=lambda x: x['start_line'])
        
        if not elements:
            # No functions/classes, chunk by lines
            logger.info("No functions/classes found, using line-based chunking")
            return self._chunk_by_lines(lines, file_path)
        
        # Group elements into chunks
        current_chunk_elements = []
        current_start = 1
        chunk_id = 0
        
        for elem in elements:
            # Check if adding this element would exceed max_chunk_lines
            potential_end = elem['end_line']
            potential_size = potential_end - current_start + 1
            
            if potential_size > self.max_chunk_lines and current_chunk_elements:
                # Create chunk with current elements
                chunk_end = current_chunk_elements[-1]['end_line']
                chunk = self._create_chunk(
                    chunk_id=chunk_id,
                    start_line=current_start,
                    end_line=chunk_end,
                    lines=lines,
                    elements=current_chunk_elements,
                    file_path=file_path
                )
                chunks.append(chunk)
                chunk_id += 1
                
                # Start new chunk
                current_start = elem['start_line']
                current_chunk_elements = [elem]
            else:
                # Add element to current chunk
                current_chunk_elements.append(elem)
        
        # Create final chunk
        if current_chunk_elements:
            chunk_end = current_chunk_elements[-1]['end_line']
            chunk = self._create_chunk(
                chunk_id=chunk_id,
                start_line=current_start,
                end_line=chunk_end,
                lines=lines,
                elements=current_chunk_elements,
                file_path=file_path
            )
            chunks.append(chunk)
        
        return chunks
    
    def _chunk_by_lines(self, lines: List[str], file_path: str) -> List[CodeChunk]:
        """
        Chunk file by lines (fallback for unparseable files).
        
        Simple strategy: split every max_chunk_lines.
        """
        chunks = []
        total_lines = len(lines)
        chunk_id = 0
        
        start = 0
        while start < total_lines:
            end = min(start + self.max_chunk_lines, total_lines)
            
            chunk_content = '\n'.join(lines[start:end])
            
            chunk = CodeChunk(
                chunk_id=chunk_id,
                start_line=start + 1,  # 1-indexed
                end_line=end,
                content=chunk_content,
                type='mixed',
                elements=[]
            )
            
            chunks.append(chunk)
            chunk_id += 1
            
            # Move to next chunk (with overlap for context)
            start = end - self.overlap_lines if end < total_lines else end
        
        return chunks
    
    def _create_chunk(
        self,
        chunk_id: int,
        start_line: int,
        end_line: int,
        lines: List[str],
        elements: List[Dict],
        file_path: str
    ) -> CodeChunk:
        """Create a CodeChunk object."""
        # Extract content (0-indexed)
        chunk_lines = lines[start_line - 1:end_line]
        content = '\n'.join(chunk_lines)
        
        # Determine chunk type
        types = [e['type'] for e in elements]
        if all(t == 'function' for t in types):
            chunk_type = 'function'
        elif all(t == 'class' for t in types):
            chunk_type = 'class'
        else:
            chunk_type = 'mixed'
        
        # Get element names
        element_names = [e['name'] for e in elements]
        
        return CodeChunk(
            chunk_id=chunk_id,
            start_line=start_line,
            end_line=end_line,
            content=content,
            type=chunk_type,
            elements=element_names
        )
    
    def get_chunk_summary(self, chunks: List[CodeChunk]) -> Dict[str, Any]:
        """
        Get summary of chunking strategy.
        
        Args:
            chunks: List of chunks
            
        Returns:
            Summary dictionary
        """
        total_lines = sum(c.size() for c in chunks)
        
        return {
            'total_chunks': len(chunks),
            'total_lines': total_lines,
            'avg_chunk_size': total_lines // len(chunks) if chunks else 0,
            'min_chunk_size': min(c.size() for c in chunks) if chunks else 0,
            'max_chunk_size': max(c.size() for c in chunks) if chunks else 0,
            'chunk_details': [
                {
                    'chunk_id': c.chunk_id,
                    'lines': f"{c.start_line}-{c.end_line}",
                    'size': c.size(),
                    'type': c.type,
                    'elements': c.elements
                }
                for c in chunks
            ]
        }
