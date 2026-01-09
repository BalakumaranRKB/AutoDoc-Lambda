"""
Python code analyzer using AST.

Parses Python source code and extracts structural information.
"""
import ast
import logging
from typing import List, Optional
from models import CodeElement, FileAnalysis, FileType
from utils import count_lines


logger = logging.getLogger(__name__)


class PythonCodeAnalyzer:
    """Analyzes Python source code structure."""
    
    def __init__(self):
        """Initialize the analyzer."""
        pass
    
    def analyze_file(self, file_path: str, content: str) -> FileAnalysis:
        """
        Analyze a Python file and extract structural information.
        
        Args:
            file_path: Path to the file
            content: File content as string
            
        Returns:
            FileAnalysis object with extracted information
        """
        logger.info(f"Analyzing file: {file_path}")
        
        # Count lines
        line_counts = count_lines(content)
        
        # Parse AST
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            logger.error(f"Syntax error in {file_path}: {e}")
            return FileAnalysis(
                file_path=file_path,
                file_type=FileType.PYTHON,
                total_lines=line_counts["total"],
                code_lines=line_counts["code"],
                comment_lines=line_counts["comment"],
                blank_lines=line_counts["blank"],
                elements=[],
                imports=[]
            )
        
        # Extract elements and imports
        elements = self._extract_elements(tree)
        imports = self._extract_imports(tree)
        
        return FileAnalysis(
            file_path=file_path,
            file_type=FileType.PYTHON,
            total_lines=line_counts["total"],
            code_lines=line_counts["code"],
            comment_lines=line_counts["comment"],
            blank_lines=line_counts["blank"],
            elements=elements,
            imports=imports
        )
    
    def _extract_elements(self, tree: ast.AST) -> List[CodeElement]:
        """
        Extract code elements (functions, classes, methods) from AST.
        
        Args:
            tree: AST tree
            
        Returns:
            List of CodeElement objects
        """
        elements = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                element = self._extract_function(node)
                elements.append(element)
            elif isinstance(node, ast.ClassDef):
                element = self._extract_class(node)
                elements.append(element)
        
        return elements
    
    def _extract_function(self, node: ast.FunctionDef) -> CodeElement:
        """
        Extract information from a function definition.
        
        Args:
            node: AST FunctionDef node
            
        Returns:
            CodeElement object
        """
        # Extract docstring
        docstring = ast.get_docstring(node)
        
        # Extract parameters
        parameters = [arg.arg for arg in node.args.args]
        
        # Extract return type if available
        return_type = None
        if node.returns:
            return_type = ast.unparse(node.returns) if hasattr(ast, 'unparse') else str(node.returns)
        
        return CodeElement(
            name=node.name,
            type="function",
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            docstring=docstring,
            parameters=parameters,
            return_type=return_type
        )
    
    def _extract_class(self, node: ast.ClassDef) -> CodeElement:
        """
        Extract information from a class definition.
        
        Args:
            node: AST ClassDef node
            
        Returns:
            CodeElement object
        """
        # Extract docstring
        docstring = ast.get_docstring(node)
        
        # Extract base classes
        bases = [ast.unparse(base) if hasattr(ast, 'unparse') else str(base) 
                for base in node.bases]
        
        return CodeElement(
            name=node.name,
            type="class",
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            docstring=docstring,
            parameters=bases  # Using parameters field to store base classes
        )
    
    def _extract_imports(self, tree: ast.AST) -> List[str]:
        """
        Extract import statements from AST.
        
        Args:
            tree: AST tree
            
        Returns:
            List of import strings
        """
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(f"import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"from {module} import {alias.name}")
        
        return imports
    
    def extract_code_snippet(self, content: str, start_line: int, end_line: int) -> str:
        """
        Extract a snippet of code from content.
        
        Args:
            content: Full file content
            start_line: Starting line (1-indexed)
            end_line: Ending line (1-indexed)
            
        Returns:
            Code snippet as string
        """
        lines = content.split('\n')
        # Convert to 0-indexed
        start_idx = max(0, start_line - 1)
        end_idx = min(len(lines), end_line)
        
        snippet = '\n'.join(lines[start_idx:end_idx])
        return snippet
