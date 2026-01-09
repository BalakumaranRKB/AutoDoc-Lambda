# Phase 2 Quick Reference

Quick commands for running breaking simulations.

**⚠️ NO API CALLS - NO COSTS - Simulations only!**

## 🚀 Quick Start

```bash
cd src/phase2_breaking

# Run all simulations (2 minutes, $0 cost)
python run_all_tests.py
```

## 📋 Individual Simulations

```bash
# Simulation 1: Large file timeout
python test_1_large_file_timeout.py

# Simulation 2: Cost explosion (10 runs, no cache)
python test_2_cost_explosion.py

# Simulation 3: Rate limits (50 concurrent)
python test_3_rate_limits.py

# Simulation 4: Sequential slowness (50 files)
python test_4_sequential_slow.py
```

## 🎛️ Custom Parameters

```bash
# Different file sizes, runs, concurrency, etc.
python test_1_large_file_timeout.py 5000
python test_2_cost_explosion.py 20
python test_3_rate_limits.py 100 30
python test_4_sequential_slow.py 200
```

## 📊 What Each Shows

| Simulation | Shows | Phase 3 Fix |
|------------|-------|-------------|
| 1. Timeout | Lambda 5-min limit | Chunking |
| 2. Cost | 90% waste w/o cache | DynamoDB |
| 3. Rate Limits | 40% failure rate | Retry logic |
| 4. Sequential | 10x slower | Parallel |

## 💰 Total Cost

**All simulations: $0.00**

No API calls, no charges, same learning!

## ⏱️ Time Required

- All simulations: ~2 minutes
- Per simulation: ~30 seconds

## 📝 For Documentation

Capture from each simulation:
1. Token/cost calculations
2. Failure explanations
3. Phase 3 solutions
4. Your analysis

## 🎯 Learning Goals

- Understand failure patterns
- Calculate real costs
- Appreciate Phase 3 solutions
- Make informed decisions

---

**Zero cost, full learning!** 🚀
