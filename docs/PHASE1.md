# Phase 1: POC - Simple Documentation Generator

Complete guide for Phase 1: Building a simple proof-of-concept that generates documentation for Python files using Claude API.

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Components](#components)
- [Deployment](#deployment)
- [Testing](#testing)
- [Limitations](#limitations)

---

## Overview

Phase 1 builds the simplest possible documentation generator:
- **Input:** Python file (path + content)
- **Process:** Analyze code structure → Call Claude API → Track costs
- **Output:** Markdown documentation + metrics

**Goal:** Prove the concept works before adding complexity.

**What Works:**
- Single Python files up to ~5,000 lines
- Generates comprehensive documentation
- Tracks token usage and costs
- Returns results in <60 seconds

**What Doesn't:**
- No caching (every request calls Claude)
- No chunking (large files timeout)
- No retry logic (failures just fail)
- No authentication

These limitations are intentional - Phase 2 exposes them, Phase 3 fixes them.

---

## Architecture

### System Overview

```
Client → API Gateway → Lambda → Claude API
                         ↓
                   CloudWatch Logs
```

### Request Flow

```
1. Client sends POST request with file_path and file_content
2. API Gateway validates and forwards to Lambda
3. Lambda:
   a. Parses request body
   b. Validates Python file (.py extension)
   c. Analyzes code structure (AST parsing)
   d. Calls Claude API with structured prompt
   e. Calculates costs from token usage
   f. Returns documentation + metrics
4. Client receives JSON response
```

### Complete Data Flow Example

```
Input:
{
  "file_path": "calculator.py",
  "file_content": "def add(a, b):\n    return a + b"
}

↓ API Gateway validates

↓ Lambda receives event

↓ PythonCodeAnalyzer extracts:
  - 2 lines of code
  - 1 function: add(a, b)
  - 0 comments

↓ ClaudeClient builds prompt:
  "Generate documentation for this Python code..."
  
↓ Claude API processes (takes ~3 seconds)
  - Input tokens: 421
  - Output tokens: 589
  
↓ CostTracker calculates:
  - Input cost: $0.0013
  - Output cost: $0.0088
  - Total: $0.0101
  
↓ Response returned:
{
  "success": true,
  "data": {
    "documentation": "# Calculator Module...",
    "total_cost": 0.0101,
    "total_tokens": 1010,
    "processing_time_seconds": 2.3
  }
}
```

---

## Components

### 1. API Gateway
- **Purpose:** HTTP interface for clients
- **Endpoint:** POST /document
- **CORS:** Enabled for web clients
- **Auth:** None (Phase 1 only!)

### 2. Lambda Function (512MB, 5min timeout)

**Main Handler:**
```python
def lambda_handler(event, context):
    # 1. Parse request
    # 2. Validate Python file
    # 3. Generate documentation
    # 4. Return response
```

**Environment Variables:**
- `ANTHROPIC_API_KEY` - Claude API key
- `COST_PER_1M_INPUT_TOKENS` - $3.00
- `COST_PER_1M_OUTPUT_TOKENS` - $15.00
- `CLAUDE_MODEL` - claude-sonnet-4-20250514
- `MAX_TOKENS` - 4096
- `TEMPERATURE` - 0.0

### 3. PythonCodeAnalyzer

Parses Python source using AST:
- Extracts functions, classes, methods
- Counts lines (code, comments, blank)
- Identifies imports
- Gets parameter types and return types

**Output:** FileAnalysis object with structure

### 4. ClaudeClient

Wraps Claude API:
- Builds structured prompts
- Calls Claude Sonnet 4
- Parses markdown documentation
- Calculates token costs

**Prompt Structure:**
```
You are an expert technical writer.
Generate documentation for this Python code:

[code here]

Include:
1. File overview
2. Function/class documentation
3. Dependencies
4. Code quality notes
```

### 5. CostTracker

Tracks spending:
- Per-file costs
- Total tokens used
- Input vs output token breakdown
- Logs to CloudWatch

**Typical Costs:**
- 1,000 lines: ~$0.02 USD (~₹1.60 INR)
- 5,000 lines: ~$0.10 USD (~₹8.00 INR)

---

## Deployment

### Prerequisites

1. **Install AWS SAM CLI:**
   ```bash
   brew install aws-sam-cli  # macOS
   ```

2. **Configure AWS:**
   ```bash
   aws configure
   ```

3. **Get Anthropic API Key:**
   - https://console.anthropic.com/settings/keys

### Deploy to AWS

```bash
# 1. Navigate to SAM directory
cd infrastructure/sam

# 2. Update samconfig.toml with your API key
# Replace YOUR_ANTHROPIC_API_KEY_HERE with actual key

# 3. Build
sam build

# 4. Deploy
sam deploy --guided
# Follow prompts, accept defaults

# 5. Get API endpoint from outputs
```

### Test Deployment

```bash
# Set your endpoint
API_ENDPOINT="https://YOUR-ID.execute-api.REGION.amazonaws.com/dev/document"

# Test
curl -X POST $API_ENDPOINT \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "test.py",
    "file_content": "def hello():\n    return \"world\""
  }'
```

**Expected:** JSON response with documentation, cost, tokens.

### Local Testing

```bash
# Start local API (requires Docker)
cd infrastructure/sam
sam build
sam local start-api

# Test locally
curl -X POST http://localhost:3000/document \
  -H "Content-Type: application/json" \
  -d '{"file_path": "test.py", "file_content": "..."}'
```

### Update Deployment

```bash
# After code changes
sam build
sam deploy
```

### Delete Everything

```bash
sam delete --stack-name doc-generator-phase1
```

---

## Testing

### Unit Tests

```bash
pytest tests/unit/
```

### Integration Test

```python
import requests

response = requests.post(API_ENDPOINT, json={
    "file_path": "calculator.py",
    "file_content": """
class Calculator:
    def add(self, a, b):
        return a + b
    """
})

print(response.json())
```

### Verify Costs

Check CloudWatch logs for cost tracking:
```
/aws/lambda/doc-generator-dev
```

Look for lines like:
```
Cost: $0.0101 USD (₹0.84 INR)
Tokens: 1010 (421 input, 589 output)
```

---

## Limitations

### Performance
- ❌ **Single file only** - Can't process repositories
- ❌ **Sequential processing** - No parallelization
- ❌ **5-minute timeout** - Large files (>5,000 lines) fail
- ❌ **512MB memory** - Complex files may hit limit

### Cost
- ❌ **No caching** - Same file = same cost every time
- ❌ **No chunking** - Large files = expensive prompts
- ❌ **Unoptimized** - Prompts could be more efficient

### Reliability
- ❌ **No retries** - API failures just fail
- ❌ **No circuit breaker** - Keep hitting failing API
- ❌ **No graceful degradation** - All-or-nothing

### Security
- ❌ **No authentication** - Anyone can use API
- ❌ **No rate limiting** - Can be abused
- ❌ **API key in env vars** - Not Secrets Manager

**Why we accept these:** Phase 1 is a POC. These become problems in Phase 2, teaching why production systems need better patterns.

---

## Success Criteria

Phase 1 is complete when:

✅ Can analyze Python files and extract structure  
✅ Can generate documentation using Claude  
✅ Can track costs accurately  
✅ Returns well-formatted JSON responses  
✅ Works for files up to 5,000 lines  
✅ Average processing time <60 seconds  
✅ Documentation is readable and helpful  

---

## Next Steps

After Phase 1:
1. Use the frontend (`frontend/index.html`) to test visually
2. Try documenting real Python files
3. Monitor costs in CloudWatch
4. Move to Phase 2 to see what breaks!

---

## Resources

- **SAM Template:** `infrastructure/sam/template.yaml`
- **Lambda Code:** `src/phase1_poc/`
- **Frontend UI:** `frontend/index.html`
- **Architecture Diagrams:** `docs/architecture/diagrams/`

## Quick Commands

```bash
# Build locally
sam build

# Test locally
sam local start-api

# Deploy
sam deploy

# View logs
sam logs --tail

# Delete
sam delete
```

That's Phase 1! Simple, working, intentionally limited. Perfect POC.
