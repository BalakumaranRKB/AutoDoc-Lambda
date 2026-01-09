"""
IMPROVED Cache Manager with Source Code Storage

Now stores source code alongside documentation for complete context.
"""
import hashlib
import time
import boto3
import os
from typing import Dict, Optional
from datetime import datetime
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def float_to_decimal(obj):
    """Convert floats to Decimal for DynamoDB."""
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: float_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [float_to_decimal(v) for v in obj]
    return obj


class CacheManager:
    """
    IMPROVED: Manages documentation cache with source code storage.
    
    Features:
    - SHA256 hash-based keys
    - 24-hour TTL auto-expiration
    - Cost tracking
    - Source code storage (NEW!)
    - Decimal conversion for DynamoDB
    """
    
    def __init__(self, table_name: str = None, region: str = None):
        """Initialize cache manager."""
        self.table_name = table_name or os.environ.get('CACHE_TABLE_NAME', 'doc-cache-dev')
        self.region = region or os.environ.get('AWS_REGION', 'us-east-1')
        
        # Initialize DynamoDB
        self.dynamodb = boto3.resource('dynamodb', region_name=self.region)
        self.table = self.dynamodb.Table(self.table_name)
        
        logger.info(f"CacheManager initialized with table: {self.table_name}")
    
    def calculate_hash(self, content: str) -> str:
        """Calculate SHA256 hash of file content."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def get_cached(self, file_hash: str) -> Optional[Dict]:
        """Retrieve cached documentation from DynamoDB."""
        try:
            response = self.table.get_item(Key={'file_hash': file_hash})
            
            if 'Item' in response:
                logger.info(f"Cache HIT for hash: {file_hash[:16]}...")
                return response['Item']
            else:
                logger.info(f"Cache MISS for hash: {file_hash[:16]}...")
                return None
                
        except Exception as e:
            logger.error(f"Error getting from cache: {str(e)}")
            return None
    
    def save_to_cache(
        self, 
        file_hash: str, 
        file_path: str,
        documentation: str,
        metadata: Dict,
        ttl_hours: int = 24,
        source_code: str = None,      # ← NEW PARAMETER
        store_source: bool = False    # ← NEW FLAG
    ) -> bool:
        """
        Save documentation to DynamoDB cache.
        
        Args:
            file_hash: SHA256 hash of the code
            file_path: Path to the file
            documentation: Generated documentation
            metadata: Cost and token metrics
            ttl_hours: Time to live in hours
            source_code: Original source code (NEW!)
            store_source: Whether to store source code (NEW!)
        """
        try:
            # Calculate TTL (Unix timestamp)
            ttl = int(time.time()) + (ttl_hours * 3600)
            
            # Convert all floats to Decimal for DynamoDB
            metadata_decimal = float_to_decimal(metadata)
            
            # Create item with IMPROVED structure
            item = {
                'file_hash': file_hash,
                'file_path': file_path,
                'documentation': documentation,
                'metadata': metadata_decimal,
                'created_at': datetime.utcnow().isoformat(),
                'ttl': ttl
            }
            
            # ← NEW: Optionally store source code
            if store_source and source_code:
                item['source_code'] = source_code
                logger.info(f"Storing source code ({len(source_code)} chars)")
            
            # Save to DynamoDB
            self.table.put_item(Item=item)
            
            logger.info(
                f"Saved to cache: {file_hash[:16]}... "
                f"(TTL: {ttl_hours}h, with_source: {store_source})"
            )
            return True
            
        except Exception as e:
            logger.error(f"Error saving to cache: {str(e)}")
            return False
    
    def check_exists(self, file_hash: str) -> bool:
        """Quick check if item exists in cache."""
        return self.get_cached(file_hash) is not None
    
    def delete_from_cache(self, file_hash: str) -> bool:
        """Delete item from cache."""
        try:
            self.table.delete_item(Key={'file_hash': file_hash})
            logger.info(f"Deleted from cache: {file_hash[:16]}...")
            return True
        except Exception as e:
            logger.error(f"Error deleting from cache: {str(e)}")
            return False
    
    def get_cache_stats(self) -> Dict:
        """Get basic cache statistics."""
        try:
            table_info = self.table.table_status
            item_count = self.table.item_count
            
            return {
                'table_name': self.table_name,
                'status': table_info,
                'item_count': item_count,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {str(e)}")
            return {
                'error': str(e)
            }
