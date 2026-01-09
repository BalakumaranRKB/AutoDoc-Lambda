#!/usr/bin/env python3
"""
Check CloudWatch logs for retry behavior
"""
import boto3
import time
from datetime import datetime

def check_retry_logs():
    """Check CloudWatch logs for retry activity."""
    
    logs = boto3.client('logs', region_name='ap-south-1')
    log_group = '/aws/lambda/doc-generator-phase3-dev'
    
    print("=" * 80)
    print("RETRY LOGIC - CLOUDWATCH LOGS")
    print("=" * 80)
    print()
    
    try:
        # Get most recent log stream
        streams_response = logs.describe_log_streams(
            logGroupName=log_group,
            orderBy='LastEventTime',
            descending=True,
            limit=5
        )
        
        if not streams_response.get('logStreams'):
            print("❌ No log streams found")
            return
        
        print(f"Checking last 5 log streams...")
        print()
        
        # Check multiple recent streams (concurrent requests)
        retry_count = 0
        error_count = 0
        timeout_count = 0
        rate_limit_count = 0
        
        all_events = []
        
        for stream in streams_response['logStreams'][:5]:
            stream_name = stream['logStreamName']
            
            start_time = int((time.time() - 300) * 1000)  # Last 5 minutes
            
            events_response = logs.get_log_events(
                logGroupName=log_group,
                logStreamName=stream_name,
                startTime=start_time,
                limit=100
            )
            
            all_events.extend(events_response.get('events', []))
        
        # Analyze all events
        for event in all_events:
            message = event['message']
            
            if 'Retrying in' in message or 'retry' in message.lower():
                retry_count += 1
                print(f"🔄 {message.strip()}")
            
            if 'ERROR' in message or 'Error' in message:
                error_count += 1
                if '429' in message or 'rate limit' in message.lower():
                    rate_limit_count += 1
                if 'timeout' in message.lower() or 'timed out' in message.lower():
                    timeout_count += 1
                print(f"❌ {message.strip()}")
        
        print()
        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print()
        print(f"Total events analyzed: {len(all_events)}")
        print(f"Retry attempts found: {retry_count}")
        print(f"Errors found: {error_count}")
        print(f"  - Rate limits (429): {rate_limit_count}")
        print(f"  - Timeouts: {timeout_count}")
        print()
        
        if retry_count == 0:
            print("⚠️  NO RETRIES DETECTED!")
            print()
            print("Possible issues:")
            print("  1. Retry logic not being called")
            print("  2. Errors are non-retryable (400, 401, etc.)")
            print("  3. Lambda timing out before retry can happen")
            print("  4. Retry logic import/initialization error")
            print()
            print("Let's check for import errors...")
            
            import_errors = [e for e in all_events if 'import' in e['message'].lower() or 'module' in e['message'].lower()]
            if import_errors:
                print()
                print("❌ IMPORT ERRORS FOUND:")
                for err in import_errors[:5]:
                    print(f"  {err['message'].strip()}")
            else:
                print("  ✅ No import errors")
        
        else:
            print(f"✅ Retry logic IS working ({retry_count} retry attempts)")
            print()
            print("Analysis:")
            if timeout_count > rate_limit_count:
                print("  • Main issue: Lambda timeouts")
                print("  • Retries take time, may exceed 5-min Lambda limit")
            elif rate_limit_count > 0:
                print("  • Rate limits being hit and retried")
                print(f"  • But still {error_count - retry_count} failures after retries")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    check_retry_logs()
