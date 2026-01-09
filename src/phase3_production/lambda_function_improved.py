"""
Production Lambda Function - Phase 3 IMPROVED
- Reduced chunk size (1000 lines) for faster processing
- Stores source code alongside documentation in cache
"""
import json
import os
import logging
from datetime import datetime
from typing import Dict, Any
from decimal import Decimal

# Local imports
from cache_manager import CacheManager
from code_analyzer import PythonCodeAnalyzer
from claude_client import ClaudeClient
from cost_tracker import CostTracker
from models import create_documentation_result
from config import Config
from chunking import IntelligentChunker
from chunk_processor import ChunkProcessor

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize components
config = Config()
cache_manager = CacheManager(
    table_name=os.environ.get('CACHE_TABLE_NAME'),
    region=os.environ.get('AWS_REGION', 'us-east-1')
)
analyzer = PythonCodeAnalyzer()
claude_client = ClaudeClient(api_key=os.environ['ANTHROPIC_API_KEY'])
cost_tracker = CostTracker()

# Initialize chunking components - IMPROVED SETTINGS
chunker = IntelligentChunker(
    max_chunk_lines=1000,    # ← REDUCED from 2000 (faster processing)
    min_chunk_lines=300,     # ← REDUCED from 500
    overlap_lines=50         # Keep same for context
)
chunk_processor = ChunkProcessor(
    claude_client=claude_client,
    cache_manager=cache_manager,
    max_workers=5,
    store_source_code=True   # ← NEW: Enable source code storage
)


def decimal_to_float(obj):
    """Convert Decimal to float for JSON serialization."""
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: decimal_to_float(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [decimal_to_float(v) for v in obj]
    return obj


def lambda_handler(event, context):
    """Main Lambda handler with improved chunking and source code storage."""
    logger.info(f"Request received: {context.aws_request_id}")
    
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        file_path = body.get('file_path')
        file_content = body.get('file_content')
        
        # Validate inputs
        if not file_path or not file_content:
            return error_response("Missing file_path or file_content", 400)
        
        if not file_path.endswith('.py'):
            return error_response("Only Python files (.py) supported", 400)
        
        # Check if chunking is needed (now 1000-line threshold)
        needs_chunking = chunker.should_chunk(file_content)
        
        if needs_chunking:
            return handle_large_file(context.aws_request_id, file_path, file_content)
        else:
            return handle_small_file(context.aws_request_id, file_path, file_content)
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return error_response(str(e), 500)


def handle_small_file(request_id: str, file_path: str, file_content: str) -> Dict:
    """Handle small files with source code storage."""
    logger.info(f"Processing small file: {file_path}")
    
    file_hash = cache_manager.calculate_hash(file_content)
    cached = cache_manager.get_cached(file_hash)
    
    if cached:
        # CACHE HIT
        logger.info("Cache HIT - returning cached documentation")
        cached_clean = decimal_to_float(cached)
        
        result = create_documentation_result(
            request_id=request_id,
            file_path=file_path,
            documentation=cached_clean['documentation'],
            total_cost=0.0,
            total_tokens=cached_clean['metadata'].get('tokens', 0),
            processing_time=0.1,
            cached=True,
            cache_key=file_hash
        )
        
        # Include source code in response if available
        if 'source_code' in cached_clean:
            result['source_code'] = cached_clean['source_code']
        
        return success_response(result)
    
    else:
        # CACHE MISS
        logger.info("Cache MISS - generating documentation")
        start_time = datetime.utcnow()
        
        analysis = analyzer.analyze_file(file_path, file_content)
        documentation, cost_metrics = claude_client.generate_documentation(
            code=file_content,
            file_path=file_path,
            analysis=analysis
        )
        
        cost_tracker.add_cost(file_path, cost_metrics)
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        result = create_documentation_result(
            request_id=request_id,
            file_path=file_path,
            documentation=documentation,
            total_cost=cost_metrics['total_cost'],
            total_tokens=cost_metrics['total_tokens'],
            processing_time=processing_time,
            cached=False,
            cache_key=file_hash
        )
        
        # Save to cache WITH source code
        cache_metadata = {
            'cost': cost_metrics['total_cost'],
            'tokens': cost_metrics['total_tokens'],
            'analysis': analysis,
            'processing_time': processing_time
        }
        
        cache_manager.save_to_cache(
            file_hash=file_hash,
            file_path=file_path,
            documentation=documentation,
            metadata=cache_metadata,
            source_code=file_content,    # ← NEW: Store source code
            store_source=True,            # ← NEW: Enable storage
            ttl_hours=24
        )
        
        return success_response(result)


def handle_large_file(request_id: str, file_path: str, file_content: str) -> Dict:
    """Handle large files with chunking (improved chunk size)."""
    logger.info(f"Processing LARGE file with chunking: {file_path}")
    
    start_time = datetime.utcnow()
    
    # Create chunks (now 1000-line max)
    chunks = chunker.chunk_file(file_path, file_content)
    chunk_summary = chunker.get_chunk_summary(chunks)
    
    logger.info(f"File split into {len(chunks)} chunks (improved chunking)")
    
    # Process chunks in parallel
    merged_documentation, chunk_metrics = chunk_processor.process_chunks(
        file_path, chunks
    )
    
    processing_time = (datetime.utcnow() - start_time).total_seconds()
    
    result = {
        'request_id': request_id,
        'file_path': file_path,
        'status': 'completed',
        'documentation': merged_documentation,
        'total_cost': chunk_metrics['total_cost'],
        'total_tokens': chunk_metrics['total_tokens'],
        'processing_time_seconds': processing_time,
        'chunked': True,
        'chunking_info': {
            'total_chunks': len(chunks),
            'cache_hits': chunk_metrics['cache_hits'],
            'cache_misses': chunk_metrics['cache_misses'],
            'cache_hit_rate': chunk_metrics['cache_hit_rate'],
            'chunk_summary': chunk_summary,
            'chunking_strategy': 'AST-based (intelligent)'  # ← NEW: Document strategy
        },
        'timestamp': datetime.utcnow().isoformat()
    }
    
    logger.info(
        f"Large file processed with improved chunking. "
        f"Chunks: {len(chunks)}, "
        f"Max chunk size: 1000 lines, "
        f"Cache hits: {chunk_metrics['cache_hits']}/{len(chunks)}, "
        f"Cost: ${chunk_metrics['total_cost']:.6f}"
    )
    
    return success_response(result)


def success_response(data: Dict[str, Any]) -> Dict:
    """Build success response."""
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'success': True,
            'data': data,
            'message': 'Documentation generated successfully'
        })
    }


def error_response(message: str, status_code: int) -> Dict:
    """Build error response."""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'success': False,
            'error': message
        })
    }
