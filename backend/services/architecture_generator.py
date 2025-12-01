# architecture_generator.py - Dynamic Architecture Diagram Generator
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np
from io import BytesIO
import base64
from typing import Dict, Any, List
import hashlib

def generate_architecture_from_figma(figma_data: Dict[str, Any]) -> str:
    """
    ✅ 3. GENERATE UNIQUE ARCHITECTURE DIAGRAM FROM FIGMA DATA
    """
    
    print(f"GENERATING ARCHITECTURE FOR: {figma_data.get('file_name', 'Unknown')}")
    
    # Extract unique elements from Figma data
    frames = figma_data.get('frames', [])
    components = figma_data.get('components', [])
    pages = figma_data.get('raw_data', {}).get('pages', [])
    
    # Create unique layout based on actual Figma structure
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Generate unique colors based on content hash
    content_hash = figma_data.get('content_hash', 'default')
    try:
        color_seed = int(content_hash[:6], 16) if content_hash != 'default' else 123456
    except ValueError:
        # If hash contains non-hex characters, use hash of the string
        color_seed = hash(content_hash) % 1000000
    np.random.seed(color_seed)
    
    # Dynamic color scheme based on Figma content
    def safe_hex_color(hash_str, start, default):
        try:
            if len(hash_str) >= start + 6:
                hex_part = hash_str[start:start+6]
                # Ensure it's valid hex
                int(hex_part, 16)
                return f"#{hex_part}"
        except (ValueError, IndexError):
            pass
        return default
    
    base_colors = {
        'page': safe_hex_color(content_hash, 0, "#E3F2FD"),
        'frame': safe_hex_color(content_hash, 2, "#FFF3E0"), 
        'component': safe_hex_color(content_hash, 4, "#E8F5E8"),
        'api': "#FCE4EC",
        'db': "#F3E5F5"
    }
    
    # Title with actual file name
    file_name = figma_data.get('file_name', 'Figma Design')
    ax.text(7, 9.5, f'{file_name} - System Architecture', 
            ha='center', va='center', fontsize=16, fontweight='bold')
    
    # ✅ DYNAMIC LAYOUT BASED ON ACTUAL FIGMA STRUCTURE
    
    # 1. Pages as top-level containers
    page_y = 8.5
    page_width = 12 / max(len(pages), 1)
    
    for i, page in enumerate(pages):
        x_pos = 1 + i * page_width
        page_box = FancyBboxPatch((x_pos, page_y), page_width - 0.2, 0.8,
                                 boxstyle="round,pad=0.05",
                                 facecolor=base_colors['page'],
                                 edgecolor='#2d3748', linewidth=2)
        ax.add_patch(page_box)
        ax.text(x_pos + page_width/2 - 0.1, page_y + 0.4, f'Page: {page}',
                ha='center', va='center', fontsize=9, fontweight='bold')
    
    # 2. Frames as UI components
    if frames:
        frame_y = 7
        frames_per_row = min(len(frames), 6)
        frame_width = 12 / frames_per_row
        
        for i, frame in enumerate(frames[:6]):  # Show first 6 frames
            x_pos = 1 + (i % frames_per_row) * frame_width
            y_pos = frame_y - (i // frames_per_row) * 0.6
            
            frame_box = FancyBboxPatch((x_pos, y_pos), frame_width - 0.1, 0.5,
                                      boxstyle="round,pad=0.03",
                                      facecolor=base_colors['frame'],
                                      edgecolor='#2d3748', linewidth=1)
            ax.add_patch(frame_box)
            
            # Truncate long frame names
            frame_name = frame['name'][:15] + "..." if len(frame['name']) > 15 else frame['name']
            ax.text(x_pos + frame_width/2 - 0.05, y_pos + 0.25, frame_name,
                   ha='center', va='center', fontsize=8, fontweight='bold')
    
    # 3. Components as reusable elements
    if components:
        comp_y = 5.5
        comps_per_row = min(len(components), 5)
        comp_width = 12 / comps_per_row
        
        for i, comp in enumerate(components[:5]):  # Show first 5 components
            x_pos = 1 + i * comp_width
            
            comp_box = FancyBboxPatch((x_pos, comp_y), comp_width - 0.1, 0.4,
                                     boxstyle="round,pad=0.02",
                                     facecolor=base_colors['component'],
                                     edgecolor='#2d3748', linewidth=1)
            ax.add_patch(comp_box)
            
            comp_name = comp['name'][:12] + "..." if len(comp['name']) > 12 else comp['name']
            ax.text(x_pos + comp_width/2 - 0.05, comp_y + 0.2, comp_name,
                   ha='center', va='center', fontsize=7, fontweight='bold')
    
    # 4. API Layer (dynamic based on complexity)
    api_complexity = len(frames) + len(components)
    if api_complexity > 10:
        api_label = "Microservices API"
        api_desc = f"{api_complexity} endpoints"
    elif api_complexity > 5:
        api_label = "REST API Gateway"
        api_desc = f"{api_complexity} services"
    else:
        api_label = "Simple API"
        api_desc = f"{api_complexity} routes"
    
    api_box = FancyBboxPatch((4, 4), 6, 0.6,
                            boxstyle="round,pad=0.05",
                            facecolor=base_colors['api'],
                            edgecolor='#2d3748', linewidth=2)
    ax.add_patch(api_box)
    ax.text(7, 4.3, f'{api_label}\n{api_desc}',
            ha='center', va='center', fontsize=10, fontweight='bold')
    
    # 5. Database layer (dynamic based on data complexity)
    text_nodes_count = figma_data.get('raw_data', {}).get('total_text_nodes', 0)
    if text_nodes_count > 20:
        db_type = "PostgreSQL + Redis\nHigh Data Volume"
    elif text_nodes_count > 10:
        db_type = "PostgreSQL\nModerate Data"
    else:
        db_type = "SQLite\nSimple Data"
    
    db_box = FancyBboxPatch((4, 2.5), 6, 0.8,
                           boxstyle="round,pad=0.05",
                           facecolor=base_colors['db'],
                           edgecolor='#2d3748', linewidth=2)
    ax.add_patch(db_box)
    ax.text(7, 2.9, db_type,
            ha='center', va='center', fontsize=10, fontweight='bold')
    
    # 6. Dynamic connections based on structure
    # Connect pages to frames
    if pages and frames:
        for i in range(min(len(pages), 3)):
            start_x = 1 + i * (12 / len(pages)) + (12 / len(pages))/2
            ax.annotate('', xy=(start_x, 7.5), xytext=(start_x, 8.5),
                       arrowprops=dict(arrowstyle='->', color='#666', lw=1.5))
    
    # Connect frames to API
    if frames:
        for i in range(min(len(frames), 4)):
            start_x = 1 + i * (12 / min(len(frames), 6)) + (12 / min(len(frames), 6))/2
            ax.annotate('', xy=(7, 4.6), xytext=(start_x, 6.5),
                       arrowprops=dict(arrowstyle='->', color='#666', lw=1))
    
    # Connect API to Database
    ax.annotate('', xy=(7, 3.3), xytext=(7, 4),
               arrowprops=dict(arrowstyle='->', color='#666', lw=2))
    
    # Add metadata footer
    metadata = f"Generated from: {len(pages)} pages, {len(frames)} frames, {len(components)} components"
    ax.text(7, 0.5, metadata, ha='center', va='center', fontsize=8, style='italic')
    
    # Save to base64
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight',
               facecolor='white', edgecolor='none', pad_inches=0.2)
    plt.close()
    
    buffer.seek(0)
    img_data = buffer.read()
    buffer.close()
    
    print(f"SUCCESS: UNIQUE ARCHITECTURE GENERATED: {len(pages)}p/{len(frames)}f/{len(components)}c")
    
    return base64.b64encode(img_data).decode()

