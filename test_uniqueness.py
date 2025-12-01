#!/usr/bin/env python3
"""
Test uniqueness of AI responses for different URLs
"""

import sys
import os
import json

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.figma_service import parse_figma_with_llm

def test_uniqueness():
    """Test that different URLs generate unique content"""
    
    test_urls = [
        "https://www.figma.com/file/abc123/social-media-app",
        "https://www.figma.com/file/def456/ecommerce-store", 
        "https://www.figma.com/file/ghi789/banking-fintech",
        "https://www.figma.com/file/jkl012/food-delivery",
        "https://www.figma.com/file/mno345/healthcare-app"
    ]
    
    print("=== Testing Uniqueness Across Different URLs ===\n")
    
    results = []
    for i, url in enumerate(test_urls, 1):
        print(f"Test {i}: {url}")
        try:
            result = parse_figma_with_llm(url)
            results.append(result)
            
            print(f"  Name: {result.get('name')}")
            print(f"  Category: {result.get('category')}")
            print(f"  Description: {result.get('description', 'N/A')[:80]}...")
            
            # Show first 3 features
            features = result.get('key_features', [])
            for j, feature in enumerate(features[:3], 1):
                print(f"  Feature {j}: {feature[:60]}...")
            
            print()
            
        except Exception as e:
            print(f"  ERROR: {e}")
            return False
    
    # Check uniqueness
    names = [r.get('name', '') for r in results]
    descriptions = [r.get('description', '') for r in results]
    
    unique_names = len(set(names))
    unique_descriptions = len(set(descriptions))
    
    print(f"Uniqueness Results:")
    print(f"  Unique Names: {unique_names}/{len(results)}")
    print(f"  Unique Descriptions: {unique_descriptions}/{len(results)}")
    
    if unique_names == len(results) and unique_descriptions == len(results):
        print("SUCCESS: All responses are unique!")
        return True
    else:
        print("WARNING: Some responses are duplicated")
        return False

if __name__ == "__main__":
    success = test_uniqueness()
    sys.exit(0 if success else 1)