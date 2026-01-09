"""
AWS Lambda handler for Phase 1 POC - with debug logging.
"""
import json
import logging
import time
from typing import Dict, Any
import uuid
import traceback
from datetime import datetime

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try imports and log each one
try:
    logger.info("Importing code_analyzer...")
    from code_analyzer import PythonCodeAnalyzer
    logger.info("✓ code_analyzer imported")
except Exception as e:
    logger.error(f"✗ Failed to import code_analyzer: {e}")
    raise

try:
    logger.info("Importing claude_client...")
    from claude_client import ClaudeClient
    logger.info("✓ claude_client imported")
except Exception as e:
    logger.error(f"✗ Failed to import claude_client: {e}")
    raise

try:
    logger.info("Importing cost_tracker...")
    from cost_tracker import CostTracker
    logger.info("✓ cost_tracker imported")
except Exception as e:
    logger.error(f"✗ Failed to import cost_tracker: {e}")
    raise

try:
    logger.info("Importing models...")
    from models import DocumentationResult, ProcessingStatus
    logger.info("✓ models imported")
except Exception as e:
    logger.error(f"✗ Failed to import models: {e}")
    raise


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime objects."""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for documentation generation.
    """
    logger.info("="*80)
    logger.info("Lambda function invoked")
    logger.info("="*80)
    
    start_time = time.time()
    
    try:
        # Extract request data
        logger.info("Parsing request body...")
        body = event.get('body', '{}')
        if isinstance(body, str):
            body = json.loads(body)
        
        file_path = body.get('file_path')
        file_content = body.get('file_content')
        
        logger.info(f"file_path: {file_path}")
        logger.info(f"file_content length: {len(file_content) if file_content else 0}")
        
        if not file_path or not file_content:
            logger.warning("Missing required fields")
            return create_error_response(
                "Missing required fields: file_path and file_content",
                400
            )
        
        # Validate file extension
        if not file_path.endswith('.py'):
            logger.warning(f"Invalid file type: {file_path}")
            return create_error_response(
                "Only Python files (.py) are supported in this version",
                400
            )
        
        # Generate documentation
        logger.info("Calling generate_documentation...")
        result = generate_documentation(file_path, file_content)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Convert to dict and add processing time
        result_dict = result.model_dump()
        result_dict['processing_time_seconds'] = processing_time
        
        # Convert datetime objects to ISO format strings
        if 'timestamp' in result_dict and isinstance(result_dict['timestamp'], datetime):
            result_dict['timestamp'] = result_dict['timestamp'].isoformat()
        
        # Handle nested datetime in analysis if present
        if result_dict.get('analysis'):
            # Analysis is already serialized by Pydantic, but double-check
            pass
        
        logger.info(f"Documentation generated successfully in {processing_time:.2f}s")
        logger.info(f"Cost: ${result_dict['total_cost']:.4f}")
        logger.info(f"Tokens: {result_dict['total_tokens']}")
        
        # Use custom encoder for datetime serialization
        response_body = json.dumps({
            "success": True,
            "data": result_dict,
            "message": "Documentation generated successfully"
        }, cls=DateTimeEncoder)
        
        response = {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": response_body
        }
        
        logger.info("Returning success response")
        return response
        
    except Exception as e:
        logger.error("="*80)
        logger.error(f"ERROR in lambda_handler: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error("Full traceback:")
        logger.error(traceback.format_exc())
        logger.error("="*80)
        return create_error_response(str(e), 500)


def generate_documentation(file_path: str, file_content: str) -> DocumentationResult:
    """Generate documentation for a single file."""
    request_id = str(uuid.uuid4())
    logger.info(f"Processing request {request_id} for {file_path}")
    
    try:
        # Initialize components
        logger.info("Initializing PythonCodeAnalyzer...")
        analyzer = PythonCodeAnalyzer()
        
        logger.info("Initializing ClaudeClient...")
        claude_client = ClaudeClient()
        
        logger.info("Initializing CostTracker...")
        cost_tracker = CostTracker()
        
        # Analyze the code
        logger.info("Analyzing code...")
        analysis = analyzer.analyze_file(file_path, file_content)
        logger.info(f"Analysis complete: {len(analysis.elements)} elements found")
        
        # Generate documentation
        logger.info("Calling Claude API...")
        documentation, cost_metrics = claude_client.generate_documentation(
            code=file_content,
            file_path=file_path
        )
        logger.info(f"Claude API returned {len(documentation)} chars")
        
        # Track costs
        logger.info("Tracking costs...")
        cost_tracker.add_cost(file_path, cost_metrics)
        cost_tracker.print_summary()
        
        # Create result
        logger.info("Creating result object...")
        result = DocumentationResult(
            request_id=request_id,
            file_path=file_path,
            status=ProcessingStatus.COMPLETED,
            documentation=documentation,
            analysis=analysis,
            total_cost=cost_metrics.total_cost,
            total_tokens=cost_metrics.total_tokens,
            cached=False
        )
        
        logger.info("Documentation generation complete")
        return result
        
    except Exception as e:
        logger.error(f"Error in generate_documentation: {str(e)}")
        logger.error(traceback.format_exc())
        return DocumentationResult(
            request_id=request_id,
            file_path=file_path,
            status=ProcessingStatus.FAILED,
            error_message=str(e)
        )


def create_error_response(message: str, status_code: int = 500) -> Dict[str, Any]:
    """Create an error response."""
    logger.error(f"Creating error response: {status_code} - {message}")
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps({
            "success": False,
            "error": message
        })
    }
