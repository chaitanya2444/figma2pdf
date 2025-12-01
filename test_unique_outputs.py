#!/usr/bin/env python3
"""
Test unique outputs for different Figma URLs
"""

import sys
import os
import json

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.figma_service import parse_figma_with_llm

def test_unique_outputs():
    """Test different URLs to ensure unique outputs"""
    
    test_urls = [
        "https://www.figma.com/file/abc123/ecommerce-shopping-app",
        "https://www.figma.com/design/xyz789/social-media-platform", 
        "https://www.figma.com/file/def456/banking-fintech-app",
        "https://www.figma.com/proto/ghi789/food-delivery-service",
        "https://www.figma.com/file/jkl012/healthcare-medical-app"
    ]
    
    print("=== Testing Unique Outputs for Different URLs ===\n")
    
    results = []
    for i, url in enumerate(test_urls, 1):
        print(f"Test {i}: {url}")
        try:
            result = parse_figma_with_llm(url)
            results.append(result)
            
            print(f"  App Name: {result.get('name')}")
            print(f"  Frames: {[f['name'] for f in result.get('pages', [{}])[0].get('key_frames', [])]}")
            print(f"  Colors: {result.get('colors', {}).get('Primary')} (Primary)")
            print(f"  Tech: {result.get('tech_recommendation', 'N/A')[:50]}...")
            flow_text = result.get('user_flows', 'N/A')[:50].replace('→', '->')
            print(f"  Flow: {flow_text}...")
            print()
            
        except Exception as e:
            print(f"  ERROR: {e}")
            return False
    
    # Check for uniqueness
    names = [r.get('name') for r in results]
    if len(set(names)) == len(names):
        print("SUCCESS: All app names are unique!")
    else:
        print("WARNING: Some app names are duplicated")
    
    return True

if __name__ == "__main__":
    test_unique_outputs()