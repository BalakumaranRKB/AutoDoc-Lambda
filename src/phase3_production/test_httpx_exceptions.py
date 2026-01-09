"""
Test httpx exception structure to ensure retry logic catches them correctly
"""
import httpx


def test_httpx_exceptions():
    """Test what exceptions httpx actually raises."""
    
    print("Testing httpx exception structure...")
    print()
    
    # Test 429 error
    print("1. Testing 429 error structure:")
    try:
        # This will fail with connection error, but shows structure
        client = httpx.Client()
        response = client.get("https://httpstat.us/429")
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        print(f"   Exception type: {type(e).__name__}")
        print(f"   Has response: {hasattr(e, 'response')}")
        print(f"   Status code: {e.response.status_code}")
        print(f"   ✅ Can check status_code")
    except Exception as e:
        print(f"   Other error: {type(e).__name__}")
    
    print()
    print("2. Testing timeout:")
    try:
        client = httpx.Client(timeout=0.001)
        response = client.get("https://httpstat.us/200?sleep=5000")
    except httpx.TimeoutException as e:
        print(f"   Exception type: {type(e).__name__}")
        print(f"   ✅ Timeout detected")
    except Exception as e:
        print(f"   Exception type: {type(e).__name__}")
    
    print()
    print("Done!")


if __name__ == "__main__":
    test_httpx_exceptions()
