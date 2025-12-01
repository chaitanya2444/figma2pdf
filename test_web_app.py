#!/usr/bin/env python3
"""
End-to-end web application test
"""

import requests
import json
import time
import sys
import os

def test_web_endpoints():
    """Test actual web endpoints"""
    base_url = "http://localhost:8002"
    
    print("=== Testing Web Application Endpoints ===")
    
    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            print("SUCCESS: Health check passed")
        else:
            print(f"ERROR: Health check failed - {response.status_code}")
            return False
    except Exception as e:
        print(f"ERROR: Cannot connect to server - {e}")
        print("Make sure backend is running on port 8002")
        return False
    
    # Test 2: Generate PDF endpoint
    test_data = {
        "figma_url": "https://www.figma.com/file/test123/ecommerce-app"
    }
    
    try:
        response = requests.post(f"{base_url}/generate", json=test_data, timeout=30)
        if response.status_code == 200:
            print("SUCCESS: PDF generation endpoint working")
            # Check if response is PDF
            if response.headers.get('content-type') == 'application/pdf':
                print(f"SUCCESS: PDF generated ({len(response.content)} bytes)")
            else:
                print("ERROR: Response is not PDF")
                return False
        else:
            print(f"ERROR: PDF generation failed - {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"ERROR: PDF generation request failed - {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_web_endpoints()
    if success:
        print("\nSUCCESS: All web application tests passed!")
    else:
        print("\nERROR: Web application tests failed!")
    sys.exit(0 if success else 1)