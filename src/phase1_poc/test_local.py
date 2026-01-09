"""
Local testing script for Phase 1 POC.

Run this to test documentation generation locally without deploying to AWS.
"""
import sys
import os
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.phase1_poc.lambda_function import lambda_handler
from src.shared.utils import setup_logging


def test_with_file(file_path: str):
    """Test documentation generation with a file."""
    setup_logging("INFO")
    
    print(f"\n{'=' * 80}")
    print(f"Testing with file: {file_path}")
    print('=' * 80)
    
    # Read file content
    try:
        with open(file_path, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        return
    
    # Create event
    event = {
        'body': json.dumps({
            'file_path': file_path,
            'file_content': content
        })
    }
    
    # Call lambda handler
    response = lambda_handler(event, None)
    
    # Print response
    print(f"\nStatus Code: {response['statusCode']}")
    
    body = json.loads(response['body'])
    
    if body['success']:
        result = body['data']
        
        print(f"\n{'-' * 80}")
        print("RESULT SUMMARY")
        print('-' * 80)
        print(f"Request ID: {result['request_id']}")
        print(f"Status: {result['status']}")
        print(f"File: {result['file_path']}")
        print(f"Total Tokens: {result['total_tokens']:,}")
        print(f"Total Cost (USD): ${result['total_cost']:.4f}")
        print(f"Total Cost (INR): ₹{result['total_cost'] * 83:.2f}")
        print(f"Processing Time: {result['processing_time_seconds']:.2f}s")
        
        if result.get('analysis'):
            analysis = result['analysis']
            print(f"\n{'-' * 80}")
            print("CODE ANALYSIS")
            print('-' * 80)
            print(f"Total Lines: {analysis['total_lines']}")
            print(f"Code Lines: {analysis['code_lines']}")
            print(f"Comment Lines: {analysis['comment_lines']}")
            print(f"Blank Lines: {analysis['blank_lines']}")
            print(f"Elements Found: {len(analysis['elements'])}")
            
            if analysis['elements']:
                print(f"\nCode Elements:")
                for elem in analysis['elements']:
                    print(f"  - {elem['type']}: {elem['name']} (lines {elem['line_start']}-{elem['line_end']})")
        
        print(f"\n{'-' * 80}")
        print("GENERATED DOCUMENTATION")
        print('-' * 80)
        print(result['documentation'])
        print('=' * 80 + '\n')
        
        # Save documentation to file
        output_file = file_path.replace('.py', '_DOCUMENTATION.md')
        with open(output_file, 'w') as f:
            f.write(result['documentation'])
        print(f"Documentation saved to: {output_file}\n")
        
    else:
        print(f"\nError: {body['error']}")
        print('=' * 80 + '\n')


def main():
    """Main function for local testing."""
    # Test files
    test_files = [
        'tests/test_data/small_repo/calculator.py',
    ]
    
    for file_path in test_files:
        if os.path.exists(file_path):
            test_with_file(file_path)
        else:
            print(f"Skipping {file_path} (not found)")
    
    print("\n" + "=" * 80)
    print("LOCAL TESTING COMPLETE")
    print("=" * 80)
    print("\nTo test with your own file:")
    print("  python src/phase1_poc/test_local.py --file /path/to/your/file.py")
    print("\nOr run the lambda function directly:")
    print("  python src/phase1_poc/lambda_function.py --file /path/to/your/file.py")
    print()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test documentation generation locally')
    parser.add_argument('--file', type=str, help='Path to Python file to test')
    args = parser.parse_args()
    
    if args.file:
        test_with_file(args.file)
    else:
        main()
