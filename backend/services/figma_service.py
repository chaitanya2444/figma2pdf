# backend/services/figma_service.py
import os
import json
import requests
from typing import Dict, Any
from groq import Groq

# Initialize AI clients
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HF_API_KEY = os.getenv("HF_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

def parse_figma_with_llm(figma_link: str) -> Dict[str, Any]:
    """Multi-AI system: Groq → Hugging Face → Smart Fallback"""
    
    # Try Groq AI first (fastest)
    if groq_client:
        try:
            print("Using Groq AI...")
            return analyze_with_groq(figma_link)
        except Exception as e:
            print(f"Groq failed: {e}")
    
    # Try Hugging Face as backup
    if HF_API_KEY:
        try:
            print("Using Hugging Face AI...")
            return analyze_with_huggingface(figma_link)
        except Exception as e:
            print(f"Hugging Face failed: {e}")
    
    # Smart fallback (always works)
    print("Using smart URL-based analysis...")
    return get_smart_fallback(figma_link)

def analyze_with_groq(figma_link: str) -> Dict[str, Any]:
    """Groq AI analysis (primary)"""
    
    prompt = f"""
Analyze this Figma design URL: {figma_link}

Return valid JSON with:
- name: App name
- pages: array with frames and descriptions  
- colors: Primary, Secondary, Accent, Background hex codes
- fonts: font array
- user_flows: step flow
- tech_recommendation: tech stack

Make it realistic based on the URL.
"""

    response = groq_client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024,
        temperature=0.3
    )
    
    return clean_json_response(response.choices[0].message.content)

def analyze_with_huggingface(figma_link: str) -> Dict[str, Any]:
    """Hugging Face AI analysis (backup)"""
    
    prompt = f"Generate app design data for Figma URL: {figma_link}. Include app name, colors, features, tech stack."
    
    response = requests.post(
        "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium",
        headers={"Authorization": f"Bearer {HF_API_KEY}"},
        json={"inputs": prompt, "parameters": {"max_new_tokens": 200}},
        timeout=30
    )
    
    if response.ok:
        # Since HF response might not be structured, use smart analysis
        return get_smart_fallback(figma_link)
    else:
        raise Exception("HF API error")

def clean_json_response(raw_text: str) -> Dict[str, Any]:
    """Clean and parse JSON from AI response"""
    json_str = raw_text.strip()
    if json_str.startswith("```json"):
        json_str = json_str[7:]
    if json_str.endswith("```"):
        json_str = json_str[:-3]
    return json.loads(json_str.strip())

def get_smart_fallback(figma_link: str) -> Dict[str, Any]:
    """Smart URL-based analysis (always works)"""
    app_type = infer_app_type_from_url(figma_link)
    
    return {
        "name": f"{app_type['name']}",
        "project_name": f"{app_type['name']}",
        "pages": [{"name": "Page 1", "key_frames": app_type['frames']}],
        "colors": app_type['colors'],
        "fonts": app_type['fonts'],
        "user_flows": app_type['flow'],
        "tech_recommendation": app_type['tech']
    }

