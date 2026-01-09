"""
Configuration management for the Code Documentation Generator.

Loads environment variables and provides typed configuration objects.
"""
import os
from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class AnthropicConfig(BaseModel):
    """Anthropic API configuration."""
    
    api_key: str = Field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))
    model: str = Field(default_factory=lambda: os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022"))
    max_tokens: int = Field(default_factory=lambda: int(os.getenv("CLAUDE_MAX_TOKENS", "8192")))
    temperature: float = Field(default_factory=lambda: float(os.getenv("CLAUDE_TEMPERATURE", "0.3")))
    
    class Config:
        frozen = True


class CostConfig(BaseModel):
    """Cost tracking configuration."""
    
    cost_per_1m_input_tokens: float = Field(
        default_factory=lambda: float(os.getenv("COST_PER_1M_INPUT_TOKENS", "3.00"))
    )
    cost_per_1m_output_tokens: float = Field(
        default_factory=lambda: float(os.getenv("COST_PER_1M_OUTPUT_TOKENS", "15.00"))
    )
    enable_tracking: bool = Field(
        default_factory=lambda: os.getenv("ENABLE_COST_TRACKING", "true").lower() == "true"
    )
    
    class Config:
        frozen = True


class AWSConfig(BaseModel):
    """AWS configuration."""
    
    region: str = Field(default_factory=lambda: os.getenv("AWS_REGION", "us-east-1"))
    account_id: Optional[str] = Field(default_factory=lambda: os.getenv("AWS_ACCOUNT_ID"))
    
    # S3
    s3_bucket_name: str = Field(default_factory=lambda: os.getenv("S3_BUCKET_NAME", "intelligent-code-docs"))
    s3_prefix: str = Field(default_factory=lambda: os.getenv("S3_PREFIX", "documentation/"))
    
    # DynamoDB
    dynamodb_table_name: str = Field(default_factory=lambda: os.getenv("DYNAMODB_TABLE_NAME", "code-doc-cache"))
    
    class Config:
        frozen = True


class ChunkingConfig(BaseModel):
    """Code chunking configuration."""
    
    max_chunk_size: int = Field(default_factory=lambda: int(os.getenv("MAX_CHUNK_SIZE", "2000")))
    chunk_overlap: int = Field(default_factory=lambda: int(os.getenv("CHUNK_OVERLAP", "100")))
    
    class Config:
        frozen = True


class RateLimitConfig(BaseModel):
    """Rate limiting configuration."""
    
    max_requests_per_minute: int = Field(
        default_factory=lambda: int(os.getenv("MAX_REQUESTS_PER_MINUTE", "50"))
    )
    retry_max_attempts: int = Field(
        default_factory=lambda: int(os.getenv("RETRY_MAX_ATTEMPTS", "3"))
    )
    retry_initial_delay: float = Field(
        default_factory=lambda: float(os.getenv("RETRY_INITIAL_DELAY", "1"))
    )
    retry_max_delay: float = Field(
        default_factory=lambda: float(os.getenv("RETRY_MAX_DELAY", "60"))
    )
    
    class Config:
        frozen = True


class CachingConfig(BaseModel):
    """Caching configuration."""
    
    enable_caching: bool = Field(
        default_factory=lambda: os.getenv("ENABLE_CACHING", "true").lower() == "true"
    )
    cache_ttl_hours: int = Field(default_factory=lambda: int(os.getenv("CACHE_TTL_HOURS", "24")))
    
    class Config:
        frozen = True


class MonitoringConfig(BaseModel):
    """Monitoring and logging configuration."""
    
    enable_xray: bool = Field(
        default_factory=lambda: os.getenv("ENABLE_XRAY", "false").lower() == "true"
    )
    log_level: str = Field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    
    class Config:
        frozen = True


class AppConfig(BaseModel):
    """Main application configuration."""
    
    anthropic: AnthropicConfig = Field(default_factory=AnthropicConfig)
    cost: CostConfig = Field(default_factory=CostConfig)
    aws: AWSConfig = Field(default_factory=AWSConfig)
    chunking: ChunkingConfig = Field(default_factory=ChunkingConfig)
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig)
    caching: CachingConfig = Field(default_factory=CachingConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    
    local_mode: bool = Field(
        default_factory=lambda: os.getenv("LOCAL_MODE", "true").lower() == "true"
    )
    debug: bool = Field(
        default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true"
    )
    
    class Config:
        frozen = True


# Singleton config instance
config = AppConfig()