def create_flow_diagram(frames: List[Dict[str, Any]]) -> str:
    """Create user flow diagram from actual frames"""
    
    if not frames:
        return ""
    
    fig, ax = plt.subplots(1, 1, figsize=(12, 6))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6)
    ax.axis('off')
    
    # Arrange frames in flow
    frames_to_show = frames[:8]  # Show up to 8 frames
    frame_width = 10 / len(frames_to_show)
    
    for i, frame in enumerate(frames_to_show):
        x_pos = 1 + i * frame_width
        
        # Frame box
        frame_box = FancyBboxPatch((x_pos, 2.5), frame_width - 0.2, 1,
                                  boxstyle="round,pad=0.05",
                                  facecolor='#E3F2FD',
                                  edgecolor='#1976D2', linewidth=1)
        ax.add_patch(frame_box)
        
        # Frame name
        frame_name = frame['name'][:10] + "..." if len(frame['name']) > 10 else frame['name']
        ax.text(x_pos + frame_width/2 - 0.1, 3, frame_name,
               ha='center', va='center', fontsize=9, fontweight='bold')
        
        # Arrow to next frame
        if i < len(frames_to_show) - 1:
            ax.annotate('', xy=(x_pos + frame_width, 3), xytext=(x_pos + frame_width - 0.2, 3),
                       arrowprops=dict(arrowstyle='->', color='#1976D2', lw=2))
    
    ax.text(6, 5, 'User Flow Based on Figma Frames', ha='center', va='center', 
           fontsize=14, fontweight='bold')
    
    # Save to base64
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight',
               facecolor='white', edgecolor='none')
    plt.close()
    
    buffer.seek(0)
    img_data = buffer.read()
    buffer.close()
    
    return base64.b64encode(img_data).decode()