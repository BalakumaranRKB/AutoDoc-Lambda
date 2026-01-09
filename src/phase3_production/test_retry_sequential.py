#!/usr/bin/env python3
"""
Test retry logic WITHOUT hitting AWS throttling

Uses sequential requests with small delays to trigger Claude API rate limits
instead of AWS Lambda throttling.
"""
import requests
import json
import sys
import time


def test_retry_sequential(api_endpoint: str, num_requests: int = 20):
    """
    Send requests sequentially with minimal delay.
    
    This avoids AWS throttling but may trigger Claude API rate limits,
    which is what we want to test retry logic against.
    """
    print("=" * 80)
    print("RETRY LOGIC TEST - SEQUENTIAL (NO AWS THROTTLING)")
    print("=" * 80)
    print()
    print(f"API Endpoint: {api_endpoint}")
    print(f"Requests: {num_requests}")
    print(f"Mode: Sequential (one at a time)")
    print()
    print("This test avoids AWS throttling by sending one request at a time")
    print("But sends them fast enough to potentially trigger Claude API rate limits")
    print()
    
    results = []
    start_time = time.time()
    
    for i in range(1, num_requests + 1):
        test_code = f'''
def process_{i}(data):
    """Process data for request {i}."""
    result = data * 2
    return result
'''
        
        payload = {
            "file_path": f"test_{i}.py",
            "file_content": test_code
        }
        
        print(f"Request {i}/{num_requests}...", end=" ", flush=True)
        
        request_start = time.time()
        
        try:
            response = requests.post(api_endpoint, json=payload, timeout=120)
            request_time = time.time() - request_start
            
            if response.status_code == 200:
                data = response.json()['data']
                print(f"✅ {request_time:.1f}s (cached: {data.get('cached', False)})")
                
                results.append({
                    'id': i,
                    'success': True,
                    'time': request_time,
                    'cached': data.get('cached', False),
                    'cost': data.get('total_cost', 0)
                })
            else:
                print(f"❌ {response.status_code}")
                results.append({
                    'id': i,
                    'success': False,
                    'time': request_time,
                    'error': response.text[:100]
                })
        
        except Exception as e:
            request_time = time.time() - request_start
            print(f"❌ Error")
            results.append({
                'id': i,
                'success': False,
                'time': request_time,
                'error': str(e)[:100]
            })
        
        # Very small delay between requests
        time.sleep(0.1)
    
    total_time = time.time() - start_time
    
    # Analyze results
    print()
    print("=" * 80)
    print("RESULTS")
    print("=" * 80)
    print()
    
    successes = sum(1 for r in results if r['success'])
    failures = num_requests - successes
    cached_count = sum(1 for r in results if r.get('cached', False))
    
    print(f"✅ Successful:  {successes}/{num_requests} ({successes/num_requests*100:.1f}%)")
    print(f"❌ Failed:      {failures}/{num_requests} ({failures/num_requests*100:.1f}%)")
    print(f"💾 Cached:      {cached_count}/{num_requests} ({cached_count/num_requests*100:.1f}%)")
    print(f"⏱️  Total time:  {total_time:.1f}s")
    print()
    
    # Timing analysis
    successful_times = [r['time'] for r in results if r['success']]
    if successful_times:
        avg_time = sum(successful_times) / len(successful_times)
        min_time = min(successful_times)
        max_time = max(successful_times)
        
        print("Timing (Successful Requests):")
        print(f"  Average: {avg_time:.1f}s")
        print(f"  Min:     {min_time:.1f}s")
        print(f"  Max:     {max_time:.1f}s")
        print()
        
        # Detect retry patterns
        slow_requests = [r for r in results if r['success'] and r['time'] > avg_time * 2]
        if slow_requests:
            print(f"⚠️  Slow requests (likely retried): {len(slow_requests)}")
            for req in slow_requests:
                print(f"   Request {req['id']}: {req['time']:.1f}s")
            print()
            print("   These slow requests likely hit rate limits and retried!")
            print()
    
    # Cost analysis
    total_cost = sum(r.get('cost', 0) for r in results if r['success'])
    print(f"💰 Total cost: ${total_cost:.4f} (₹{total_cost * 83:.2f})")
    print()
    
    # Show failures
    failed_requests = [r for r in results if not r['success']]
    if failed_requests:
        print("❌ Failed Requests:")
        for req in failed_requests[:5]:
            print(f"  Request {req['id']}: {req.get('error', 'Unknown')}")
        if len(failed_requests) > 5:
            print(f"  ... and {len(failed_requests) - 5} more")
        print()
    
    # Analysis
    print("=" * 80)
    print("RETRY LOGIC ANALYSIS")
    print("=" * 80)
    print()
    
    success_rate = (successes / num_requests) * 100
    
    if success_rate >= 95:
        print(f"✅ EXCELLENT: {success_rate:.1f}% success rate")
        print()
        if len(slow_requests) > 0:
            print(f"   Retry logic worked on {len(slow_requests)} requests!")
            print("   These requests were slower due to retries with exponential backoff")
        else:
            print("   No retries needed (no rate limits hit)")
    elif success_rate >= 80:
        print(f"✅ GOOD: {success_rate:.1f}% success rate")
    else:
        print(f"⚠️  LOW: {success_rate:.1f}% success rate")
    
    print()
    print("To verify retry logic in CloudWatch:")
    print("  Look for logs containing '🔄 Retrying in' or 'Attempt X/5 failed'")
    print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_retry_sequential.py <API_ENDPOINT> [num_requests]")
        print()
        print("Example:")
        print("  python test_retry_sequential.py https://abc123.execute-api.ap-south-1.amazonaws.com/dev/document")
        print("  python test_retry_sequential.py https://abc123.execute-api.ap-south-1.amazonaws.com/dev/document 30")
        sys.exit(1)
    
    api_endpoint = sys.argv[1]
    num_requests = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    
    test_retry_sequential(api_endpoint, num_requests)
