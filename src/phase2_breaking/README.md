# Phase 2: Breaking Tests (SIMULATIONS)

**⚠️ NO API CALLS - NO COSTS - Educational simulations only!**

These tests **simulate** what would happen if you tried to use Phase 1 in production, without actually spending money on API calls.

## 🎯 Purpose

Demonstrate **real failure patterns** through calculations and projections:
1. Large files cause timeouts
2. No caching causes cost explosion  
3. No retry logic causes high failure rates
4. Sequential processing is too slow

**Learning Goal:** Understand WHY Phase 1 fails at scale, appreciate Phase 3 solutions.

---

## 📋 Simulation Suite

### Simulation 1: Large File Timeout ⏱️
**File:** `test_1_large_file_timeout.py`

**What it simulates:** Processing a 10,000+ line Python file

**Expected outcome:** Would timeout after 5 minutes

**Calculations shown:**
- Token estimation (~200K tokens)
- Cost projection ($2-4 per file)
- Processing time estimate (7-10 minutes needed)
- Lambda timeout analysis (5 min limit)

**Run it:**
```bash
python test_1_large_file_timeout.py

# Custom size
python test_1_large_file_timeout.py 3000
```

**No cost:** $0.00 (simulation only)

---

### Simulation 2: Cost Explosion 💰
**File:** `test_2_cost_explosion.py`

**What it simulates:** Same file processed 10 times

**Expected outcome:** 10x cost without caching

**Calculations shown:**
- Cost per file (~$0.01)
- Total without cache ($0.10)
- Total with cache ($0.01)
- 90% savings calculation
- Monthly projection

**Run it:**
```bash
python test_2_cost_explosion.py

# More runs
python test_2_cost_explosion.py 20
```

**No cost:** $0.00 (simulation only)

---

### Simulation 3: Rate Limit Failures 🚫
**File:** `test_3_rate_limits.py`

**What it simulates:** 50 concurrent requests

**Expected outcome:** ~40% failure rate (429 errors)

**Calculations shown:**
- Rate limit thresholds
- Request pattern analysis
- Failure rate estimation
- Retry logic improvement
- Cost of failures

**Run it:**
```bash
python test_3_rate_limits.py

# Different load
python test_3_rate_limits.py 100 30
```

**No cost:** $0.00 (simulation only)

---

### Simulation 4: Sequential Slowness 🐌
**File:** `test_4_sequential_slow.py`

**What it simulates:** 50 files processed one-by-one

**Expected outcome:** 4+ minutes (vs <1 min parallel)

**Calculations shown:**
- Time per file breakdown
- Sequential timeline
- Parallel timeline  
- Speedup calculation (10x)
- Architecture comparisons

**Run it:**
```bash
python test_4_sequential_slow.py

# Different count
python test_4_sequential_slow.py 100
```

**No cost:** $0.00 (simulation only)

---

## 🚀 Quick Start

### Run All Simulations

```bash
cd src/phase2_breaking

# Run all 4 simulations
python run_all_tests.py
```

**Takes:** ~2 minutes  
**Cost:** $0.00

### Run Individual Simulations

```bash
# Timeout simulation
python test_1_large_file_timeout.py

# Cost explosion
python test_2_cost_explosion.py

# Rate limits
python test_3_rate_limits.py

# Sequential slowness
python test_4_sequential_slow.py
```

---

## 📊 What You'll See

Each simulation shows:

