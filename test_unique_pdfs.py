#!/usr/bin/env python3
"""
Test that different URLs generate unique comprehensive PDFs
"""

import sys
import os
import json

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.figma_service import parse_figma_with_llm
from services.pdf_service import generate_pdf_from_data

def test_unique_pdfs():
    """Test that different URLs generate unique comprehensive PDFs"""
    
    test_urls = [
        "https://www.figma.com/file/test1/social-networking-platform",
        "https://www.figma.com/file/test2/ecommerce-marketplace-store", 
        "https://www.figma.com/file/test3/fintech-banking-application"
    ]
    
    print("=== Testing Unique PDF Generation ===\n")
    
    pdf_files = []
    for i, url in enumerate(test_urls, 1):
        print(f"Test {i}: {url}")
        try:
            # Get AI analysis
            ai_data = parse_figma_with_llm(url)
            print(f"  App: {ai_data.get('name')}")
            print(f"  Category: {ai_data.get('category')}")
            
            # Generate PDF
            pdf_path = generate_pdf_from_data(ai_data)
            
            if os.path.exists(pdf_path):
                file_size = os.path.getsize(pdf_path)
                pdf_files.append((pdf_path, file_size, ai_data.get('name')))
                print(f"  PDF: {os.path.basename(pdf_path)} ({file_size:,} bytes)")
            else:
                print(f"  ERROR: PDF not generated")
                return False
                
        except Exception as e:
            print(f"  ERROR: {e}")
            return False
        
        print()
    
    # Verify all PDFs are different sizes (indicating unique content)
    sizes = [size for _, size, _ in pdf_files]
    names = [name for _, _, name in pdf_files]
    
    print("Summary:")
    for pdf_path, size, name in pdf_files:
        print(f"  {name}: {size:,} bytes")
    
    unique_sizes = len(set(sizes))
    unique_names = len(set(names))
    
    if unique_sizes == len(pdf_files) and unique_names == len(pdf_files):
        print(f"\nSUCCESS: All {len(pdf_files)} PDFs are unique!")
        return True
    else:
        print(f"\nWARNING: Some PDFs may be similar")
        return False

if __name__ == "__main__":
    success = test_unique_pdfs()
    sys.exit(0 if success else 1)