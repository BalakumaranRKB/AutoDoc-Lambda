#!/usr/bin/env python3
"""
Debug Phase 3 deployment issues
"""
import boto3
import json
import sys

def get_stack_info():
    """Get info about deployed stacks."""
    cf = boto3.client('cloudformation')
    
    print("Looking for deployed stacks...")
    print()
    
    try:
        response = cf.list_stacks(
            StackStatusFilter=['CREATE_COMPLETE', 'UPDATE_COMPLETE']
        )
        
        doc_stacks = [s for s in response['StackSummaries'] 
                     if 'doc' in s['StackName'].lower()]
        
        if not doc_stacks:
            print("❌ No documentation generator stacks found")
            return None
        
        print(f"Found {len(doc_stacks)} stack(s):")
        for stack in doc_stacks:
            print(f"  - {stack['StackName']}")
        print()
        
        # Get details of first stack
        stack_name = doc_stacks[0]['StackName']
        print(f"Getting details for: {stack_name}")
        print()
        
        response = cf.describe_stacks(StackName=stack_name)
        stack = response['Stacks'][0]
        
        # Print outputs
        print("Stack Outputs:")
        for output in stack.get('Outputs', []):
            print(f"  {output['OutputKey']}: {output['OutputValue']}")
        print()
        
        # Get function name
        function_name = None
        for output in stack.get('Outputs', []):
            if 'Function' in output['OutputKey']:
                function_name = output['OutputValue']
                break
        
        return {
            'stack_name': stack_name,
            'function_name': function_name,
            'outputs': {o['OutputKey']: o['OutputValue'] for o in stack.get('Outputs', [])}
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def check_lambda_function(function_name):
    """Check Lambda function configuration."""
    lambda_client = boto3.client('lambda')
    
    print(f"Checking Lambda function: {function_name}")
    print()
    
    try:
        response = lambda_client.get_function(FunctionName=function_name)
        config = response['Configuration']
        
        print("Function Configuration:")
        print(f"  Runtime: {config['Runtime']}")
        print(f"  Memory: {config['MemorySize']} MB")
        print(f"  Timeout: {config['Timeout']} seconds")
        print(f"  Last Modified: {config['LastModified']}")
        print()
        
        print("Environment Variables:")
        env_vars = config.get('Environment', {}).get('Variables', {})
        for key in sorted(env_vars.keys()):
            if 'KEY' in key or 'SECRET' in key:
                print(f"  {key}: ***HIDDEN***")
            else:
                print(f"  {key}: {env_vars[key]}")
        print()
        
        # Check for missing vars
        required_vars = [
            'ANTHROPIC_API_KEY',
            'CACHE_TABLE_NAME',
            'COST_PER_1M_INPUT_TOKENS',
            'COST_PER_1M_OUTPUT_TOKENS'
        ]
        
        missing = [v for v in required_vars if v not in env_vars]
        if missing:
            print(f"⚠️  Missing environment variables: {', '.join(missing)}")
        else:
            print("✅ All required environment variables present")
        print()
        
        return config
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def get_recent_logs(function_name, minutes=5):
    """Get recent Lambda logs."""
    logs_client = boto3.client('logs')
    log_group = f'/aws/lambda/{function_name}'
    
    print(f"Fetching logs from: {log_group}")
    print(f"Last {minutes} minutes")
    print()
    
    try:
        # Get log streams
        response = logs_client.describe_log_streams(
            logGroupName=log_group,
            orderBy='LastEventTime',
            descending=True,
            limit=5
        )
        
        if not response.get('logStreams'):
            print("❌ No log streams found")
            return
        
        # Get events from most recent stream
        stream_name = response['logStreams'][0]['logStreamName']
        
        import time
        start_time = int((time.time() - minutes * 60) * 1000)
        
        response = logs_client.get_log_events(
            logGroupName=log_group,
            logStreamName=stream_name,
            startTime=start_time,
            limit=50
        )
        
        events = response.get('events', [])
        
        if not events:
            print("No recent log events found")
            return
        
        print(f"Recent logs ({len(events)} events):")
        print("=" * 80)
        for event in events[-20:]:  # Last 20 events
            message = event['message'].strip()
            print(message)
        print("=" * 80)
        print()
        
        # Check for errors
        errors = [e for e in events if 'ERROR' in e['message'] or 'Error' in e['message']]
        if errors:
            print(f"⚠️  Found {len(errors)} error(s):")
            for error in errors[-5:]:
                print(f"  {error['message'].strip()}")
        
    except logs_client.exceptions.ResourceNotFoundException:
        print(f"❌ Log group not found: {log_group}")
        print("   The function may not have been invoked yet")
    except Exception as e:
        print(f"❌ Error fetching logs: {e}")


def check_dynamodb_table(table_name):
    """Check DynamoDB table."""
    dynamodb = boto3.client('dynamodb')
    
    print(f"Checking DynamoDB table: {table_name}")
    print()
    
    try:
        response = dynamodb.describe_table(TableName=table_name)
        table = response['Table']
        
        print("Table Status:")
        print(f"  Status: {table['TableStatus']}")
        print(f"  Item Count: {table['ItemCount']}")
        print(f"  Size: {table['TableSizeBytes']} bytes")
        
        # Check TTL
        ttl_response = dynamodb.describe_time_to_live(TableName=table_name)
        ttl_status = ttl_response['TimeToLiveDescription']['TimeToLiveStatus']
        print(f"  TTL Status: {ttl_status}")
        print()
        
        if ttl_status != 'ENABLED':
            print("⚠️  TTL is not enabled!")
        else:
            print("✅ TTL is enabled")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    print("=" * 80)
    print("PHASE 3 DEPLOYMENT DEBUGGER")
    print("=" * 80)
    print()
    
    # Get stack info
    info = get_stack_info()
    if not info:
        print("Could not find stack information")
        return
    
    function_name = info['function_name']
    if not function_name:
        print("Could not determine function name")
        print("Available outputs:", info['outputs'])
        return
    
    # Check Lambda
    config = check_lambda_function(function_name)
    if not config:
        return
    
    # Check DynamoDB
    env_vars = config.get('Environment', {}).get('Variables', {})
    table_name = env_vars.get('CACHE_TABLE_NAME')
    if table_name:
        check_dynamodb_table(table_name)
    else:
        print("⚠️  No CACHE_TABLE_NAME in environment variables")
    
    print()
    
    # Get logs
    get_recent_logs(function_name, minutes=10)
    
    print()
    print("=" * 80)
    print("COMMON ISSUES:")
    print("=" * 80)
    print()
    print("1. Missing dependencies in Lambda layer")
    print("   → Check that phase3_production has all .py files")
    print()
    print("2. Import errors")
    print("   → Look for 'ModuleNotFoundError' in logs above")
    print()
    print("3. Missing environment variables")
    print("   → Check ANTHROPIC_API_KEY is set")
    print()
    print("4. DynamoDB permissions")
    print("   → Check Lambda role has dynamodb:GetItem, PutItem")
    print()


if __name__ == "__main__":
    main()
