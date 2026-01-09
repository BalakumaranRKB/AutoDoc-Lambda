# Quick Deployment Reference

Quick reference for building and deploying each phase.

---

## Phase 3: Production System

### Build and Deploy (Recommended)

```bash
cd infrastructure/sam

# Build with container (CRITICAL for avoiding binary dependency issues)
sam build --template template-phase3.yaml --use-container

# First deployment (guided setup)
sam deploy --template template-phase3.yaml --guided

# Subsequent deployments
sam deploy --template template-phase3.yaml
```

### Get API Endpoint

```bash
aws cloudformation describe-stacks \
  --stack-name doc-generator-phase3 \
  --region ap-south-1 \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
  --output text
```

### Quick Test

```bash
cd ../src/phase3_production

export API_ENDPOINT="https://YOUR-ID.execute-api.ap-south-1.amazonaws.com/dev/document"

# Test caching
python test_phase3.py $API_ENDPOINT

# Test chunking
python test_phase3_final.py $API_ENDPOINT
```

---

## Common Commands

### View Logs

```bash
# Tail logs in real-time
aws logs tail /aws/lambda/doc-generator-phase3-dev \
  --follow \
  --region ap-south-1

# View recent logs
aws logs tail /aws/lambda/doc-generator-phase3-dev \
  --since 10m \
  --region ap-south-1
```

### Check DynamoDB Cache

```bash
# View cached items
aws dynamodb scan \
  --table-name doc-cache-phase3-dev \
  --region ap-south-1 \
  --limit 10

# Count items
aws dynamodb scan \
  --table-name doc-cache-phase3-dev \
  --region ap-south-1 \
  --select COUNT
```

### Delete Stack

```bash
aws cloudformation delete-stack \
  --stack-name doc-generator-phase3 \
  --region ap-south-1
```

---

## Important Notes

### ✅ Always Use `--use-container`

**DON'T:**
```bash
sam build --template template-phase3.yaml  # ❌ Will fail on macOS
```

**DO:**
```bash
sam build --template template-phase3.yaml --use-container  # ✅ Works everywhere
```

### ✅ Test Order

1. **Local tests first** (no deployment needed):
   ```bash
   python test_chunking_local.py
   python test_retry_logic.py
   ```

2. **Deploy to AWS**:
   ```bash
   sam build --use-container
   sam deploy
   ```

3. **Test deployed API**:
   ```bash
   python test_phase3_final.py $API_ENDPOINT
   ```

### ✅ Avoid AWS Throttling

Your account has a **10 concurrent Lambda limit**.

**DON'T:**
```bash
python test_retry_under_load.py $API_ENDPOINT 30 15  # ❌ 15 workers = throttling
```

**DO:**
```bash
python test_retry_under_load.py $API_ENDPOINT 30 5   # ✅ 5 workers = no throttling
```

---

## Cost Monitoring

```bash
# Check Lambda invocations (last 7 days)
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=doc-generator-phase3-dev \
  --start-time $(date -u -d '7 days ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 86400 \
  --statistics Sum \
  --region ap-south-1
```

---

## Troubleshooting Quick Fixes

### Issue: Decimal Serialization Error
**Solution:** Already fixed in code (decimal_to_float helper)

### Issue: 500 errors under load  
**Solution:** Reduce concurrent workers to 3-5

### Issue: Binary dependency error
**Solution:** Use `--use-container` flag

### Issue: Stack already exists
**Solution:** Delete old stack first
```bash
aws cloudformation delete-stack --stack-name doc-generator-phase3
```

---

**For detailed documentation, see [PHASE3-COMPLETE.md](PHASE3-COMPLETE.md)**
