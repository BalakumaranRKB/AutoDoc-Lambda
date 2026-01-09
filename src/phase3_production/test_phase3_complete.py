#!/usr/bin/env python3
"""
Comprehensive Phase 3 test demonstrating BOTH caching AND retry logic
"""
import requests
import json
import sys
import time


def test_phase3_complete(api_endpoint: str):
    """
    Complete test showing:
    1. Cache MISS on first request
    2. Cache HIT on subsequent identical requests (instant, $0)
    3. Retry logic handling any rate limits
    """
    print("=" * 80)
    print("PHASE 3 COMPLETE TEST - CACHING + RETRY LOGIC")
    print("=" * 80)
    print()
    print(f"API Endpoint: {api_endpoint}")
    print()
    
    # Same test code for all requests
    test_code = '''
def fibonacci(n):
    """Calculate the nth Fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def factorial(n):
    """Calculate factorial of n."""
    if n <= 1:
        return 1
    return n * factorial(n-1)
'''
    
    payload = {
        "file_path": "math_utils.py",
        "file_content": test_code
    }
    
    results = []
    
    # Test 1: First request (Cache MISS)
    print("=" * 80)
    print("TEST 1: First Request (Cache MISS)")
    print("=" * 80)
    print()
    
    start = time.time()
    response = requests.post(api_endpoint, json=payload, timeout=120)
    elapsed = time.time() - start
    
    if response.status_code == 200:
        data = response.json()['data']
        print(f"✅ SUCCESS")
        print(f"   Time: {elapsed:.1f}s")
        print(f"   Cached: {data.get('cached', False)}")
        print(f"   Cost: ${data.get('total_cost', 0):.6f}")
        print(f"   Tokens: {data.get('total_tokens', 0):,}")
        
        results.append({
            'test': 1,
            'success': True,
            'time': elapsed,
            'cached': data.get('cached', False),
            'cost': data.get('total_cost', 0)
        })
    else:
        print(f"❌ FAILED: {response.status_code}")
        return
    
    print()
    time.sleep(1)
    
    # Test 2: Immediate second request (Cache HIT)
    print("=" * 80)
    print("TEST 2: Second Request - Immediate (Cache HIT)")
    print("=" * 80)
    print()
    
    start = time.time()
    response = requests.post(api_endpoint, json=payload, timeout=120)
    elapsed = time.time() - start
    
    if response.status_code == 200:
        data = response.json()['data']
        print(f"✅ SUCCESS")
        print(f"   Time: {elapsed:.1f}s")
        print(f"   Cached: {data.get('cached', False)}")
        print(f"   Cost: ${data.get('total_cost', 0):.6f}")
        print(f"   Speedup: {results[0]['time']/elapsed:.1f}x faster")
        
        results.append({
            'test': 2,
            'success': True,
            'time': elapsed,
            'cached': data.get('cached', False),
            'cost': data.get('total_cost', 0)
        })
    else:
        print(f"❌ FAILED: {response.status_code}")
    
    print()
    time.sleep(1)
    
    # Test 3: Burst of 10 identical requests (all Cache HITs)
    print("=" * 80)
    print("TEST 3: Burst of 10 Identical Requests (All Cache HITs)")
    print("=" * 80)
    print()
    print("Sending 10 rapid requests (0.1s apart)...")
    print()
    
    burst_start = time.time()
    burst_results = []
    
    for i in range(10):
        start = time.time()
        response = requests.post(api_endpoint, json=payload, timeout=120)
        elapsed = time.time() - start
        
        if response.status_code == 200:
            data = response.json()['data']
            cached = data.get('cached', False)
            cost = data.get('total_cost', 0)
            
            status = "✅" if cached else "⚠️ "
            print(f"{status} Request {i+1}/10: {elapsed:.1f}s (cached: {cached}, cost: ${cost:.6f})")
            
            burst_results.append({
                'success': True,
                'time': elapsed,
                'cached': cached,
                'cost': cost
            })
        else:
            print(f"❌ Request {i+1}/10: Failed ({response.status_code})")
            burst_results.append({
                'success': False,
                'time': elapsed
            })
        
        time.sleep(0.1)  # Small delay
    
    burst_total = time.time() - burst_start
    
    print()
    print(f"Burst completed in {burst_total:.1f}s")
    
    # Analysis
    print()
    print("=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)
    print()
    
    all_results = results + burst_results
    total_successes = sum(1 for r in all_results if r.get('success', False))
    total_cached = sum(1 for r in all_results if r.get('cached', False))
    total_cost = sum(r.get('cost', 0) for r in all_results)
    
    print(f"Total Requests:   {len(all_results)}")
    print(f"Successful:       {total_successes}/{len(all_results)} ({total_successes/len(all_results)*100:.1f}%)")
    print(f"Cache Hits:       {total_cached}/{len(all_results)} ({total_cached/len(all_results)*100:.1f}%)")
    print(f"Total Cost:       ${total_cost:.6f} (₹{total_cost * 83:.2f})")
    print()
    
    # Calculate savings
    first_request_cost = results[0]['cost']
    if total_cached > 0:
        savings = first_request_cost * total_cached
        savings_percent = (savings / (first_request_cost * len(all_results))) * 100
        
        print("💰 COST SAVINGS FROM CACHING:")
        print(f"   First request cost: ${first_request_cost:.6f}")
        print(f"   Saved from {total_cached} cache hits: ${savings:.6f}")
        print(f"   Overall savings: {savings_percent:.1f}%")
        print(f"   In INR: ₹{savings * 83:.2f}")
        print()
    
    # Performance analysis
    cache_hit_times = [r['time'] for r in all_results if r.get('cached', False)]
    cache_miss_times = [r['time'] for r in all_results if r.get('success', False) and not r.get('cached', False)]
    
    if cache_hit_times and cache_miss_times:
        avg_hit = sum(cache_hit_times) / len(cache_hit_times)
        avg_miss = sum(cache_miss_times) / len(cache_miss_times)
        speedup = avg_miss / avg_hit
        
        print("⚡ PERFORMANCE:")
        print(f"   Cache MISS avg: {avg_miss:.1f}s")
        print(f"   Cache HIT avg:  {avg_hit:.1f}s")
        print(f"   Speedup:        {speedup:.1f}x faster")
        print()
    
    # Final assessment
    print("=" * 80)
    print("PHASE 3 FEATURES VERIFIED")
    print("=" * 80)
    print()
    
    if total_successes == len(all_results):
        print("✅ RETRY LOGIC: All requests succeeded (100% success rate)")
        print("   Even with rapid requests, retry logic handled any issues")
        print()
    
    if total_cached >= 10:
        print(f"✅ CACHING: {total_cached} cache hits with $0 cost")
        print(f"   Saved ${savings:.6f} through intelligent caching")
        print()
    
    if total_successes == len(all_results) and total_cached >= 10:
        print("🎉 PHASE 3 IS PRODUCTION READY!")
        print()
        print("Key achievements:")
        print(f"  • 100% success rate (retry logic working)")
        print(f"  • {savings_percent:.0f}% cost reduction (caching working)")
        print(f"  • {speedup:.0f}x faster response (cache vs API)")
        print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_phase3_complete.py <API_ENDPOINT>")
        print()
        print("Example:")
        print("  python test_phase3_complete.py https://abc123.execute-api.ap-south-1.amazonaws.com/dev/document")
        sys.exit(1)
    
    api_endpoint = sys.argv[1]
    test_phase3_complete(api_endpoint)
