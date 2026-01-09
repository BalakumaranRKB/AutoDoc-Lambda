"""
Data models - Pydantic v1 compatible
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
    
    class Config:
        frozen = True
    
    name: str
    type: str
    line_start: int
    line_end: int
    docstring: Optional[str] = None
    parameters: List[str] = Field(default_factory=list)
    return_type: Optional[str] = None
    complexity: Optional[int] = None


class FileAnalysis(BaseModel):
    """Analysis result for a single file."""
    
    class Config:
        frozen = True
    
    file_path: str
    file_type: FileType
    total_lines: int
    code_lines: int
    comment_lines: int
    blank_lines: int
    elements: List[CodeElement] = Field(default_factory=list)
    imports: List[str] = Field(default_factory=list)


class CostMetrics(BaseModel):
    """Cost tracking for a single API call."""
    
    class Config:
        frozen = True
    
    input_tokens: int
    output_tokens: int
    total_tokens: int
    input_cost: float
    output_cost: float
    total_cost: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class DocumentationResult(BaseModel):
    """Final documentation result."""
    
    class Config:
        use_enum_values = True
    
    request_id: str
    file_path: Optional[str] = None
    repository_name: Optional[str] = None
    status: ProcessingStatus = ProcessingStatus.COMPLETED
    documentation: str = ""
    analysis: Optional[Dict] = None
    total_cost: float = 0.0
    total_tokens: int = 0
    processing_time_seconds: float = 0.0
    error_message: Optional[str] = None
    cached: bool = False
    cache_key: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
