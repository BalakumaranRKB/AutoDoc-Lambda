# Phase 2: Breaking - Discovering Limits

This phase deliberately breaks the Phase 1 POC to discover its limitations. Students experience real failures that motivate Phase 3 improvements.

## Table of Contents
- [Overview](#overview)
- [Breaking Scenario 1: Large Files](#breaking-scenario-1-large-files)
- [Breaking Scenario 2: Cost Explosion](#breaking-scenario-2-cost-explosion)
- [Breaking Scenario 3: Rate Limits](#breaking-scenario-3-rate-limits)
- [Breaking Scenario 4: Slow Processing](#breaking-scenario-4-slow-processing)
- [Summary](#summary)

---

## Overview

**Goal:** Understand what fails and why.

**Method:** Stress test Phase 1 with realistic workloads.

**Learning:** Experience real constraints (cost, performance, reliability) that production systems must handle.

---

## Breaking Scenario 1: Large Files

### The Test
Process a 50,000-line Python file.

### What Happens
```bash
curl -X POST $API_ENDPOINT \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "huge_module.py",
    "file_content": "[50,000 lines of code...]"
  }'
```

**Result:** Lambda timeout after 5 minutes.

### Why It Fails
1. **Huge context window:** 50K lines = ~200K tokens in prompt
2. **Claude processing time:** Large prompts take 3-4+ minutes
3. **Lambda timeout:** 5-minute hard limit
4. **Single-pass processing:** No way to break it up

### Cost Impact
Before timeout: ~₹4,000 ($48) for a single file!

### Observed Errors
```
Task timed out after 300.00 seconds
```

CloudWatch shows:
- Lambda ran for exactly 300 seconds
- Partial API response received
- No documentation generated
- Still charged for API usage (partial)

### Key Lessons
- **Token limits matter** - Can't send infinite context
- **Synchronous processing fails** - Need async or chunking
- **Timeouts are hard limits** - Can't just "wait longer"

---

## Breaking Scenario 2: Cost Explosion

### The Test
Generate documentation for the same 1,000-line file 10 times.

### What Happens
```python
for i in range(10):
    response = requests.post(API_ENDPOINT, json={
        "file_path": "utils.py",
        "file_content": same_code  # Identical every time
    })
```

**Result:** 10 successful requests, 10x the cost.

### Why It Fails
- **No caching:** Every request calls Claude API
- **No deduplication:** Identical input = full cost each time
- **No optimization:** Could serve 9 requests from cache

### Cost Impact
```
Request 1: ₹20
Request 2: ₹20  ← Could be ₹0 from cache
Request 3: ₹20  ← Could be ₹0 from cache
...
Request 10: ₹20 ← Could be ₹0 from cache

Total: ₹200
With caching: ₹20 (90% savings!)
```

### Real-World Scenario
- Developer runs documentation 10 times while debugging
- CI/CD regenerates docs on every commit
- Multiple team members document same files
- **Monthly cost:** ₹20,000+ instead of ₹2,000

### Key Lessons
- **Caching is essential** - Don't recompute identical results
- **Content hashing works** - SHA256 of code = cache key
- **Economics drive architecture** - 90% cost reduction motivates caching

---

## Breaking Scenario 3: Rate Limits

### The Test
Send 100 concurrent requests.

### What Happens
```python
import concurrent.futures

def make_request(i):
    return requests.post(API_ENDPOINT, json={...})

with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
    futures = [executor.submit(make_request, i) for i in range(100)]
```

**Result:** Mix of successes and 429 errors.

### Observed Failures
```json
{
  "error": {
    "type": "rate_limit_error",
    "message": "Rate limit exceeded"
  }
}
```

**Pattern:**
- First 20-30 requests: Success
- Next 50 requests: 429 errors
- Last 20 requests: Success (after backoff)

### Why It Fails
- **No retry logic:** 429 = immediate failure
- **No exponential backoff:** Keeps hammering API
- **No request queuing:** All hit at once

### Cost Impact
- ~40% of requests fail
- Failed requests still consume API quota
- Users get inconsistent results

### Key Lessons
- **APIs have limits** - Can't send unlimited requests
- **Retry patterns essential** - 429 should retry, not fail
- **Exponential backoff** - Prevents thundering herd
- **Queue requests** - Smooth out bursts

---

## Breaking Scenario 4: Slow Processing

### The Test
Document 100 files sequentially.

### What Happens
```python
files = [f"file_{i}.py" for i in range(100)]

start = time.time()
for file in files:
    response = requests.post(API_ENDPOINT, json={...})
end = time.time()

print(f"Total time: {end - start:.0f} seconds")
```

**Result:** Takes 50+ minutes.

### Breakdown
```
Per file:
- API Gateway overhead: ~0.2s
- Lambda cold start: ~1s (first request)
- Code analysis: ~0.5s
- Claude API call: ~3s
- Response processing: ~0.3s
Total per file: ~5 seconds

100 files × 5 seconds = 500 seconds (8.3 minutes)
But with cold starts, retries, variance: 50+ minutes
```

### Why It's Slow
- **Sequential processing:** One file at a time
- **No parallelization:** Not using available concurrency
- **Repeated cold starts:** Lambda not staying warm
- **Network overhead:** 100 separate HTTP round trips

### Better Approach
With 10 parallel workers: ~5 minutes instead of 50.

### Key Lessons
- **Parallelization matters** - 10x speedup available
- **Batch processing** - Reduce overhead
- **Keep Lambda warm** - Provisioned concurrency
- **ECS for large jobs** - Better for sustained workloads

---

## Summary

### What We Learned

| Problem | Phase 1 Reality | Phase 3 Solution |
|---------|----------------|------------------|
| Large files (50K lines) | Timeout (5 min) | Chunking (2K per chunk) |
| Repeated files | ₹200 (10x cost) | Caching (₹20, 90% savings) |
| Rate limits | 40% failure rate | Retry with backoff |
| 100 files | 50+ minutes | Parallel processing (5 min) |

### Economic Reality

**Phase 1 costs for 100-file repo (no optimization):**
- First run: ₹2,000
- Second run: ₹2,000 (no cache!)
- Third run: ₹2,000 (no cache!)
- **Monthly (10 runs):** ₹20,000

**Phase 3 costs (with optimizations):**
- First run: ₹2,000
- Second run: ₹200 (90% cache hit)
- Third run: ₹200 (90% cache hit)
- **Monthly (10 runs):** ₹3,800 (81% savings!)

### Performance Reality

**Phase 1 for 100 files:**
- Sequential processing: 50+ minutes
- High failure rate: ~40% on bursts
- No resilience: Failures propagate

**Phase 3 for 100 files:**
- Parallel processing: ~5 minutes (10x faster)
- Retry logic: <5% failure rate
- Graceful degradation: Partial results OK

### Reliability Reality

**Phase 1:**
- 429 error = complete failure
- Network blip = lost request
- Lambda timeout = wasted money
- No visibility into what failed

**Phase 3:**
- 429 error = automatic retry
- Network blip = exponential backoff
- Lambda timeout = chunked processing continues
- CloudWatch metrics show everything

---

## Next Steps

Phase 2 exposed the problems. Phase 3 fixes them:

1. **Caching (Assignment 1)** - DynamoDB cache layer
2. **Chunking (Assignment 2)** - Handle 50K+ line files
3. **Retry Logic (Assignment 3)** - Exponential backoff
4. **Integration (Assignment 4)** - All features working together

Each assignment addresses a specific failure from Phase 2.

---

## Testing Phase 2 Yourself

### Test 1: Timeout
```bash
# Generate a large file
python -c "
for i in range(10000):
    print(f'def func_{i}(): pass')
" > huge.py

# Try to document it
curl -X POST $API_ENDPOINT \
  -d @huge.py
```

### Test 2: Cost Explosion
```bash
# Same file 10 times
for i in {1..10}; do
  curl -X POST $API_ENDPOINT -d @same_file.py
done

# Check CloudWatch logs for total cost
```

### Test 3: Rate Limit
```python
# concurrent_test.py
import concurrent.futures
import requests

def call_api(i):
    try:
        resp = requests.post(API_ENDPOINT, json={...}, timeout=10)
        return resp.status_code
    except Exception as e:
        return str(e)

with concurrent.futures.ThreadPoolExecutor(max_workers=50) as ex:
    results = list(ex.map(call_api, range(100)))

print(f"Success: {results.count(200)}")
print(f"Rate limited: {results.count(429)}")
```

---

**Remember:** These failures are educational. They teach why production systems need caching, retry logic, and chunking. Phase 3 implements these patterns properly.
