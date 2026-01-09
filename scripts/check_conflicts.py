#!/usr/bin/env python3
"""
Check for existing resources that might conflict
"""
import boto3
import sys

def check_existing_resources():
    """Check for existing stacks and resources."""
    
    # Check CloudFormation stacks
    print("Checking CloudFormation stacks...")
    cf = boto3.client('cloudformation', region_name='ap-south-1')
    
    try:
        response = cf.list_stacks(
            StackStatusFilter=[
                'CREATE_IN_PROGRESS',
                'CREATE_FAILED',
                'CREATE_COMPLETE',
                'ROLLBACK_IN_PROGRESS',
                'ROLLBACK_FAILED',
                'ROLLBACK_COMPLETE',
                'DELETE_IN_PROGRESS',
                'DELETE_FAILED',
                'UPDATE_IN_PROGRESS',
                'UPDATE_COMPLETE_CLEANUP_IN_PROGRESS',
                'UPDATE_COMPLETE',
                'UPDATE_FAILED',
                'UPDATE_ROLLBACK_IN_PROGRESS',
                'UPDATE_ROLLBACK_FAILED',
                'UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS',
                'UPDATE_ROLLBACK_COMPLETE'
            ]
        )
        
        doc_stacks = [s for s in response['StackSummaries'] 
                     if 'doc-generator' in s['StackName'].lower()]
        
        if doc_stacks:
            print("\nFound existing stacks:")
            for stack in doc_stacks:
                print(f"  - {stack['StackName']} ({stack['StackStatus']})")
        else:
            print("  No existing doc-generator stacks found")
            
    except Exception as e:
        print(f"  Error checking stacks: {e}")
    
    # Check DynamoDB tables
    print("\nChecking DynamoDB tables...")
    dynamodb = boto3.client('dynamodb', region_name='ap-south-1')
    
    try:
        response = dynamodb.list_tables()
        cache_tables = [t for t in response['TableNames'] if 'doc-cache' in t.lower()]
        
        if cache_tables:
            print("  Found existing cache tables:")
            for table in cache_tables:
                print(f"    - {table}")
                
                # Get table details
                table_info = dynamodb.describe_table(TableName=table)
                status = table_info['Table']['TableStatus']
                print(f"      Status: {status}")
        else:
            print("  No existing doc-cache tables found")
            
    except Exception as e:
        print(f"  Error checking tables: {e}")
    
    # Check for failed changesets
    print("\nChecking for failed changesets...")
    try:
        response = cf.list_change_sets(StackName='doc-generator-phase3')
        for cs in response.get('Summaries', []):
            if cs['Status'] == 'FAILED':
                print(f"  Found failed changeset: {cs['ChangeSetName']}")
                print(f"    Status: {cs['Status']}")
                print(f"    Reason: {cs.get('StatusReason', 'N/A')}")
    except cf.exceptions.ChangeSetNotFoundException:
        print("  No changesets found for doc-generator-phase3")
    except Exception as e:
        print(f"  Error: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("Checking for conflicting AWS resources")
    print("=" * 60)
    print()
    check_existing_resources()
    print()
    print("=" * 60)
    print("\nRecommendations:")
    print("1. If doc-cache-dev table exists, delete it or use different name")
    print("2. If doc-generator-phase3 stack exists in FAILED state, delete it")
    print("3. Check CloudFormation console for detailed error messages")
