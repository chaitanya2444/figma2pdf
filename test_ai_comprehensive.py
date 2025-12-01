#!/usr/bin/env python3
"""
Test comprehensive AI-generated documentation
"""

import sys
import os
import json

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.figma_service import parse_figma_with_llm
from services.pdf_service import generate_pdf_from_data

def test_comprehensive_ai():
    """Test full AI-driven comprehensive analysis"""
    
    test_url = "https://www.figma.com/file/test123/ecommerce-marketplace-app"
    
    print("=== Testing Comprehensive AI Analysis ===")
    print(f"URL: {test_url}")
    
    # Get AI analysis
    try:
        ai_data = parse_figma_with_llm(test_url)
        
        print(f"\nSUCCESS: AI Analysis Generated:")
        print(f"   App Name: {ai_data.get('name')}")
        print(f"   Category: {ai_data.get('category', 'N/A')}")
        print(f"   Description: {ai_data.get('description', 'N/A')[:100]}...")
        print(f"   Features: {len(ai_data.get('key_features', []))} features")
        print(f"   Screens: {len(ai_data.get('pages', [{}])[0].get('key_frames', []))} screens")
        print(f"   Colors: {len(ai_data.get('colors', {}))} color definitions")
        
        # Generate comprehensive PDF
        pdf_path = generate_pdf_from_data(ai_data)
        
        if os.path.exists(pdf_path):
            file_size = os.path.getsize(pdf_path)
            print(f"\nSUCCESS: Comprehensive PDF Generated:")
            print(f"   File: {os.path.basename(pdf_path)}")
            print(f"   Size: {file_size:,} bytes")
            print(f"   Path: {pdf_path}")
            
            # Verify it contains comprehensive content
            if file_size > 5000:  # 5KB+ indicates content
                print("SUCCESS: PDF contains rich, comprehensive content!")
                return True
            else:
                print("WARNING: PDF seems small - may lack comprehensive content")
                return False
        else:
            print("ERROR: PDF generation failed")
            return False
            
    except Exception as e:
        print(f"ERROR: Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_comprehensive_ai()
    if success:
        print("\nSUCCESS: Comprehensive AI documentation system working!")
    else:
        print("\nERROR: Issues with comprehensive AI system")
    sys.exit(0 if success else 1)