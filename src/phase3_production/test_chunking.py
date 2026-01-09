#!/usr/bin/env python3
"""
Test chunking feature with a large file

Demonstrates:
1. Automatic chunking detection
2. Parallel chunk processing  
3. Individual chunk caching
4. Documentation merging
"""
import requests
import json
import sys
import time


def generate_large_file(num_functions: int = 100) -> str:
    """Generate a large Python file with many functions."""
    
    code_parts = [
        '"""',
        'Large Python module for testing chunking.',
        '',
        'This file contains many functions to test the chunking feature.',
        '"""',
        '',
        'import math',
        'import random',
        ''
    ]
    
    for i in range(num_functions):
        func_code = f'''
def function_{i}(x, y):
    """
    Function number {i}.
    
    Performs calculation {i} on inputs x and y.
    
    Args:
        x: First input number
        y: Second input number
        
    Returns:
        Calculated result
    """
    result = (x + y) * {i}
    if result > 100:
        return result / 2
    return result
'''
        code_parts.append(func_code)
    
    return '\n'.join(code_parts)


def test_chunking(api_endpoint: str):
    """Test chunking feature."""
    
    print("=" * 80)
    print("CHUNKING FEATURE TEST")
    print("=" * 80)
    print()
    print(f"API Endpoint: {api_endpoint}")
    print()
    
    # Generate large file
    print("Generating large Python file...")
    large_code = generate_large_file(num_functions=150)
    
    lines = large_code.split('\n')
    total_lines = len(lines)
    
    print(f"✅ Generated file with {total_lines} lines")
    print(f"   Contains 150 functions")
    print(f"   Should trigger chunking (threshold: 2000 lines)")
    print()
    
    payload = {
        "file_path": "large_module.py",
        "file_content": large_code
    }
    
    # Test 1: First request (all chunks will be cache misses)
    print("=" * 80)
    print("TEST 1: First Request - Process Large File")
    print("=" * 80)
    print()
    print("Sending large file (will be chunked)...")
    print("This may take 30-60 seconds as chunks are processed in parallel...")
    print()
    
    start = time.time()
    
    try:
        response = requests.post(api_endpoint, json=payload, timeout=180)
        elapsed = time.time() - start
        
        if response.status_code == 200:
            data = response.json()['data']
            
            print(f"✅ SUCCESS")
            print(f"   Time: {elapsed:.1f}s")
            print(f"   Chunked: {data.get('chunked', False)}")
            print()
            
            if data.get('chunked'):
                chunk_info = data.get('chunking_info', {})
                
                print("CHUNKING DETAILS:")
                print(f"   Total chunks: {chunk_info.get('total_chunks', 0)}")
                print(f"   Cache hits: {chunk_info.get('cache_hits', 0)}")
                print(f"   Cache misses: {chunk_info.get('cache_misses', 0)}")
                print(f"   Cache hit rate: {chunk_info.get('cache_hit_rate', 0):.1f}%")
                print()
                
                print(f"   Total cost: ${data.get('total_cost', 0):.6f}")
                print(f"   Total tokens: {data.get('total_tokens', 0):,}")
                print()
                
                # Show chunk summary
                chunk_summary = chunk_info.get('chunk_summary', {})
                print("CHUNK BREAKDOWN:")
                print(f"   Avg chunk size: {chunk_summary.get('avg_chunk_size', 0)} lines")
                print(f"   Min chunk size: {chunk_summary.get('min_chunk_size', 0)} lines")
                print(f"   Max chunk size: {chunk_summary.get('max_chunk_size', 0)} lines")
                print()
                
                first_cost = data.get('total_cost', 0)
                first_chunks = chunk_info.get('total_chunks', 0)
            else:
                print("⚠️  File was NOT chunked (unexpected!)")
                return
        else:
            print(f"❌ FAILED: {response.status_code}")
            print(f"   Error: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return
    
    # Wait before second request
    print()
    print("Waiting 2 seconds before second request...")
    time.sleep(2)
    print()
    
    # Test 2: Second request (all chunks should be cache hits)
    print("=" * 80)
    print("TEST 2: Second Request - All Chunks Cached")
    print("=" * 80)
    print()
    print("Sending SAME large file again...")
    print("All chunks should be cached (fast and free!)...")
    print()
    
    start = time.time()
    
    try:
        response = requests.post(api_endpoint, json=payload, timeout=180)
        elapsed = time.time() - start
        
        if response.status_code == 200:
            data = response.json()['data']
            
            print(f"✅ SUCCESS")
            print(f"   Time: {elapsed:.1f}s")
            print()
            
            chunk_info = data.get('chunking_info', {})
            
            print("CHUNKING DETAILS:")
            print(f"   Total chunks: {chunk_info.get('total_chunks', 0)}")
            print(f"   Cache hits: {chunk_info.get('cache_hits', 0)}")
            print(f"   Cache misses: {chunk_info.get('cache_misses', 0)}")
            print(f"   Cache hit rate: {chunk_info.get('cache_hit_rate', 0):.1f}%")
            print()
            
            print(f"   Total cost: ${data.get('total_cost', 0):.6f}")
            print()
            
            second_cost = data.get('total_cost', 0)
            second_chunks = chunk_info.get('total_chunks', 0)
            cache_hits = chunk_info.get('cache_hits', 0)
            
        else:
            print(f"❌ FAILED: {response.status_code}")
            return
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return
    
    # Analysis
    print("=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)
    print()
    
    print(f"File size: {total_lines} lines (150 functions)")
    print(f"Chunks: {first_chunks}")
    print()
    
    print("Request 1 (all cache misses):")
    print(f"   Cost: ${first_cost:.6f}")
    print()
    
    print("Request 2 (all cache hits):")
    print(f"   Cost: ${second_cost:.6f}")
    print(f"   Cache hits: {cache_hits}/{second_chunks}")
    print()
    
    if first_cost > 0:
        savings = first_cost - second_cost
        savings_percent = (savings / first_cost) * 100
        
        print("💰 COST SAVINGS:")
        print(f"   Saved: ${savings:.6f} ({savings_percent:.1f}%)")
        print(f"   In INR: ₹{savings * 83:.2f}")
        print()
    
    # Final assessment
    print("=" * 80)
    print("CHUNKING FEATURE ASSESSMENT")
    print("=" * 80)
    print()
    
    if cache_hits == second_chunks:
        print("✅ CHUNKING + CACHING WORKING PERFECTLY!")
        print()
        print(f"   • Large file ({total_lines} lines) processed successfully")
        print(f"   • Split into {first_chunks} logical chunks")
        print(f"   • All chunks cached individually")
        print(f"   • Second request: 100% cache hits, $0 cost")
        print()
        print("🎉 Phase 3 is production-ready with chunking!")
    else:
        print(f"⚠️  Some chunks not cached: {cache_hits}/{second_chunks}")
    
    print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_chunking.py <API_ENDPOINT>")
        print()
        print("Example:")
        print("  python test_chunking.py https://abc123.execute-api.ap-south-1.amazonaws.com/dev/document")
        sys.exit(1)
    
    api_endpoint = sys.argv[1]
    test_chunking(api_endpoint)
