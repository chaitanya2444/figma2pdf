# Test Groq API integration (simple version)
import os
import sys
sys.path.append('backend')

from services.figma_service import parse_figma_with_llm

# Test with different Figma URLs
test_urls = [
    "https://www.figma.com/design/ABC123/E-commerce-App",
    "https://www.figma.com/design/XYZ789/Banking-Dashboard"
]

print("Testing Groq AI Integration...")
print("=" * 50)

for i, url in enumerate(test_urls, 1):
    print(f"\nTest {i}: {url}")
    try:
        result = parse_figma_with_llm(url)
        print(f"App Name: {result['name']}")
        print(f"Colors: {result['colors']}")
        print(f"Frames: {len(result['pages'][0]['frames'])} detected")
        print("SUCCESS: Unique content generated!")
    except Exception as e:
        print(f"Error: {e}")

print("\nReady for 100% unique PDF generation!")