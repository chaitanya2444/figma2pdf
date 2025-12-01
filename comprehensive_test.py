#!/usr/bin/env python3
"""
Comprehensive test suite for Figma2PDF system
Tests all components multiple times to catch intermittent errors
"""

import sys
import os
import traceback
import json
from pathlib import Path

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_ai_diagram_generator():
    """Test AI diagram generation with various data structures"""
    print("=== Testing AI Diagram Generator ===")
    
    from services.ai_diagram_generator import generate_ai_architecture_diagram
    
    test_cases = [
        # Case 1: Full structure with project_name
        {
            'pages': [{'key_frames': [{'name': 'Home'}, {'name': 'Shop'}, {'name': 'Cart'}]}],
            'project_name': 'E-commerce App'
        },
        # Case 2: Structure with name only
        {
            'pages': [{'key_frames': [{'name': 'Dashboard'}, {'name': 'Profile'}]}],
            'name': 'Business App'
        },
        # Case 3: Minimal structure
        {
            'pages': [{'key_frames': [{'name': 'Page1'}]}]
        },
        # Case 4: Empty structure
        {
            'pages': []
        },
        # Case 5: Missing pages
        {}
    ]
    
    for i, test_data in enumerate(test_cases, 1):
        try:
            print(f"  Test {i}: {test_data}")
            result = generate_ai_architecture_diagram(test_data)
            if result and result.startswith("data:image/png;base64,"):
                print(f"  SUCCESS: Test {i} PASSED")
            else:
                print(f"  ERROR: Test {i} FAILED - Invalid result")
                return False
        except Exception as e:
            print(f"  ERROR: Test {i} FAILED - {e}")
            traceback.print_exc()
            return False
    
    return True

def test_figma_service():
    """Test Figma service parsing"""
    print("\n=== Testing Figma Service ===")
    
    from services.figma_service import parse_figma_with_llm
    
    test_urls = [
        "https://www.figma.com/file/abc123/ecommerce-design",
        "https://www.figma.com/design/xyz789/social-app",
        "https://www.figma.com/file/def456/banking-app",
        "https://www.figma.com/proto/ghi789/food-delivery"
    ]
    
    for i, url in enumerate(test_urls, 1):
        try:
            print(f"  Test {i}: {url}")
            result = parse_figma_with_llm(url)
            
            # Check required fields
            required_fields = ['name', 'project_name', 'pages']
            for field in required_fields:
                if field not in result:
                    print(f"  ERROR: Test {i} FAILED - Missing {field}")
                    return False
            
            # Check pages structure
            if not isinstance(result['pages'], list):
                print(f"  ERROR: Test {i} FAILED - Pages not a list")
                return False
                
            print(f"  SUCCESS: Test {i} PASSED")
        except Exception as e:
            print(f"  ERROR: Test {i} FAILED - {e}")
            traceback.print_exc()
            return False
    
    return True

def test_pdf_service():
    """Test PDF generation"""
    print("\n=== Testing PDF Service ===")
    
    from services.pdf_service import generate_pdf_from_data
    
    test_data = {
        'name': 'Test App',
        'project_name': 'Test App',
        'pages': [
            {'key_frames': [
                {'name': 'Home Page'},
                {'name': 'Product List'},
                {'name': 'Shopping Cart'},
                {'name': 'Checkout'}
            ]}
        ]
    }
    
    for i in range(3):
        try:
            print(f"  Test {i+1}: Generating PDF")
            pdf_path = generate_pdf_from_data(test_data)
            
            if os.path.exists(pdf_path):
                file_size = os.path.getsize(pdf_path)
                print(f"  SUCCESS: Test {i+1} PASSED - PDF created ({file_size} bytes)")
                # Clean up
                os.remove(pdf_path)
            else:
                print(f"  ERROR: Test {i+1} FAILED - PDF not created")
                return False
        except Exception as e:
            print(f"  ERROR: Test {i+1} FAILED - {e}")
            traceback.print_exc()
            return False
    
    return True

def test_main_endpoints():
    """Test main.py endpoints logic"""
    print("\n=== Testing Main Endpoints Logic ===")
    
    # Import main functions
    sys.path.append('backend')
    from main import extract_figma_key
    
    test_urls = [
        "https://www.figma.com/file/abc123def456/my-design",
        "https://www.figma.com/design/xyz789/another-design",
        "https://www.figma.com/proto/ghi123/prototype-design",
        "https://www.figma.com/community/file/123456789/community-design"
    ]
    
    expected_keys = ["abc123def456", "xyz789", "ghi123", "123456789"]
    
    for i, (url, expected) in enumerate(zip(test_urls, expected_keys), 1):
        try:
            print(f"  Test {i}: {url}")
            key = extract_figma_key(url)
            if key == expected:
                print(f"  SUCCESS: Test {i} PASSED - Key: {key}")
            else:
                print(f"  ERROR: Test {i} FAILED - Expected {expected}, got {key}")
                return False
        except Exception as e:
            print(f"  ERROR: Test {i} FAILED - {e}")
            return False
    
    return True

def run_stress_test():
    """Run all tests multiple times to catch intermittent issues"""
    print("\n" + "="*50)
    print("RUNNING COMPREHENSIVE STRESS TEST")
    print("="*50)
    
    test_functions = [
        test_ai_diagram_generator,
        test_figma_service,
        test_pdf_service,
        test_main_endpoints
    ]
    
    for round_num in range(1, 6):  # Run 5 rounds
        print(f"\nROUND {round_num}/5")
        print("-" * 30)
        
        all_passed = True
        for test_func in test_functions:
            if not test_func():
                all_passed = False
                break
        
        if all_passed:
            print(f"SUCCESS: ROUND {round_num} - ALL TESTS PASSED")
        else:
            print(f"ERROR: ROUND {round_num} - TESTS FAILED")
            return False
    
    print("\n" + "="*50)
    print("SUCCESS: ALL 5 ROUNDS COMPLETED SUCCESSFULLY!")
    print("SUCCESS: System is stable and ready for production")
    print("="*50)
    return True

if __name__ == "__main__":
    success = run_stress_test()
    sys.exit(0 if success else 1)