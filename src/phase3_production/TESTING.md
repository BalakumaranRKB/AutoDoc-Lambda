# Testing Phase 3 Deployment

Quick guide to test your Phase 3 deployment with caching.

## Step 1: Get Your API Endpoint

```bash
# Option 1: From SAM deploy output
# Look for "ApiEndpoint" in the deploy output

# Option 2: From CloudFormation
aws cloudformation describe-stacks \
  --stack-name YOUR_STACK_NAME \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
  --output text

# Option 3: List all stacks first
aws cloudformation list-stacks \
  --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE \
  --query 'StackSummaries[*].StackName' \
  --output table
```

## Step 2: Run the Test

```bash
cd src/phase3_production

# Replace with your actual endpoint
python test_phase3.py https://YOUR-API-ID.execute-api.REGION.amazonaws.com/dev/document
```

## What the Test Does

1. **First Request (Cache MISS)**
   - Sends Python code to API
   - Should call Claude API
   - Cost: ~$0.01-0.02
   - Time: ~3-5 seconds
   - Saves to DynamoDB cache

2. **Second Request (Cache HIT)**
   - Sends IDENTICAL code
   - Should retrieve from cache
   - Cost: **$0.00** ✅
   - Time: <1 second ⚡
   - No Claude API call

3. **Verification**
   - Compares costs
   - Calculates savings %
   - Measures speed improvement
   - Shows checklist

## Expected Output

```
==================================================
TEST 1: First Request (should be Cache MISS)
==================================================

✅ SUCCESS
   Status Code: 200
   Time: 3.42 seconds
   Cached: False
   Cost: $0.012000
   Tokens: 1,245

✅ PASS: Cache MISS as expected

==================================================
TEST 2: Second Request (should be Cache HIT)
==================================================

✅ SUCCESS
   Status Code: 200
   Time: 0.15 seconds
   Cached: True
   Cost: $0.000000
   Tokens: 1,245

✅ PASS: Cache HIT!
   Speed improvement: 22.8x faster

==================================================
TEST SUMMARY
==================================================

💰 COST SAVINGS:
   Saved: $0.012000 (100.0%)
   In INR: ₹0.9960

⚡ PERFORMANCE:
   Speedup: 22.8x faster with cache
   
✅ EXCELLENT: ~100% cost reduction on cache hit!
```

## Troubleshooting

### "Connection refused" or "Network error"
- Check your API endpoint URL is correct
- Ensure the stack deployed successfully
- Verify the endpoint is accessible

### "Internal Server Error (500)"
- Check CloudWatch logs:
  ```bash
  aws logs tail /aws/lambda/YOUR-FUNCTION-NAME --follow
  ```
- Verify environment variables are set
- Check DynamoDB table exists

### Cache always MISS
- Check DynamoDB table name in Lambda env vars
- Verify Lambda has DynamoDB permissions
- Check CloudWatch logs for errors

### How to check CloudWatch logs

```bash
# Get function name
aws cloudformation describe-stacks \
  --stack-name YOUR_STACK_NAME \
  --query 'Stacks[0].Outputs[?OutputKey==`FunctionName`].OutputValue' \
  --output text

# Tail logs
aws logs tail /aws/lambda/FUNCTION_NAME --follow
```

## Manual Testing with curl

```bash
# Set your endpoint
API_ENDPOINT="https://YOUR-ID.execute-api.REGION.amazonaws.com/dev/document"

# Test request
curl -X POST $API_ENDPOINT \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "test.py",
    "file_content": "def hello():\n    return \"world\""
  }'
```

## Check DynamoDB Cache

```bash
# Get table name
aws cloudformation describe-stacks \
  --stack-name YOUR_STACK_NAME \
  --query 'Stacks[0].Outputs[?OutputKey==`CacheTableName`].OutputValue' \
  --output text

# Scan table (see cached items)
aws dynamodb scan --table-name doc-cache-dev --max-items 5
```

## Success Criteria

Your Phase 3 is working if:

✅ First request costs $0.01-0.02  
✅ Second identical request costs $0.00  
✅ Second request returns `"cached": true`  
✅ Cache hits are 10-30x faster  
✅ DynamoDB has cached items  
✅ CloudWatch shows cache HIT/MISS logs  

## Next Steps

After confirming caching works:
1. Update the frontend to show cache status
2. Test with different files
3. Monitor DynamoDB in AWS Console
4. Check CloudWatch dashboard
5. Calculate actual cost savings

Good luck! 🚀
