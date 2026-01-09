"""
Data models for the Code Documentation Generator.

Uses Pydantic for data validation and serialization.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class ProcessingStatus(str, Enum):
    """Status of documentation generation."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CACHED = "cached"


class FileType(str, Enum):
    """Supported file types."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    GO = "go"
    UNKNOWN = "unknown"


class CodeElement(BaseModel):
    """Represents a code element (function, class, method)."""
    
    name: str
    type: str  # "function", "class", "method"
    line_start: int
    line_end: int
    docstring: Optional[str] = None
    parameters: List[str] = Field(default_factory=list)
    return_type: Optional[str] = None
    complexity: Optional[int] = None
    
    class Config:
        frozen = True


class FileAnalysis(BaseModel):
    """Analysis result for a single file."""
    
    file_path: str
    file_type: FileType
    total_lines: int
    code_lines: int
    comment_lines: int
    blank_lines: int
    elements: List[CodeElement] = Field(default_factory=list)
    imports: List[str] = Field(default_factory=list)
    
    class Config:
        frozen = True


class DocumentationChunk(BaseModel):
    """A chunk of code with its documentation."""
    
    chunk_id: str
    file_path: str
    start_line: int
    end_line: int
    code_content: str
    documentation: str
    tokens_used: int
    cost: float
    
    class Config:
        frozen = True


class CostMetrics(BaseModel):
    """Cost tracking for a single API call."""
    
    input_tokens: int
    output_tokens: int
    total_tokens: int
    input_cost: float
    output_cost: float
    total_cost: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        frozen = True


class DocumentationResult(BaseModel):
    """Final documentation result for a file or repository."""
    
    request_id: str
    file_path: Optional[str] = None
    repository_name: Optional[str] = None
    status: ProcessingStatus
    documentation: str = ""
    chunks: List[DocumentationChunk] = Field(default_factory=list)
    analysis: Optional[FileAnalysis] = None
    total_cost: float = 0.0
    total_tokens: int = 0
    processing_time_seconds: float = 0.0
    error_message: Optional[str] = None
    cached: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        use_enum_values = True


class RepositoryRequest(BaseModel):
    """Request to document a repository."""
    
    repository_url: Optional[str] = None
    files: List[str] = Field(default_factory=list)
    file_contents: Dict[str, str] = Field(default_factory=dict)
    max_files: Optional[int] = None
    include_patterns: List[str] = Field(default_factory=lambda: ["*.py"])
    exclude_patterns: List[str] = Field(default_factory=lambda: [
        "*.pyc", "__pycache__", ".git", "venv", "node_modules"
    ])
    
    class Config:
        frozen = True


class CacheEntry(BaseModel):
    """Cache entry for storing documentation results."""
    
    file_hash: str
    file_path: str
    documentation: str
    cost: float
    tokens: int
    created_at: datetime
    ttl: int  # Time to live in seconds
    
    class Config:
        use_enum_values = True


class APIResponse(BaseModel):
    """Standard API response format."""
    
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    cost_metrics: Optional[CostMetrics] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        use_enum_values = True
