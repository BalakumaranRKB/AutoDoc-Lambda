"""
Chunk Processor - Handles parallel processing and merging of chunks

Processes multiple code chunks in parallel and intelligently merges
the documentation results.
"""
import logging
import hashlib
from typing import List, Dict, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from decimal import Decimal
from chunking import CodeChunk
from claude_client import ClaudeClient
from cache_manager import CacheManager

logger = logging.getLogger(__name__)


def decimal_to_float(obj):
    """Convert Decimal to float for JSON serialization."""
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: decimal_to_float(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [decimal_to_float(v) for v in obj]
    return obj


class ChunkProcessor:
    """
    Processes code chunks in parallel and merges results.
    
    Features:
    - Parallel API calls for chunks
    - Individual chunk caching
    - Intelligent documentation merging
    - Progress tracking
    """
    
    def __init__(
        self,
        claude_client: ClaudeClient,
        cache_manager: CacheManager,
        max_workers: int = 5
    ):
        """
        Initialize chunk processor.
        
        Args:
            claude_client: Claude API client
            cache_manager: Cache manager for chunk caching
            max_workers: Maximum parallel workers (default: 5)
        """
        self.claude_client = claude_client
        self.cache_manager = cache_manager
        self.max_workers = max_workers
    
    def process_chunks(
        self,
        file_path: str,
        chunks: List[CodeChunk]
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Process all chunks in parallel and merge results.
        
        Args:
            file_path: Path to the original file
            chunks: List of code chunks
            
        Returns:
            Tuple of (merged_documentation, combined_metrics)
        """
        logger.info(f"Processing {len(chunks)} chunks with {self.max_workers} workers")
        
        chunk_results = []
        total_cost = 0.0
        total_tokens = 0
        cache_hits = 0
        cache_misses = 0
        
        # Process chunks in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all chunk processing tasks
            future_to_chunk = {
                executor.submit(
                    self._process_single_chunk,
                    file_path,
                    chunk
                ): chunk
                for chunk in chunks
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_chunk):
                chunk = future_to_chunk[future]
                
                try:
                    result = future.result()
                    chunk_results.append(result)
                    
                    # Track metrics
                    total_cost += result['cost']
                    total_tokens += result['tokens']
                    
                    if result['cached']:
                        cache_hits += 1
                    else:
                        cache_misses += 1
                    
                    logger.info(
                        f"Chunk {chunk.chunk_id + 1}/{len(chunks)} complete "
                        f"(cached: {result['cached']}, cost: ${result['cost']:.6f})"
                    )
                    
                except Exception as e:
                    logger.error(f"Error processing chunk {chunk.chunk_id}: {e}")
                    # Add error placeholder
                    chunk_results.append({
                        'chunk_id': chunk.chunk_id,
                        'documentation': f"<!-- Error processing chunk {chunk.chunk_id}: {str(e)} -->",
                        'cost': 0.0,
                        'tokens': 0,
                        'cached': False,
                        'error': str(e)
                    })
        
        # Sort results by chunk_id to maintain order
        chunk_results.sort(key=lambda x: x['chunk_id'])
        
        # Merge documentation
        merged_doc = self._merge_chunk_documentation(file_path, chunk_results, chunks)
        
        # Combined metrics
        metrics = {
            'total_cost': total_cost,
            'total_tokens': total_tokens,
            'total_chunks': len(chunks),
            'cache_hits': cache_hits,
            'cache_misses': cache_misses,
            'cache_hit_rate': (cache_hits / len(chunks) * 100) if chunks else 0
        }
        
        logger.info(
            f"All chunks processed. "
            f"Cost: ${total_cost:.6f}, "
            f"Cache hits: {cache_hits}/{len(chunks)}"
        )
        
        return merged_doc, metrics
    
    def _process_single_chunk(
        self,
        file_path: str,
        chunk: CodeChunk
    ) -> Dict[str, Any]:
        """
        Process a single chunk (with caching).
        
        Args:
            file_path: Original file path
            chunk: Code chunk to process
            
        Returns:
            Dictionary with documentation and metrics
        """
        # Calculate chunk hash for caching
        chunk_hash = self._calculate_chunk_hash(file_path, chunk)
        
        # Check cache
        cached = self.cache_manager.get_cached(chunk_hash)
        
        if cached:
            # Cache HIT - convert Decimals to floats
            logger.info(f"Cache HIT for chunk {chunk.chunk_id}")
            
            cached_clean = decimal_to_float(cached)
            
            return {
                'chunk_id': chunk.chunk_id,
                'documentation': cached_clean['documentation'],
                'cost': 0.0,
                'tokens': cached_clean['metadata'].get('tokens', 0),
                'cached': True
            }
        else:
            # Cache MISS - generate documentation
            logger.info(f"Cache MISS for chunk {chunk.chunk_id}, generating docs")
            
            # Build context for this chunk
            context = self._build_chunk_context(file_path, chunk)
            
            # Generate documentation
            documentation, cost_metrics = self.claude_client.generate_documentation(
                code=chunk.content,
                file_path=f"{file_path} (Chunk {chunk.chunk_id + 1})",
                analysis=None,
                context=context
            )
            
            # Save to cache
            cache_metadata = {
                'cost': cost_metrics['total_cost'],
                'tokens': cost_metrics['total_tokens'],
                'chunk_id': chunk.chunk_id,
                'chunk_lines': f"{chunk.start_line}-{chunk.end_line}"
            }
            
            self.cache_manager.save_to_cache(
                file_hash=chunk_hash,
                file_path=f"{file_path}#chunk{chunk.chunk_id}",
                documentation=documentation,
                metadata=cache_metadata,
                ttl_hours=24
            )
            
            return {
                'chunk_id': chunk.chunk_id,
                'documentation': documentation,
                'cost': cost_metrics['total_cost'],
                'tokens': cost_metrics['total_tokens'],
                'cached': False
            }
    
    def _calculate_chunk_hash(self, file_path: str, chunk: CodeChunk) -> str:
        """Calculate unique hash for a chunk (for caching)."""
        # Include file path and chunk content in hash
        hash_input = f"{file_path}::{chunk.chunk_id}::{chunk.content}"
        return hashlib.sha256(hash_input.encode('utf-8')).hexdigest()
    
    def _build_chunk_context(self, file_path: str, chunk: CodeChunk) -> str:
        """Build context string for chunk documentation."""
        context = f"""This is part of a larger file ({file_path}).

**Chunk Information:**
- Chunk {chunk.chunk_id + 1}
- Lines: {chunk.start_line}-{chunk.end_line}
- Type: {chunk.type}
- Contains: {', '.join(chunk.elements) if chunk.elements else 'code'}

Generate documentation for this specific chunk. Focus on the functions/classes present.
"""
        return context
    
    def _merge_chunk_documentation(
        self,
        file_path: str,
        chunk_results: List[Dict[str, Any]],
        chunks: List[CodeChunk]
    ) -> str:
        """
        Intelligently merge chunk documentation into cohesive docs.
        
        Args:
            file_path: Original file path
            chunk_results: List of chunk results
            chunks: Original chunks
            
        Returns:
            Merged documentation string
        """
        # Build merged documentation
        doc_parts = []
        
        # Header
        doc_parts.append(f"# Documentation: {file_path}")
        doc_parts.append("")
        doc_parts.append(f"*This file was processed in {len(chunks)} chunks for efficiency.*")
        doc_parts.append("")
        
        # Add each chunk's documentation
        for i, result in enumerate(chunk_results):
            chunk = chunks[i]
            
            # Section header
            doc_parts.append(f"## Chunk {chunk.chunk_id + 1}: Lines {chunk.start_line}-{chunk.end_line}")
            doc_parts.append("")
            
            if chunk.elements:
                doc_parts.append(f"*Contains: {', '.join(chunk.elements)}*")
                doc_parts.append("")
            
            # Add documentation (remove any redundant headers)
            chunk_doc = result['documentation']
            
            # Remove the file header if Claude added one
            lines = chunk_doc.split('\n')
            if lines and lines[0].startswith('# '):
                lines = lines[1:]
            
            doc_parts.append('\n'.join(lines).strip())
            doc_parts.append("")
            doc_parts.append("---")
            doc_parts.append("")
        
        return '\n'.join(doc_parts)
