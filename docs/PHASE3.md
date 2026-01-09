# Phase 3: Production - Homework Assignments

> ⚠️ **NOTE:** This document describes the original homework assignments. 
> 
> **For the complete implementation guide, see [PHASE3-COMPLETE.md](PHASE3-COMPLETE.md)**
> 
> This file is kept for historical reference and learning path documentation.

---

This phase transforms the Phase 1 POC into a production-ready system by fixing the problems discovered in Phase 2.

## Table of Contents
- [Overview](#overview)
- [Assignment 1: DynamoDB Caching](#assignment-1-dynamodb-caching)
- [Assignment 2: Intelligent Chunking](#assignment-2-intelligent-chunking)
- [Assignment 3: Retry Logic](#assignment-3-retry-logic)
- [Assignment 4: Integration & Testing](#assignment-4-integration--testing)
- [Grading](#grading)

---

## Overview

**Goal:** Build production-ready features that solve Phase 2 failures.

**Approach:** Four assignments, each fixing a specific problem:
1. Caching → Fixes cost explosion
2. Chunking → Fixes large file timeouts
3. Retry logic → Fixes rate limit failures
4. Integration → Everything working together

**Timeline:** 7 days (2 days per assignment + 1 day integration)

---

## Assignment 1: DynamoDB Caching

**Difficulty:** Medium | **Time:** 4-6 hours | **Due:** Day 2

### Problem to Solve
Phase 2 showed: Same file documented 10 times = ₹200 cost.  
With caching: First time ₹20, next 9 times ₹0 = **90% savings**.

### What You'll Build
1. DynamoDB table for cache storage
2. Cache manager module (get/set/check)
3. Lambda integration (check cache → generate if miss → save to cache)

### Key Concepts
- **Cache keys:** SHA256 hash of file content
- **TTL (Time To Live):** Auto-expire after 24 hours
- **Hit rate:** Measure cache effectiveness

### Files to Create
```
src/phase3_production/
├── cache_manager.py      # DynamoDB cache operations
└── (updated) lambda_function.py  # Cache integration
```

### SAM Template Updates
```yaml
# Add to template.yaml
Resources:
  DocumentationCache:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub 'doc-cache-${Environment}'
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: file_hash
          AttributeType: S
      KeySchema:
        - AttributeName: file_hash
          KeyType: HASH
      TimeToLiveSpecification:
        AttributeName: ttl
        Enabled: true
```

### Success Criteria
- ✅ First request: Cache MISS, calls Claude API
- ✅ Second request (same file): Cache HIT, no API call
- ✅ Cost reduced by 90% on repeated files
- ✅ DynamoDB shows cached items

### Deliverables
1. Working `cache_manager.py`
2. Updated Lambda with caching
3. Test showing cache hit/miss
4. Cost comparison (with vs without cache)

---

## Assignment 2: Intelligent Chunking

**Difficulty:** Hard | **Time:** 5-7 hours | **Due:** Day 4

### Problem to Solve
Phase 2 showed: 50,000-line files timeout after 5 minutes.  
With chunking: Process in 2,000-line chunks = **Success in 8 minutes**.

### What You'll Build
1. Code chunker (split large files intelligently)
2. Chunk processor (process multiple chunks)
3. Documentation merger (combine chunk docs)

### Key Concepts
- **Intelligent splitting:** Split at function/class boundaries, not arbitrary lines
- **Overlap:** Include context from previous chunk
- **Merging:** Combine docs without duplication

### Files to Create
```
src/phase3_production/
├── code_chunker.py       # Split code into chunks
├── chunk_processor.py    # Process and merge
└── (updated) lambda_function.py  # Chunking logic
```

### Chunking Strategy
```
File: 10,000 lines
↓
Split into chunks:
- Chunk 1: Lines 1-2,000 (Functions 1-50)
- Chunk 2: Lines 1,900-3,900 (Functions 48-98)  ← 100 line overlap
- Chunk 3: Lines 3,800-5,800 (Functions 96-146)
- Chunk 4: Lines 5,700-7,700 (Functions 144-194)
- Chunk 5: Lines 7,600-10,000 (Functions 192-250)
↓
Process each chunk independently
↓
Merge documentation:
- File overview from Chunk 1
- All function docs (remove duplicates from overlap)
- Combined metrics
```

### Success Criteria
- ✅ 50,000-line file processes successfully
- ✅ Processing time: <15 minutes
- ✅ Cost: <₹500 (vs ₹4,000 single request)
- ✅ Documentation quality maintained

### Deliverables
1. Working `code_chunker.py`
2. Working `chunk_processor.py`
3. Test with 10,000+ line file
4. Performance metrics (time, cost, quality)

---

## Assignment 3: Retry Logic

**Difficulty:** Medium | **Time:** 3-4 hours | **Due:** Day 6

### Problem to Solve
Phase 2 showed: 100 concurrent requests = 40% failure rate (429 errors).  
With retry logic: Exponential backoff → **<5% failure rate**.

### What You'll Build
1. Retry decorator with exponential backoff
2. Claude client with automatic retries
3. Circuit breaker (advanced, optional)

### Key Concepts
- **Exponential backoff:** 1s, 2s, 4s, 8s, 16s delays
- **Retryable errors:** 429, 503, timeouts
- **Non-retryable errors:** 401, 400 (fail fast)

### Files to Create
```
src/phase3_production/
├── retry_logic.py            # Retry decorator
└── (updated) claude_client.py  # Retry integration
```

### Retry Pattern
```
Attempt 1: Call API → 429 Rate Limit
  ↓ Wait 1 second
Attempt 2: Call API → 429 Rate Limit
  ↓ Wait 2 seconds
Attempt 3: Call API → 429 Rate Limit
  ↓ Wait 4 seconds
Attempt 4: Call API → Success! ✓
```

### Success Criteria
- ✅ Automatic retry on 429 errors
- ✅ Exponential backoff implemented
- ✅ Max 5 attempts before giving up
- ✅ Success rate >95% under load

### Deliverables
1. Working `retry_logic.py`
2. Updated Claude client
3. Test showing retry behavior
4. Success rate comparison (with vs without retries)

---

## Assignment 4: Integration & Testing

**Difficulty:** Medium | **Time:** 4-5 hours | **Due:** Day 7

### Problem to Solve
All Phase 3 features working together:
- Caching + Chunking + Retry Logic = **Production system**

### What You'll Build
1. Integrated Lambda function (all features)
2. Comprehensive test suite
3. Performance comparison (Phase 1 vs Phase 3)
4. Complete documentation

### Integration Flow
```
Request arrives
    ↓
Check cache (Assignment 1)
    ↓
If cache HIT → Return cached docs
    ↓
If cache MISS:
    ↓
Check file size
    ↓
If <2,000 lines → Single request (with retry)
    ↓
If >2,000 lines → Chunk (Assignment 2)
    ↓
Process with retry logic (Assignment 3)
    ↓
Save to cache
    ↓
Return result
```

### Test Suite
```python
class Phase3TestSuite:
    def test_cache_performance(self):
        # First request: cache miss
        # Second request: cache hit
        # Verify 90% cost reduction
    
    def test_large_file_handling(self):
        # 10,000-line file
        # Verify chunking works
        # Verify docs are complete
    
    def test_retry_resilience(self):
        # Burst of 100 requests
        # Verify retries happen
        # Verify >95% success rate
    
    def test_phase1_vs_phase3(self):
        # Same workload on both
        # Compare cost, time, reliability
```

### Success Criteria
- ✅ All features integrated and working
- ✅ Test suite passes 100%
- ✅ Phase 1 vs Phase 3 comparison shows:
  - 85% cost reduction
  - 10x speed improvement
  - 95%+ reliability

### Deliverables
1. Integrated `production_lambda.py`
2. Complete test suite
3. Performance analysis document
4. Architecture documentation
5. 5-minute video demo

---

## Grading

### Assignment Breakdown

| Assignment | Points | Weight |
|-----------|--------|--------|
| Assignment 1: Caching | 100 | 25% |
| Assignment 2: Chunking | 100 | 30% |
| Assignment 3: Retry Logic | 100 | 20% |
| Assignment 4: Integration | 100 | 25% |
| **Total** | **400** | **100%** |

### Grading Rubrics

**Assignment 1 (Caching):**
- DynamoDB table created: 15 points
- Cache manager implementation: 30 points
- Lambda integration: 20 points
- Cache hit/miss logic: 15 points
- Testing and metrics: 10 points
- Documentation: 10 points

**Assignment 2 (Chunking):**
- Chunking strategy design: 15 points
- Code chunker implementation: 25 points
- Chunk processor: 20 points
- Merge logic: 15 points
- Lambda integration: 10 points
- Testing and documentation: 15 points

**Assignment 3 (Retry Logic):**
- Retry strategy design: 10 points
- Retry decorator: 30 points
- Exponential backoff: 20 points
- Error classification: 15 points
- Integration: 15 points
- Testing: 10 points

**Assignment 4 (Integration):**
- Full integration: 25 points
- Test suite: 20 points
- Architecture docs: 15 points
- Performance analysis: 15 points
- Deployment guide: 10 points
- Video presentation: 15 points

### Extra Credit (50 points max)
- Parallel processing with SQS+ECS: +25 points
- CloudWatch dashboard: +15 points
- Multi-language support: +20 points
- Cost prediction model: +15 points

---

## Resources

### AWS Documentation
- DynamoDB: https://docs.aws.amazon.com/dynamodb/
- Lambda: https://docs.aws.amazon.com/lambda/
- SAM: https://docs.aws.amazon.com/sam/

### Code Examples
- Starter code in `src/phase3_production/`
- Test templates in `tests/`
- SAM template examples in `infrastructure/sam/`

### Support
- Office hours: Daily 6-8 PM
- Slack channel: #production-ai-engineering
- Code reviews: On request

---

## Expected Outcomes

By end of Phase 3, you should have:

✅ **Working System:**
- Handles files up to 50K+ lines
- Cache hit rate >80%
- Success rate >95%
- Processing time <15 minutes

✅ **Cost Optimization:**
- 85% reduction vs Phase 1
- Typical repo: ₹2,000 → ₹300
- Monthly savings: ₹34,000

✅ **Production Skills:**
- Caching strategies
- Distributed system patterns
- Retry logic and resilience
- Performance optimization
- AWS services integration

✅ **Documentation:**
- Architecture diagrams
- API documentation
- Deployment guides
- Test results

---

## Timeline

**Day 1-2:** Assignment 1 (Caching)
**Day 3-4:** Assignment 2 (Chunking)
**Day 5-6:** Assignment 3 (Retry Logic)
**Day 7:** Assignment 4 (Integration & Testing)

---

Good luck! Remember: Phase 2 showed the problems, Phase 3 builds the solutions. Every feature you implement directly addresses a failure you experienced.

This is how real production systems are built. 🚀

---

> 📚 **For implementation details and deployment instructions, see [PHASE3-COMPLETE.md](PHASE3-COMPLETE.md)**
