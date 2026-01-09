"""
Configuration for Phase 3 Production.
"""
import os


class Config:
    """Configuration class."""
    
    def __init__(self):
        # Anthropic API
        self.anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        self.claude_model = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-20250514")
        self.max_tokens = int(os.environ.get("MAX_TOKENS", "4096"))
        self.temperature = float(os.environ.get("TEMPERATURE", "0.0"))
        
        # Cost tracking
        self.cost_per_1m_input_tokens = float(os.environ.get("COST_PER_1M_INPUT_TOKENS", "3.00"))
        self.cost_per_1m_output_tokens = float(os.environ.get("COST_PER_1M_OUTPUT_TOKENS", "15.00"))
        
        # Caching
        self.cache_table_name = os.environ.get("CACHE_TABLE_NAME", "doc-cache-dev")
        self.cache_ttl_hours = int(os.environ.get("CACHE_TTL_HOURS", "24"))
        
        # Logging
        self.log_level = os.environ.get("LOG_LEVEL", "INFO")


# Global config instance
config = Config()
