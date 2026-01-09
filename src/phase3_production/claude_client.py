"""
Direct Claude API client with retry logic
This avoids all pydantic dependencies and handles transient failures
"""
import json
import os
import logging
from typing import Dict, Any, Tuple
import httpx
from models import create_cost_metrics
from retry_logic import with_retry, RetryConfig

logger = logging.getLogger(__name__)


class ClaudeClient:
    """Direct HTTP client for Claude API with retry logic."""
    
    def __init__(self, api_key: str = None):
        """Initialize Claude client."""
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        if not self.api_key:
            raise ValueError("Anthropic API key is required")
        
        self.api_url = "https://api.anthropic.com/v1/messages"
        self.model = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-20250514")
        self.max_tokens = int(os.environ.get("MAX_TOKENS", "4096"))
        self.temperature = float(os.environ.get("TEMPERATURE", "0.0"))
        
        # Retry configuration
        self.retry_config = RetryConfig(
            max_attempts=5,
            initial_delay=1.0,
            exponential_base=2.0,
            max_delay=60.0,
            retryable_status_codes=(429, 503, 502, 504)
        )
        
        logger.info(f"Initialized Claude client with model: {self.model}")
        logger.info(f"Retry config: max_attempts={self.retry_config.max_attempts}")
    
    def generate_documentation(
        self, 
        code: str, 
        file_path: str,
        analysis: Dict = None,
        context: str = None
    ) -> Tuple[str, Dict[str, Any]]:
        """Generate documentation using direct API call with retry logic."""
        logger.info(f"Generating documentation for {file_path}")
        
        # Use retry decorator
        @with_retry(self.retry_config)
        def make_api_call():
            return self._call_claude_api(code, file_path, context)
        
        try:
            documentation, usage = make_api_call()
            
            # Calculate cost
            cost_metrics = self._calculate_cost(
                usage['input_tokens'], 
                usage['output_tokens']
            )
            
            logger.info(
                f"Generated documentation. "
                f"Tokens: {cost_metrics['total_tokens']}, "
                f"Cost: ${cost_metrics['total_cost']:.6f}"
            )
            
            return documentation, cost_metrics
            
        except Exception as e:
            logger.error(f"Failed to generate documentation after retries: {e}")
            raise
    
    def _call_claude_api(self, code: str, file_path: str, context: str = None) -> Tuple[str, Dict]:
        """
        Make the actual API call to Claude.
        
        This method is wrapped by retry logic.
        """
        # Build prompt
        prompt = self._build_prompt(code, file_path, context)
        
        # Build request
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        # Make HTTP request
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                self.api_url,
                headers=headers,
                json=payload
            )
            
            # This will raise an exception for 4xx/5xx status codes
            # The retry logic will catch retryable ones (429, 503, etc.)
            response.raise_for_status()
            
            data = response.json()
        
        # Extract documentation and usage
        documentation = data['content'][0]['text']
        usage = {
            'input_tokens': data['usage']['input_tokens'],
            'output_tokens': data['usage']['output_tokens']
        }
        
        return documentation, usage
    
    def _build_prompt(self, code: str, file_path: str, context: str = None) -> str:
        """Build documentation prompt."""
        prompt = f"""You are an expert technical writer. Generate comprehensive documentation for this Python code.

**File:** {file_path}

**Code:**
```python
{code}
```

Generate documentation with:
1. File overview
2. Functions/classes with parameters, returns, and examples
3. Dependencies
4. Code quality notes

Format in clear Markdown."""
        
        if context:
            prompt += f"\n\n**Context:** {context}"
        
        return prompt
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> Dict[str, Any]:
        """Calculate cost metrics."""
        input_cost_per_1m = float(os.environ.get("COST_PER_1M_INPUT_TOKENS", "3.00"))
        output_cost_per_1m = float(os.environ.get("COST_PER_1M_OUTPUT_TOKENS", "15.00"))
        
        input_cost = (input_tokens / 1_000_000) * input_cost_per_1m
        output_cost = (output_tokens / 1_000_000) * output_cost_per_1m
        
        return create_cost_metrics(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_cost=input_cost,
            output_cost=output_cost
        )
