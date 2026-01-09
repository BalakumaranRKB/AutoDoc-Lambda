#!/usr/bin/env python3
"""
Detailed CloudWatch log analysis for recent errors
"""
import boto3
import time
from datetime import datetime
from collections import Counter

def analyze_errors():
    """Deep dive into what errors are occurring."""
    
    logs = boto3.client('logs', region_name='ap-south-1')
    log_group = '/aws/lambda/doc-generator-phase3-dev'
    
    print("=" * 80)
    print("DETAILED ERROR ANALYSIS")
    print("=" * 80)
    print()
    
    try:
        # Get recent log streams
        streams_response = logs.describe_log_streams(
            logGroupName=log_group,
            orderBy='LastEventTime',
            descending=True,
            limit=10
        )
        
        if not streams_response.get('logStreams'):
            print("❌ No log streams found")
            return
        
        all_events = []
        start_time = int((time.time() - 600) * 1000)  # Last 10 minutes
        
        print(f"Analyzing last 10 log streams (last 10 minutes)...")
        print()
        
        for stream in streams_response['logStreams'][:10]:
            stream_name = stream['logStreamName']
            
            events_response = logs.get_log_events(
                logGroupName=log_group,
                logStreamName=stream_name,
                startTime=start_time,
                limit=100
            )
            
            all_events.extend(events_response.get('events', []))
        
        print(f"Total events: {len(all_events)}")
        print()
        
        # Categorize errors
        errors = []
        retries = []
        successes = []
        imports = []
        timeouts = []
        
        for event in all_events:
            msg = event['message']
            
            if 'ERROR' in msg or 'Error' in msg or 'error' in msg:
                errors.append(msg.strip())
            
            if 'Retrying in' in msg or '🔄' in msg:
                retries.append(msg.strip())
            
            if 'SUCCESS' in msg or '✅' in msg or 'Success on attempt' in msg:
                successes.append(msg.strip())
            
            if 'import' in msg.lower() or 'module' in msg.lower():
                imports.append(msg.strip())
            
            if 'timed out' in msg.lower() or 'timeout' in msg.lower():
                timeouts.append(msg.strip())
        
        # Print summary
        print("CATEGORY BREAKDOWN:")
        print(f"  Errors:    {len(errors)}")
        print(f"  Retries:   {len(retries)}")
        print(f"  Successes: {len(successes)}")
        print(f"  Imports:   {len(imports)}")
        print(f"  Timeouts:  {len(timeouts)}")
        print()
        
        # Show recent errors
        if errors:
            print("=" * 80)
            print("RECENT ERRORS (Last 10):")
            print("=" * 80)
            for error in errors[-10:]:
                # Truncate long errors
                if len(error) > 200:
                    print(f"  {error[:200]}...")
                else:
                    print(f"  {error}")
            print()
        
        # Show retry attempts
        if retries:
            print("=" * 80)
            print(f"RETRY ATTEMPTS DETECTED: {len(retries)}")
            print("=" * 80)
            for retry in retries[:10]:
                print(f"  {retry}")
            print()
        else:
            print("=" * 80)
            print("⚠️  NO RETRY ATTEMPTS FOUND")
            print("=" * 80)
            print()
            print("This means:")
            print("  1. Errors are not retryable (400, 401, etc.)")
            print("  2. Retry decorator not being called")
            print("  3. Exceptions not matching retry conditions")
            print()
        
        # Check for specific error patterns
        print("=" * 80)
        print("ERROR PATTERN ANALYSIS:")
        print("=" * 80)
        
        error_types = Counter()
        for error in errors:
            if 'ModuleNotFoundError' in error or 'ImportError' in error:
                error_types['Import Error'] += 1
            elif '429' in error or 'rate limit' in error.lower():
                error_types['Rate Limit (429)'] += 1
            elif 'timeout' in error.lower() or 'timed out' in error.lower():
                error_types['Timeout'] += 1
            elif 'Task timed out' in error:
                error_types['Lambda Timeout'] += 1
            elif 'Decimal' in error:
                error_types['Decimal Serialization'] += 1
            elif 'HTTPStatusError' in error:
                error_types['HTTP Error'] += 1
            elif 'Authentication' in error or 'API key' in error:
                error_types['Auth Error'] += 1
            else:
                error_types['Other'] += 1
        
        for error_type, count in error_types.most_common():
            print(f"  {error_type}: {count}")
        print()
        
        # Diagnosis
        print("=" * 80)
        print("DIAGNOSIS:")
        print("=" * 80)
        
        if error_types.get('Import Error', 0) > 0:
            print("❌ IMPORT ERRORS DETECTED")
            print("   → Missing retry_logic module or dependency")
            print("   → Check SAM build included all files")
            
        elif error_types.get('Lambda Timeout', 0) > 0:
            print("⏱️  LAMBDA TIMEOUTS DETECTED")
            print("   → Functions running >300 seconds")
            print("   → Retries may be causing this (each retry adds delay)")
            
        elif len(retries) > 0:
            print("✅ RETRY LOGIC IS WORKING")
            print(f"   → {len(retries)} retry attempts logged")
            print(f"   → But still {len(errors)} errors total")
            print("   → May need more retry attempts or longer timeout")
            
        else:
            print("⚠️  RETRY LOGIC NOT TRIGGERING")
            print("   → Check exception types being raised")
            print("   → Verify httpx exceptions are caught")
            print("   → Look for 'Checking if should retry' logs")
        
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    analyze_errors()
