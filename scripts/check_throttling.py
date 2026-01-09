#!/usr/bin/env python3
"""
Check Lambda concurrency limits and throttling
"""
import boto3
from datetime import datetime, timedelta

def check_lambda_throttling():
    """Check if Lambda is being throttled."""
    
    print("=" * 80)
    print("LAMBDA THROTTLING CHECK")
    print("=" * 80)
    print()
    
    # Check Lambda function config
    lambda_client = boto3.client('lambda', region_name='ap-south-1')
    function_name = 'doc-generator-phase3-dev'
    
    try:
        # Get function config
        response = lambda_client.get_function(FunctionName=function_name)
        config = response['Configuration']
        
        # Check concurrency settings
        reserved_concurrent = config.get('ReservedConcurrentExecutions', 'Unreserved')
        
        print(f"Function: {function_name}")
        print(f"Reserved Concurrency: {reserved_concurrent}")
        print()
        
        # Get account-level concurrency
        account_settings = lambda_client.get_account_settings()
        account_limit = account_settings['AccountLimit']['ConcurrentExecutions']
        account_usage = account_settings['AccountUsage']['FunctionCount']
        
        print(f"Account Limit: {account_limit} concurrent executions")
        print(f"Functions in account: {account_usage}")
        print()
        
    except Exception as e:
        print(f"Error getting Lambda config: {e}")
        print()
    
    # Check CloudWatch metrics for throttling
    cloudwatch = boto3.client('cloudwatch', region_name='ap-south-1')
    
    try:
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=10)
        
        print("Checking CloudWatch metrics (last 10 minutes)...")
        print()
        
        # Get throttles
        throttles = cloudwatch.get_metric_statistics(
            Namespace='AWS/Lambda',
            MetricName='Throttles',
            Dimensions=[{'Name': 'FunctionName', 'Value': function_name}],
            StartTime=start_time,
            EndTime=end_time,
            Period=60,
            Statistics=['Sum']
        )
        
        # Get concurrent executions
        concurrent = cloudwatch.get_metric_statistics(
            Namespace='AWS/Lambda',
            MetricName='ConcurrentExecutions',
            Dimensions=[{'Name': 'FunctionName', 'Value': function_name}],
            StartTime=start_time,
            EndTime=end_time,
            Period=60,
            Statistics=['Maximum']
        )
        
        # Get invocations
        invocations = cloudwatch.get_metric_statistics(
            Namespace='AWS/Lambda',
            MetricName='Invocations',
            Dimensions=[{'Name': 'FunctionName', 'Value': function_name}],
            StartTime=start_time,
            EndTime=end_time,
            Period=60,
            Statistics=['Sum']
        )
        
        # Get errors
        errors = cloudwatch.get_metric_statistics(
            Namespace='AWS/Lambda',
            MetricName='Errors',
            Dimensions=[{'Name': 'FunctionName', 'Value': function_name}],
            StartTime=start_time,
            EndTime=end_time,
            Period=60,
            Statistics=['Sum']
        )
        
        # Analyze
        total_throttles = sum(point['Sum'] for point in throttles.get('Datapoints', []))
        max_concurrent = max([point['Maximum'] for point in concurrent.get('Datapoints', [])], default=0)
        total_invocations = sum(point['Sum'] for point in invocations.get('Datapoints', []))
        total_errors = sum(point['Sum'] for point in errors.get('Datapoints', []))
        
        print(f"Total Invocations: {total_invocations}")
        print(f"Total Errors: {total_errors}")
        print(f"Total Throttles: {total_throttles}")
        print(f"Max Concurrent Executions: {max_concurrent}")
        print()
        
        if total_throttles > 0:
            print("❌ THROTTLING DETECTED!")
            print(f"   {total_throttles} requests were throttled")
            print()
            print("   This means:")
            print("   • Too many concurrent Lambda invocations")
            print("   • Hit account or function concurrency limit")
            print("   • API Gateway returns 500 when Lambda is throttled")
            print()
            print("   Solutions:")
            print("   1. Reduce concurrent requests (use fewer workers)")
            print("   2. Increase reserved concurrency for this function")
            print("   3. Request AWS to increase account limit")
            print()
        else:
            print("✅ No throttling detected")
            print()
            
            if total_errors > 0:
                print(f"⚠️  But {total_errors} errors occurred")
                print("   These errors are NOT logged (strange!)")
                print("   Possible causes:")
                print("   • Lambda crashes before logging")
                print("   • Out of memory")
                print("   • Import errors at initialization")
                print()
        
    except Exception as e:
        print(f"Error getting CloudWatch metrics: {e}")


if __name__ == "__main__":
    check_lambda_throttling()
