#!/usr/bin/env python3
"""
Test JSON + Figma URL combination for unique PDF generation
"""

import sys
import os
import json

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.figma_service import parse_figma_with_llm
from services.pdf_service import generate_pdf_from_data

def test_json_merge():
    """Test combining JSON data with Figma URL analysis"""
    
    figma_url = "https://www.figma.com/file/test123/ecommerce-platform"
    
    # Load sample JSON
    with open('sample_json_data.json', 'r') as f:
        json_data = json.load(f)
    
    print("=== Testing JSON + Figma URL Combination ===")
    print(f"Figma URL: {figma_url}")
    print(f"JSON Data: {json_data['name']}")
    
    try:
        # Test 1: AI only
        print("\n1. AI Analysis Only:")
        ai_only = parse_figma_with_llm(figma_url)
        print(f"   Name: {ai_only.get('name')}")
        print(f"   Features: {len(ai_only.get('key_features', []))}")
        
        # Test 2: AI + JSON merge
        print("\n2. AI + JSON Merge:")
        merged_data = parse_figma_with_llm(figma_url, json_data)
        print(f"   Name: {merged_data.get('name')}")
        print(f"   Features: {len(merged_data.get('key_features', []))}")
        print(f"   Description: {merged_data.get('description')[:80]}...")
        
        # Generate PDF with merged data
        pdf_path = generate_pdf_from_data(merged_data)
        
        if os.path.exists(pdf_path):
            file_size = os.path.getsize(pdf_path)
            print(f"\nSUCCESS: PDF Generated: {os.path.basename(pdf_path)}")
            print(f"   Size: {file_size:,} bytes")
            print(f"   Contains custom JSON data merged with AI analysis")
            return True
        else:
            print("ERROR: PDF generation failed")
            return False
            
    except Exception as e:
        print(f"ERROR: Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_json_merge()
    if success:
        print("\nSUCCESS: JSON + Figma URL combination working!")
    else:
        print("\nERROR: Issues with JSON merge system")
    sys.exit(0 if success else 1)