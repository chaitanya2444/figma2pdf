# Quick test to verify diagram generation works
from backend.services.ai_diagram_generator import generate_ai_architecture_diagram

# Mock figma_data from your PDF output
figma_data = {
    'pages': [
        {'key_frames': [
            {'name': 'Product detail page (FRAME)'},
            {'name': 'About (FRAME)'},
            {'name': 'Article (FRAME)'},
            {'name': 'Shop (FRAME)'},
            {'name': 'Landing page (FRAME)'}
        ]}
    ],
    'project_name': 'Untitled'
}

# Generate & print preview
diagram_base64 = generate_ai_architecture_diagram(figma_data)
print("Success? Starts with data:image:", diagram_base64[:50] + "...")

if diagram_base64.startswith("data:image/png;base64,"):
    print("SUCCESS: Diagram generation working perfectly!")
    print("SUCCESS: Ready to embed in PDF!")
else:
    print("ERROR: Issue with diagram generation")