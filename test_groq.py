# Test Groq API integration
import os
import sys
sys.path.append('backend')

# Test the Groq API
from services.figma_service import parse_figma_with_llm

# Test with different Figma URLs
test_urls = [
    "https://www.figma.com/design/ABC123/E-commerce-App",
    "https://www.figma.com/design/XYZ789/Banking-Dashboard", 
    "https://www.figma.com/design/DEF456/Social-Media-App"
]

print("🧪 Testing Groq AI Integration...")
print("=" * 50)

for i, url in enumerate(test_urls, 1):
    print(f"\n📱 Test {i}: {url}")
    try:
        result = parse_figma_with_llm(url)
        print(f"✅ App Name: {result['name']}")
        print(f"🎨 Colors: {result['colors']}")
        print(f"🔧 Tech: {result['tech_recommendation'][:50]}...")
        print(f"📄 Frames: {len(result['pages'][0]['frames'])} detected")
    except Exception as e:
        print(f"❌ Error: {e}")

print("\n🚀 Ready for unique PDF generation!")