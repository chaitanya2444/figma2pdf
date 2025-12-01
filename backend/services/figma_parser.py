# figma_parser.py - Dynamic Figma JSON Parser
import os
import requests
import json
from typing import Dict, Any, List
import hashlib

FIGMA_API_URL = "https://api.figma.com/v1"
FIGMA_TOKEN = os.getenv("FIGMA_TOKEN")

def fetch_figma_data(figma_url: str) -> Dict[str, Any]:
    """
    ✅ 1. FETCH FIGMA FILE DATA EVERY TIME - NO CACHING
    """
    # Extract file key from URL
    import re
    match = re.search(r'/file/([a-zA-Z0-9]+)', figma_url)
    if not match:
        raise ValueError("Invalid Figma URL")
    
    file_key = match.group(1)
    
    # Make API call with token
    headers = {"Authorization": f"Bearer {FIGMA_TOKEN}"} if FIGMA_TOKEN else {}
    
    print(f"FETCHING FIGMA DATA: {file_key}")
    response = requests.get(f"{FIGMA_API_URL}/files/{file_key}", headers=headers, timeout=30)
    
    if response.status_code != 200:
        print(f"ERROR: Figma API Error: {response.status_code}")
        raise Exception(f"Figma API failed: {response.status_code}")
    
    figma_data = response.json()
    print(f"SUCCESS: FIGMA DATA FETCHED: {figma_data.get('name', 'Unknown')}")
    
    return figma_data