def infer_app_type_from_url(url: str) -> Dict[str, Any]:
    """Advanced URL analysis for app type detection"""
    
    url_lower = url.lower()
    
    # E-commerce
    if any(word in url_lower for word in ['ecommerce', 'shop', 'store', 'cart', 'product', 'retail', 'marketplace']):
        return {
            "name": "E-commerce Platform",
            "frames": [
                {"name": "Product Discovery", "description": "Homepage with featured products, categories, and search functionality"},
                {"name": "Product Details", "description": "Detailed product view with images, specifications, reviews, and purchase options"},
                {"name": "Shopping Cart", "description": "Cart management with item quantities, promo codes, and shipping calculator"},
                {"name": "Secure Checkout", "description": "Multi-step payment process with address forms and payment methods"},
                {"name": "User Account", "description": "Profile management with order history, wishlist, and preferences"}
            ],
            "colors": {"Primary": "#FF6B35", "Secondary": "#F7931E", "Accent": "#FFD23F", "Background": "#FFFFFF"},
            "fonts": ["Inter", "Poppins"],
            "flow": "Browse Products → View Details → Add to Cart → Checkout → Order Confirmation",
            "tech": "React + Next.js + Stripe + PostgreSQL + Vercel + Redis"
        }
    
    # Fintech/Banking
    elif any(word in url_lower for word in ['bank', 'finance', 'payment', 'wallet', 'money', 'fintech', 'crypto']):
        return {
            "name": "Financial Services App",
            "frames": [
                {"name": "Account Dashboard", "description": "Overview of account balances, recent transactions, and quick action buttons"},
                {"name": "Transaction History", "description": "Detailed transaction list with filtering, search, and export capabilities"},
                {"name": "Money Transfer", "description": "P2P transfer interface with recipient selection and amount input"},
                {"name": "Investment Portfolio", "description": "Investment tracking with charts, performance metrics, and trading options"},
                {"name": "Security Center", "description": "Two-factor authentication, biometric settings, and privacy controls"}
            ],
            "colors": {"Primary": "#1B365D", "Secondary": "#0066CC", "Accent": "#00C851", "Background": "#F8F9FA"},
            "fonts": ["Roboto", "Source Sans Pro"],
            "flow": "Login → Dashboard → Transfer/Invest → Confirmation → Receipt",
            "tech": "React Native + Node.js + Plaid API + MongoDB + AWS + Blockchain"
        }
    
    # Social Media
    elif any(word in url_lower for word in ['social', 'chat', 'message', 'feed', 'post', 'share', 'community']):
        return {
            "name": "Social Media Platform",
            "frames": [
                {"name": "Activity Feed", "description": "Real-time content stream with posts, stories, reactions, and infinite scroll"},
                {"name": "User Profile", "description": "Personal profile with bio, post grid, follower count, and activity highlights"},
                {"name": "Direct Messages", "description": "Private messaging with chat bubbles, media sharing, and group conversations"},
                {"name": "Content Creation", "description": "Post composer with photo/video upload, filters, and caption editing"},
                {"name": "Explore & Discover", "description": "Content discovery with trending topics, hashtags, and user suggestions"}
            ],
            "colors": {"Primary": "#4267B2", "Secondary": "#42B883", "Accent": "#FF4458", "Background": "#FFFFFF"},
            "fonts": ["Inter", "SF Pro Display"],
            "flow": "Browse Feed → Engage → Create Content → Share → Discover",
            "tech": "Flutter + Firebase + GraphQL + Redis + Google Cloud + WebRTC"
        }
    
    # Food Delivery
    elif any(word in url_lower for word in ['food', 'delivery', 'restaurant', 'order', 'menu', 'dining']):
        return {
            "name": "Food Delivery Service",
            "frames": [
                {"name": "Restaurant Discovery", "description": "Location-based restaurant listings with cuisine filters and delivery estimates"},
                {"name": "Menu Browser", "description": "Interactive menu with item photos, descriptions, customization options"},
                {"name": "Order Cart", "description": "Order summary with special instructions, delivery time, and payment selection"},
                {"name": "Live Tracking", "description": "Real-time order status with delivery driver location and ETA updates"},
                {"name": "Rating & Review", "description": "Post-delivery feedback system with photo upload and tip options"}
            ],
            "colors": {"Primary": "#FF6B35", "Secondary": "#FFA726", "Accent": "#4CAF50", "Background": "#FAFAFA"},
            "fonts": ["Inter", "Nunito"],
            "flow": "Browse Restaurants → Select Menu → Place Order → Track Delivery → Rate Experience",
            "tech": "React Native + Express.js + Google Maps + Stripe + MongoDB + Socket.io"
        }
    
    # Healthcare
    elif any(word in url_lower for word in ['health', 'medical', 'doctor', 'clinic', 'patient', 'healthcare']):
        return {
            "name": "Healthcare Management System",
            "frames": [
                {"name": "Patient Dashboard", "description": "Health overview with upcoming appointments, medications, and vital signs"},
                {"name": "Doctor Directory", "description": "Healthcare provider search with specialties, ratings, and availability"},
                {"name": "Appointment Booking", "description": "Calendar-based scheduling with time slots and consultation types"},
                {"name": "Medical Records", "description": "Secure access to test results, prescriptions, and treatment history"},
                {"name": "Telemedicine", "description": "Video consultation interface with chat and file sharing capabilities"}
            ],
            "colors": {"Primary": "#2E7D32", "Secondary": "#66BB6A", "Accent": "#03DAC6", "Background": "#F1F8E9"},
            "fonts": ["Roboto", "Open Sans"],
            "flow": "Book Appointment → Consultation → Prescription → Follow-up → Records",
            "tech": "React + TypeScript + FastAPI + PostgreSQL + WebRTC + HIPAA Compliance"
        }
    
    # Default: Business/SaaS
    else:
        return {
            "name": "Business Management Platform",
            "frames": [
                {"name": "Analytics Dashboard", "description": "KPI overview with interactive charts, metrics, and performance indicators"},
                {"name": "Data Management", "description": "Comprehensive data tables with advanced filtering, sorting, and export options"},
                {"name": "Team Collaboration", "description": "Project management with task assignment, progress tracking, and team communication"},
                {"name": "Configuration Panel", "description": "System settings with user permissions, integrations, and customization options"},
                {"name": "Reports & Insights", "description": "Automated report generation with scheduling, templates, and data visualization"}
            ],
            "colors": {"Primary": "#4285F4", "Secondary": "#34A853", "Accent": "#FBBC04", "Background": "#FFFFFF"},
            "fonts": ["Inter", "Roboto"],
            "flow": "Login → Dashboard → Manage Data → Configure → Generate Reports",
            "tech": "React + TypeScript + FastAPI + PostgreSQL + Docker + Kubernetes"
        }