#!/usr/bin/env python3
"""Test script to verify AI diagram generation and PDF embedding"""

import sys
import os
sys.path.append('backend')

from services.ai_diagram_generator import generate_ai_architecture_diagram
from services.pdf_service import generate_pdf_from_data

# Test data
test_data = {
    "project_name": "E-commerce App",
    "overview": "Modern e-commerce application with microservices architecture",
    "pages": [
        {
            "name": "Home Page",
            "key_frames": [
                {"name": "Product Grid", "type": "FRAME"},
                {"name": "Navigation", "type": "COMPONENT"},
                {"name": "Cart Button", "type": "BUTTON"}
            ]
        }
    ],
    "ui_elements": [],
    "design_system": {"colors": {"primary": "#0066FF"}, "typography": []},
    "main_user_flows": ["User browses products -> adds to cart -> checkout"],
    "tech_recommendations": "React, Node.js, PostgreSQL"
}

print("Testing AI diagram generation...")
diagram_b64 = generate_ai_architecture_diagram(test_data)

if diagram_b64:
    print(f"✅ Diagram generated successfully! Length: {len(diagram_b64)} chars")
    
    print("Testing PDF generation with embedded diagram...")
    pdf_path = generate_pdf_from_data(test_data, ".")
    
    if os.path.exists(pdf_path):
        print(f"✅ PDF generated successfully: {pdf_path}")
        print(f"📄 File size: {os.path.getsize(pdf_path)} bytes")
        print("\n🎉 IT WORKED! Open the PDF to see your beautiful AI diagram!")
    else:
        print("❌ PDF generation failed")
else:
    print("❌ Diagram generation failed")