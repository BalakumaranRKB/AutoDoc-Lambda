#!/usr/bin/env python3
"""
Test Phase 3 Deployment with Caching

This script tests:
1. Cache MISS on first request
2. Cache HIT on second identical request  
3. 90% cost reduction verification
"""
import requests
import json
import sys
import time


def test_phase3_caching(api_endpoint: str):
    """
    Test Phase 3 caching functionality.
    
    Args:
        api_endpoint: Your API Gateway endpoint URL
    """
    print("=" * 80)
    print("PHASE 3 CACHING TEST")
    print("=" * 80)
    print()
    print(f"API Endpoint: {api_endpoint}")
    print()
    
    # Test code
    test_code = '''
def calculate_sum(numbers):
    """
    Calculate the sum of a list of numbers.
    
    Args:
        numbers: List of numbers to sum
        
    Returns:
        Total sum of all numbers
    """
    total = 0
    for num in numbers:
        total += num
    return total


def calculate_average(numbers):
    """
    Calculate the average of a list of numbers.
    
    Args:
        numbers: List of numbers
        
    Returns:
        Average value
    """
    if not numbers:
        return 0
    return calculate_sum(numbers) / len(numbers)
'''
    
    payload = {
        "file_path": "calculator.py",
        "file_content": test_code
    }
    
    print("Test File: calculator.py")
    print(f"Lines: {len(test_code.split(chr(10)))}")
    print()
    
    # TEST 1: First Request (Cache MISS)
    print("=" * 80)
    print("TEST 1: First Request (should be Cache MISS)")
    print("=" * 80)
    print()
    
    print("Sending request...")
    start = time.time()
    
    try:
        response = requests.post(api_endpoint, json=payload, timeout=60)
        elapsed = time.time() - start
        
        if response.status_code == 200:
            first_data = response.json()['data']
            
            print(f"✅ SUCCESS")
            print(f"   Status Code: {response.status_code}")
            print(f"   Time: {elapsed:.2f} seconds")
            print(f"   Cached: {first_data.get('cached', False)}")
            print(f"   Cache Key: {first_data.get('cache_key', 'N/A')[:16]}...")
            print(f"   Cost: ${first_data.get('total_cost', 0):.6f}")
            print(f"   Tokens: {first_data.get('total_tokens', 0):,}")
            print()
            
            if first_data.get('cached'):
                print("⚠️  WARNING: First request should NOT be cached!")
            else:
                print("✅ PASS: Cache MISS as expected")
            
            # Save for comparison
            first_cost = first_data.get('total_cost', 0)
            first_time = elapsed
            first_cached = first_data.get('cached', False)
            cache_key = first_data.get('cache_key', 'unknown')
            
            print()
            print("Documentation Preview:")
            print("-" * 80)
            doc = first_data.get('documentation', '')
            print(doc[:300] + "..." if len(doc) > 300 else doc)
            print("-" * 80)
            
        else:
            print(f"❌ FAILED")
            print(f"   Status Code: {response.status_code}")
            print(f"   Error: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return
    
    # Wait a moment
    print()
    print("Waiting 2 seconds before next request...")
    time.sleep(2)
    print()
    
    # TEST 2: Second Request (Cache HIT)
    print("=" * 80)
    print("TEST 2: Second Request (should be Cache HIT)")
    print("=" * 80)
    print()
    
    print("Sending IDENTICAL request...")
    start = time.time()
    
    try:
        response = requests.post(api_endpoint, json=payload, timeout=60)
        elapsed = time.time() - start
        
        if response.status_code == 200:
            second_data = response.json()['data']
            
            print(f"✅ SUCCESS")
            print(f"   Status Code: {response.status_code}")
            print(f"   Time: {elapsed:.2f} seconds")
            print(f"   Cached: {second_data.get('cached', False)}")
            print(f"   Cache Key: {second_data.get('cache_key', 'N/A')[:16]}...")
            print(f"   Cost: ${second_data.get('total_cost', 0):.6f}")
            print(f"   Tokens: {second_data.get('total_tokens', 0):,}")
            print()
            
            if second_data.get('cached'):
                print("✅ PASS: Cache HIT!")
                print(f"   Speed improvement: {first_time/elapsed:.1f}x faster")
            else:
                print("❌ FAIL: Should have been cached!")
            
            second_cost = second_data.get('total_cost', 0)
            second_time = elapsed
            second_cached = second_data.get('cached', False)
            
        else:
            print(f"❌ FAILED")
            print(f"   Status Code: {response.status_code}")
            print(f"   Error: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return
    
    # Summary
    print()
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print()
    
    print("Request 1 (Cache MISS):")
    print(f"   Cost: ${first_cost:.6f}")
    print(f"   Time: {first_time:.2f}s")
    print()
    
    print("Request 2 (Cache HIT):")
    print(f"   Cost: ${second_cost:.6f}")
    print(f"   Time: {second_time:.2f}s")
    print()
    
    # Calculate savings
    if first_cost > 0:
        savings = first_cost - second_cost
        savings_percent = (savings / first_cost) * 100
        
        print("💰 COST SAVINGS:")
        print(f"   Saved: ${savings:.6f} ({savings_percent:.1f}%)")
        print(f"   In INR: ₹{savings * 83:.4f}")
        print()
        
        if savings_percent >= 99:
            print("✅ EXCELLENT: ~100% cost reduction on cache hit!")
        elif savings_percent >= 90:
            print("✅ GREAT: 90%+ cost reduction achieved!")
        else:
            print(f"⚠️  WARNING: Only {savings_percent:.1f}% savings (expected 100%)")
    
    # Speed improvement
    if second_time > 0:
        speedup = first_time / second_time
        print()
        print("⚡ PERFORMANCE:")
        print(f"   Speedup: {speedup:.1f}x faster with cache")
        
        if speedup >= 10:
            print("✅ EXCELLENT: Cache is much faster!")
        elif speedup >= 5:
            print("✅ GOOD: Significant speed improvement")
        else:
            print("⚠️  Cache speedup lower than expected")
    
    print()
    print("=" * 80)
    print("✅ PHASE 3 TEST COMPLETE")
    print("=" * 80)
    print()
    
    # Verification checklist - FIXED
    print("Verification Checklist:")
    print(f"  [{'✅' if not first_cached else '❌'}] First request is cache MISS")
    print(f"  [{'✅' if second_cost == 0 else '❌'}] Second request cost is $0")
    print(f"  [{'✅' if second_cached else '❌'}] Second request is cache HIT")
    print(f"  [{'✅' if speedup >= 5 else '❌'}] Cache is significantly faster")
    print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_phase3.py <API_ENDPOINT>")
        print()
        print("Example:")
        print("  python test_phase3.py https://abc123.execute-api.us-east-1.amazonaws.com/dev/document")
        print()
        print("To get your API endpoint:")
        print("  aws cloudformation describe-stacks --stack-name YOUR_STACK_NAME --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' --output text")
        sys.exit(1)
    
    api_endpoint = sys.argv[1]
    test_phase3_caching(api_endpoint)
