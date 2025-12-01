import os
import json
import base64
import time
import gc
from pathlib import Path
from uuid import uuid4
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from io import BytesIO


TEMP_DIR = Path("C:/temp/figma2pdf")
TEMP_DIR.mkdir(parents=True, exist_ok=True)

def generate_architecture_prompt(figma_data: dict) -> str:
    """Generate architecture prompt from Figma data"""
    pages = figma_data.get('pages', [])
    components = []
    
    for page in pages:
        for frame in page.get('key_frames', []):
            components.append(frame.get('name', 'Component'))
    
    project_name = figma_data.get('project_name', figma_data.get('name', 'App'))
    
    prompt = f"""
    Create a system architecture for {project_name} with these components: {', '.join(components[:5])}.
    
    Include:
    - User/Client layer
    - API Gateway/Load Balancer
    - Microservices (based on components)
    - Database layer
    - External services (payment, auth)
    
    Make it an e-commerce/web app architecture with modern cloud patterns.
    """
    
    return prompt

def create_architecture_diagram(prompt: str, figma_data: dict = None) -> str:
    """Create a simple architecture diagram using matplotlib"""
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis('off')
    
    # Define colors
    user_color = '#E3F2FD'
    api_color = '#FFF3E0'
    service_color = '#E8F5E8'
    db_color = '#FCE4EC'
    
    # User Layer
    user_box = patches.Rectangle((1, 6.5), 2, 1, linewidth=2, 
                                edgecolor='#1976D2', facecolor=user_color)
    ax.add_patch(user_box)
    ax.text(2, 7, 'Users/Clients', ha='center', va='center', fontweight='bold')
    
    # API Gateway
    api_box = patches.Rectangle((4, 6.5), 2, 1, linewidth=2,
                               edgecolor='#F57C00', facecolor=api_color)
    ax.add_patch(api_box)
    ax.text(5, 7, 'API Gateway', ha='center', va='center', fontweight='bold')
    
    # Dynamic Microservices based on Figma data
    default_services = ['Auth Service', 'Product Service', 'Cart Service', 'Payment Service']
    
    if figma_data:
        components = [frame.get('name', '') for page in figma_data.get('pages', []) 
                     for frame in page.get('key_frames', [])][:4]
        services = [f"{name.split()[0]} Service" for name in components if name] or default_services
    else:
        services = default_services
    for i, service in enumerate(services):
        x = 1 + i * 2
        service_box = patches.Rectangle((x, 4), 1.5, 1, linewidth=2,
                                       edgecolor='#388E3C', facecolor=service_color)
        ax.add_patch(service_box)
        ax.text(x + 0.75, 4.5, service, ha='center', va='center', fontsize=9, fontweight='bold')
    
    # Database
    db_box = patches.Rectangle((3.5, 1.5), 3, 1, linewidth=2,
                              edgecolor='#C2185B', facecolor=db_color)
    ax.add_patch(db_box)
    ax.text(5, 2, 'Database\n(PostgreSQL)', ha='center', va='center', fontweight='bold')
    
    # Arrows
    # User to API
    ax.arrow(3, 7, 0.8, 0, head_width=0.1, head_length=0.1, fc='black', ec='black')
    
    # API to Services
    for i in range(4):
        x = 1.75 + i * 2
        ax.arrow(5, 6.4, x - 4.5, -1.2, head_width=0.1, head_length=0.1, fc='black', ec='black')
    
    # Services to DB
    for i in range(4):
        x = 1.75 + i * 2
        ax.arrow(x, 4, 5 - x, -1.3, head_width=0.1, head_length=0.1, fc='black', ec='black')
    
    plt.title('System Architecture Diagram', fontsize=16, fontweight='bold', pad=20)
    
    # Save to memory
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()
    gc.collect()
    
    buffer.seek(0)
    img_data = buffer.read()
    buffer.close()
    
    return base64.b64encode(img_data).decode()



def generate_ai_architecture_diagram(figma_data: dict) -> str:
    """Main function to generate architecture diagram from Figma data"""
    try:
        prompt = generate_architecture_prompt(figma_data)
        diagram_b64 = create_architecture_diagram(prompt, figma_data)
        return f"data:image/png;base64,{diagram_b64}"
    except Exception as e:
        print(f"Diagram generation error: {e}")
        return ""