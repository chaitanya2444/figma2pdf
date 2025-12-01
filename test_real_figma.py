#!/usr/bin/env python3
"""
Test with a real public Figma URL
"""

import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.figma_service import parse_figma_with_llm

def test_real_figma():
    """Test with a real Figma URL"""
    
    # Use a public Figma community file
    real_figma_url = "https://www.figma.com/file/HhYJ5ucbYWUbkbNJdKckLn/Wireframe-Kit"
    
    print("=== Testing Real Figma URL ===")
    print(f"URL: {real_figma_url}")
    
    try:
        result = parse_figma_with_llm(real_figma_url)
        
        print(f"\nResult:")
        print(f"  Name: {result.get('name')}")
        print(f"  Category: {result.get('category')}")
        print(f"  Description: {result.get('description', 'N/A')[:100]}...")
        print(f"  Features: {len(result.get('key_features', []))} features")
        print(f"  Screens: {len(result.get('pages', [{}])[0].get('key_frames', []))} screens")
        
        # Show first few features
        features = result.get('key_features', [])
        for i, feature in enumerate(features[:3], 1):
            print(f"  Feature {i}: {feature[:60]}...")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_real_figma()
    if success:
        print("\nSUCCESS: Real Figma URL processing working!")
    else:
        print("\nERROR: Issues with real Figma URL processing")
    sys.exit(0 if success else 1)