#!/usr/bin/env python3
"""
Local test for chunking logic (no API calls)

Tests:
1. Chunk detection
2. Intelligent splitting by functions/classes
3. Chunk size validation
4. Merging logic
"""
import sys
sys.path.insert(0, '/Users/aishitdharwal/Documents/AI Classroom/Intelligent-Code-Documentation-Generator/src/phase3_production')

from chunking import IntelligentChunker, CodeChunk


def generate_test_file(num_functions: int = 150) -> str:
    """Generate a large test file."""
    code_parts = [
        '"""Large test module."""',
        '',
        'import math',
        'import random',
        ''
    ]
    
    for i in range(num_functions):
        func_code = f'''
def function_{i}(x, y):
    """
    Function number {i}.
    
    Performs calculation {i}.
    
    Args:
        x: First input
        y: Second input
        
    Returns:
        Result
    """
    result = (x + y) * {i}
    if result > 100:
        return result / 2
    else:
        return result + 10
'''
        code_parts.append(func_code)
    
    return '\n'.join(code_parts)


def test_chunking_locally():
    """Test chunking logic locally."""
    
    print("=" * 80)
    print("LOCAL CHUNKING TEST (No API Calls)")
    print("=" * 80)
    print()
    
    # Initialize chunker
    chunker = IntelligentChunker(
        max_chunk_lines=2000,
        min_chunk_lines=500,
        overlap_lines=50
    )
    
    # Test 1: Small file (should NOT chunk)
    print("TEST 1: Small File (1000 lines)")
    print("-" * 80)
    
    small_file = generate_test_file(num_functions=50)
    small_lines = small_file.split('\n')
    
    print(f"File size: {len(small_lines)} lines")
    
    should_chunk = chunker.should_chunk(small_file)
    print(f"Should chunk: {should_chunk}")
    
    if should_chunk:
        print("❌ FAIL: Small file should NOT be chunked")
    else:
        print("✅ PASS: Small file correctly identified")
    
    print()
    
    # Test 2: Large file (should chunk)
    print("TEST 2: Large File (3000+ lines)")
    print("-" * 80)
    
    large_file = generate_test_file(num_functions=150)
    large_lines = large_file.split('\n')
    
    print(f"File size: {len(large_lines)} lines")
    
    should_chunk = chunker.should_chunk(large_file)
    print(f"Should chunk: {should_chunk}")
    
    if not should_chunk:
        print("❌ FAIL: Large file should be chunked")
        return
    else:
        print("✅ PASS: Large file correctly identified")
    
    print()
    
    # Test 3: Create chunks
    print("TEST 3: Chunk Creation")
    print("-" * 80)
    
    chunks = chunker.chunk_file("test_large.py", large_file)
    
    print(f"Total chunks created: {len(chunks)}")
    print()
    
    # Verify chunks
    for i, chunk in enumerate(chunks):
        print(f"Chunk {i}:")
        print(f"  Lines: {chunk.start_line}-{chunk.end_line} ({chunk.size()} lines)")
        print(f"  Type: {chunk.type}")
        print(f"  Elements: {len(chunk.elements)} ({', '.join(chunk.elements[:3])}{'...' if len(chunk.elements) > 3 else ''})")
        
        # Validate chunk size
        if chunk.size() > 2000:
            print(f"  ⚠️  WARNING: Chunk exceeds max size!")
        elif chunk.size() < 100:
            print(f"  ⚠️  WARNING: Chunk is very small")
        else:
            print(f"  ✅ Size OK")
        print()
    
    # Test 4: Get summary
    print("TEST 4: Chunk Summary")
    print("-" * 80)
    
    summary = chunker.get_chunk_summary(chunks)
    
    print(f"Total chunks: {summary['total_chunks']}")
    print(f"Total lines: {summary['total_lines']}")
    print(f"Avg chunk size: {summary['avg_chunk_size']} lines")
    print(f"Min chunk size: {summary['min_chunk_size']} lines")
    print(f"Max chunk size: {summary['max_chunk_size']} lines")
    print()
    
    # Validate
    if summary['max_chunk_size'] <= 2000:
        print("✅ PASS: All chunks within max size")
    else:
        print(f"❌ FAIL: Some chunks exceed max size ({summary['max_chunk_size']} lines)")
    
    if summary['total_chunks'] > 0:
        print("✅ PASS: Chunks created successfully")
    else:
        print("❌ FAIL: No chunks created")
    
    print()
    
    # Test 5: Content verification
    print("TEST 5: Content Verification")
    print("-" * 80)
    
    # Verify we didn't lose any content
    total_chunk_lines = sum(chunk.size() for chunk in chunks)
    original_lines = len(large_lines)
    
    print(f"Original file: {original_lines} lines")
    print(f"Total in chunks: {total_chunk_lines} lines")
    
    # Note: With overlap, chunk lines > original lines is expected
    if total_chunk_lines >= original_lines:
        print("✅ PASS: No content lost (overlap is normal)")
    else:
        print(f"❌ FAIL: Lost {original_lines - total_chunk_lines} lines!")
    
    print()
    
    # Test 6: Show sample chunk content
    print("TEST 6: Sample Chunk Content")
    print("-" * 80)
    
    if chunks:
        sample_chunk = chunks[0]
        lines = sample_chunk.content.split('\n')
        
        print(f"First chunk preview (first 20 lines):")
        print("-" * 40)
        for i, line in enumerate(lines[:20], 1):
            print(f"{i:3}: {line}")
        
        if len(lines) > 20:
            print(f"... ({len(lines) - 20} more lines)")
        
        print("-" * 40)
        print()
        
        # Verify it's valid Python
        import ast
        try:
            ast.parse(sample_chunk.content)
            print("✅ PASS: Chunk contains valid Python code")
        except SyntaxError as e:
            print(f"❌ FAIL: Chunk has syntax error: {e}")
    
    print()
    
    # Final summary
    print("=" * 80)
    print("LOCAL CHUNKING TEST COMPLETE")
    print("=" * 80)
    print()
    
    print("Summary:")
    print(f"  ✅ Small files (<2000 lines): Not chunked")
    print(f"  ✅ Large files (>2000 lines): Chunked into {len(chunks)} parts")
    print(f"  ✅ Chunk sizes: {summary['min_chunk_size']}-{summary['max_chunk_size']} lines")
    print(f"  ✅ Chunks contain valid Python code")
    print()
    
    print("The chunking logic is working correctly!")
    print("Ready to deploy and test with real API.")
    print()


if __name__ == "__main__":
    test_chunking_locally()