def parse_figma_structure(figma_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    ✅ 2. PARSE FIGMA JSON DYNAMICALLY - NO FIXED TEXT
    """
    
    # Extract basic info
    file_name = figma_data.get("name", "Untitled")
    last_modified = figma_data.get("lastModified", "")
    
    # Parse document structure
    document = figma_data.get("document", {})
    
    # Extract pages
    pages = []
    frames = []
    components = []
    text_nodes = []
    colors = set()
    
    print(f"PARSING STRUCTURE FOR: {file_name}")
    
    # Walk through all pages
    for page in document.get("children", []):
        if page.get("type") == "CANVAS":
            page_name = page.get("name", "Page")
            pages.append(page_name)
            print(f"  Page: {page_name}")
            
            # Walk through frames in this page
            page_frames = extract_frames_from_page(page, page_name)
            frames.extend(page_frames)
            
            # Extract components and text
            page_components, page_text = extract_content_from_page(page, page_name)
            components.extend(page_components)
            text_nodes.extend(page_text)
    
    # Extract colors from styles
    styles = figma_data.get("styles", {})
    for style_id, style_data in styles.items():
        if style_data.get("styleType") == "FILL":
            colors.add(style_id)
    
    # Generate unique hash for this specific file state
    content_hash = hashlib.md5(f"{file_name}{last_modified}{len(frames)}{len(components)}".encode()).hexdigest()[:8]
    
    parsed_structure = {
        "file_name": file_name,
        "last_modified": last_modified,
        "content_hash": content_hash,
        "pages": pages,
        "frames": frames,
        "components": components,
        "text_nodes": text_nodes,
        "colors": list(colors),
        "total_pages": len(pages),
        "total_frames": len(frames),
        "total_components": len(components),
        "total_text_nodes": len(text_nodes)
    }
    
    print(f"PARSED RESULTS:")
    print(f"  Pages: {len(pages)}")
    print(f"  Frames: {len(frames)}")
    print(f"  Components: {len(components)}")
    print(f"  Text Nodes: {len(text_nodes)}")
    
    return parsed_structure

def extract_frames_from_page(page: Dict[str, Any], page_name: str) -> List[Dict[str, Any]]:
    """Extract all frames from a page"""
    frames = []
    
    def walk_node(node, depth=0):
        node_type = node.get("type", "")
        node_name = node.get("name", "")
        
        if node_type == "FRAME":
            bounds = node.get("absoluteBoundingBox", {})
            frame_data = {
                "name": node_name,
                "page": page_name,
                "type": node_type,
                "width": bounds.get("width", 0),
                "height": bounds.get("height", 0),
                "x": bounds.get("x", 0),
                "y": bounds.get("y", 0),
                "children_count": len(node.get("children", [])),
                "visible": node.get("visible", True)
            }
            frames.append(frame_data)
            print(f"    Frame: {node_name} ({frame_data['width']}x{frame_data['height']})")
        
        # Recurse through children
        for child in node.get("children", []):
            walk_node(child, depth + 1)
    
    walk_node(page)
    return frames

def extract_content_from_page(page: Dict[str, Any], page_name: str) -> tuple:
    """Extract components and text from a page"""
    components = []
    text_nodes = []
    
    def walk_content(node):
        node_type = node.get("type", "")
        node_name = node.get("name", "")
        
        # Extract components
        if node_type in ["COMPONENT", "INSTANCE"]:
            component_data = {
                "name": node_name,
                "type": node_type,
                "page": page_name,
                "id": node.get("id", ""),
                "description": node.get("description", "")
            }
            components.append(component_data)
            print(f"    Component: {node_name} ({node_type})")
        
        # Extract text content
        if node_type == "TEXT":
            text_content = node.get("characters", "")
            if text_content.strip():
                text_data = {
                    "content": text_content,
                    "name": node_name,
                    "page": page_name,
                    "style": node.get("style", {})
                }
                text_nodes.append(text_data)
                print(f"    Text: {text_content[:50]}...")
        
        # Recurse through children
        for child in node.get("children", []):
            walk_content(child)
    
    walk_content(page)
    return components, text_nodes

def generate_dynamic_content(parsed_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    ✅ Generate dynamic content from parsed Figma data - NO TEMPLATES
    """
    
    # Dynamic screen analysis
    screen_analysis = f"Screen Count: {parsed_data['total_frames']}\n"
    screen_analysis += "Screens:\n"
    for frame in parsed_data['frames']:
        screen_analysis += f"- {frame['name']} ({frame['width']}x{frame['height']})\n"
    
    # Dynamic component analysis
    component_analysis = f"Components Detected: {parsed_data['total_components']}\n"
    if parsed_data['components']:
        for comp in parsed_data['components']:
            component_analysis += f"- {comp['name']} / {comp['type']}\n"
    else:
        component_analysis += "- No reusable components found\n"
    
    # Dynamic text content analysis
    text_analysis = f"Text Content: {parsed_data['total_text_nodes']} text elements\n"
    unique_texts = set()
    for text in parsed_data['text_nodes']:
        if len(text['content']) > 5:  # Skip very short text
            unique_texts.add(text['content'][:30])
    
    for text in list(unique_texts)[:10]:  # Show first 10 unique texts
        text_analysis += f"- \"{text}...\"\n"
    
    # Dynamic page structure
    page_structure = f"Page Structure: {parsed_data['total_pages']} pages\n"
    for page in parsed_data['pages']:
        page_frames = [f for f in parsed_data['frames'] if f['page'] == page]
        page_structure += f"- {page}: {len(page_frames)} frames\n"
    
    return {
        "file_name": parsed_data['file_name'],
        "content_hash": parsed_data['content_hash'],
        "screen_analysis": screen_analysis,
        "component_analysis": component_analysis,
        "text_analysis": text_analysis,
        "page_structure": page_structure,
        "frames": parsed_data['frames'],
        "components": parsed_data['components'],
        "raw_data": parsed_data
    }

def parse_figma_url(figma_url: str) -> Dict[str, Any]:
    """
    Main entry point - fetches and parses Figma data dynamically
    """
    try:
        # ✅ 1. Fetch fresh data every time
        figma_data = fetch_figma_data(figma_url)
        
        # ✅ 2. Parse structure dynamically
        parsed_structure = parse_figma_structure(figma_data)
        
        # ✅ 3. Generate dynamic content
        dynamic_content = generate_dynamic_content(parsed_structure)
        
        return dynamic_content
        
    except Exception as e:
        print(f"ERROR: FIGMA PARSING FAILED: {e}")
        # Return error info instead of generic fallback
        return {
            "file_name": "Figma API Error",
            "content_hash": "error",
            "screen_analysis": f"Error: {str(e)}",
            "component_analysis": "Could not fetch Figma data",
            "text_analysis": "API call failed",
            "page_structure": "No data available",
            "frames": [],
            "components": [],
            "raw_data": {}
        }