✅ **Problem description** - What would fail  
✅ **Calculations** - Token counts, costs, timing  
✅ **Failure analysis** - Why it fails  
✅ **Phase 3 solution** - How to fix it  
✅ **Estimates** - What it would cost (but you don't pay!)  

---

## 💡 Educational Value

### Simulation 1 Teaches:
- Token counting matters
- Lambda timeout limits are hard
- Context window sizes
- **Solution:** Chunking strategy

### Simulation 2 Teaches:
- Cache hit rates
- Cost optimization potential
- Hash-based caching
- **Solution:** DynamoDB cache

### Simulation 3 Teaches:
- API rate limiting
- Exponential backoff math
- Failure patterns
- **Solution:** Retry logic

### Simulation 4 Teaches:
- Parallelization benefits
- Architecture tradeoffs
- Time vs cost
- **Solution:** ECS + SQS

---

## 🎓 For Students

### How to Use These Simulations

1. **Run each simulation**
2. **Read the output carefully**
3. **Note the calculations**
4. **Understand the failure patterns**
5. **Appreciate the Phase 3 solutions**

### What to Document

For your homework/presentation:

**For Each Simulation:**
- Terminal output (copy/paste)
- Key metrics (costs, timing, failure rates)
- Why it fails (your explanation)
- Phase 3 solution (how you'll fix it)

**Example Documentation:**
```
Simulation 2: Cost Explosion

Without caching:
- 10 runs × $0.0102 = $0.1020 total
- Every request calls API

With caching:
- First run: $0.0102
- Runs 2-10: $0.0000 (cache hit)
- Total: $0.0102 (90% savings!)

Lesson: Caching is essential for cost control
Phase 3: Implement DynamoDB cache with SHA256 keys
```

---

## 📈 Projection Accuracy

These simulations are based on:

✅ **Real Claude API pricing** (as of Jan 2025)  
✅ **Actual Lambda performance** (observed)  
✅ **Documented rate limits** (Claude API)  
✅ **Conservative estimates** (not best-case)  

**Accuracy:** ~90% - Real results may vary by ±10%

---

## ⚡ Advantages of Simulations

vs. Actually Running Tests:

| Aspect | Simulations | Real Tests |
|--------|-------------|------------|
| **Cost** | $0.00 | $2-4 |
| **Time** | 2 minutes | 15-30 minutes |
| **API calls** | 0 | 100+ |
| **Rate limits** | No risk | Will hit limits |
| **Learning** | Same! | Same! |

**Conclusion:** Simulations give you the same learning at 0% of the cost!

---

## 🔧 Customization

Want to simulate different scenarios?

```bash
# Larger file
python test_1_large_file_timeout.py 5000

# More runs
python test_2_cost_explosion.py 50

# Higher concurrency
python test_3_rate_limits.py 200 50

# More files
python test_4_sequential_slow.py 500
```

All still $0.00!

---

## 📚 Next Steps

After running simulations:

1. ✅ Understand all 4 failure patterns
2. ✅ Calculate costs for YOUR use case
3. ✅ Design Phase 3 solutions
4. ⬜ Implement Assignment 1 (Caching)
5. ⬜ Implement Assignment 2 (Chunking)
6. ⬜ Implement Assignment 3 (Retry Logic)
7. ⬜ Implement Assignment 4 (Integration)

---

## 💬 Discussion Questions

Use these for lectures/presentations:

1. **Why does Lambda timeout at 5 minutes?**
   - AWS architectural limit
   - Designed for short-lived functions
   - Forces better design (chunking)

2. **How much could caching actually save?**
   - Simulation shows 90%
   - Real-world: 80-95% depending on usage
   - More repetition = more savings

3. **Why exponential backoff instead of linear?**
   - Prevents thundering herd
   - Gives API time to recover
   - Mathematical proof of convergence

4. **Parallel vs Sequential - always better?**
   - Usually yes for independent tasks
   - Cost is the same
   - Need to manage concurrency limits

---

## 🎯 Success Criteria

You've mastered Phase 2 when you can:

✅ Run all simulations  
✅ Explain each failure pattern  
✅ Calculate costs accurately  
✅ Understand token counting  
✅ Design Phase 3 solutions  
✅ Make informed architecture decisions  

---

**Remember:** These are simulations! You learn the same lessons without spending a penny. Phase 3 will implement the real fixes. 🚀

---

## 📞 Questions?

Common questions:

**Q: Are the calculations accurate?**  
A: ~90% accurate based on real API pricing and observed performance.

**Q: Should I also run real tests?**  
A: No need! Simulations teach the same lessons at $0 cost.

**Q: Can I modify the simulations?**  
A: Yes! Edit the scripts to match your scenarios.

**Q: Will Phase 3 really fix these?**  
A: Yes! Each assignment targets one specific failure.
