#!/usr/bin/env python3
"""
Check CloudWatch logs for Phase 3 Lambda
"""
import boto3
import time
from datetime import datetime, timedelta

def get_recent_logs():
    """Get recent Lambda logs to debug caching."""
    
    logs = boto3.client('logs', region_name='ap-south-1')
    log_group = '/aws/lambda/doc-generator-phase3-dev'
    
    print("=" * 80)
    print("PHASE 3 LAMBDA LOGS (Last 5 minutes)")
    print("=" * 80)
    print()
    
    try:
        # Get log streams
        streams_response = logs.describe_log_streams(
            logGroupName=log_group,
            orderBy='LastEventTime',
            descending=True,
            limit=3
        )
        
        if not streams_response.get('logStreams'):
            print("❌ No log streams found")
            return
        
        # Get events from most recent stream
        stream_name = streams_response['logStreams'][0]['logStreamName']
        
        start_time = int((time.time() - 300) * 1000)  # Last 5 minutes
        
        events_response = logs.get_log_events(
            logGroupName=log_group,
            logStreamName=stream_name,
            startTime=start_time,
            limit=100
        )
        
        events = events_response.get('events', [])
        
        if not events:
            print("No recent events found")
            return
        
        print(f"Found {len(events)} log events:")
        print("=" * 80)
        
        # Print all events
        for event in events:
            timestamp = datetime.fromtimestamp(event['timestamp'] / 1000)
            message = event['message'].strip()
            print(f"[{timestamp.strftime('%H:%M:%S')}] {message}")
        
        print("=" * 80)
        print()
        
        # Look for cache-related messages
        cache_hits = [e for e in events if 'Cache HIT' in e['message']]
        cache_misses = [e for e in events if 'Cache MISS' in e['message']]
        errors = [e for e in events if 'ERROR' in e['message'] or 'Error' in e['message']]
        
        print("SUMMARY:")
        print(f"  Cache HITs:   {len(cache_hits)}")
        print(f"  Cache MISSes: {len(cache_misses)}")
        print(f"  Errors:       {len(errors)}")
        print()
        
        if errors:
            print("ERRORS FOUND:")
            for error in errors[-5:]:
                print(f"  {error['message'].strip()}")
            print()
        
        # Look for hash calculations
        hash_logs = [e for e in events if 'File hash' in e['message']]
        if hash_logs:
            print("FILE HASHES:")
            for log in hash_logs:
                print(f"  {log['message'].strip()}")
            print()
        
        # Look for DynamoDB operations
        dynamodb_logs = [e for e in events if 'DynamoDB' in e['message'] or 'cache' in e['message'].lower()]
        if dynamodb_logs:
            print("CACHE OPERATIONS:")
            for log in dynamodb_logs[-10:]:
                print(f"  {log['message'].strip()}")
            print()
        
    except logs.exceptions.ResourceNotFoundException:
        print(f"❌ Log group not found: {log_group}")
        print()
        print("Make sure the function name is correct.")
        print("Check CloudFormation outputs for the exact function name.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    get_recent_logs()
