import os
import json
import base64
import gc
from typing import Dict, Any
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
from io import BytesIO
import numpy as np

def generate_ai_architecture_diagram(figma_data: dict) -> str:
    """Generate dynamic architecture diagram based on AI analysis"""
    
    try:
        # Extract data for diagram generation
        app_name = figma_data.get('name', 'Application')
        category = figma_data.get('category', 'Web Application')
        tech_req = figma_data.get('technical_requirements', {})
        features = figma_data.get('key_features', [])
        
        # Create dynamic diagram
        fig, ax = plt.subplots(1, 1, figsize=(14, 10))
        ax.set_xlim(0, 14)
        ax.set_ylim(0, 10)
        ax.axis('off')
        
        # Dynamic color scheme based on app category
        colors = get_category_colors(category)
        
        # Title
        ax.text(7, 9.5, f'{app_name} - System Architecture', 
                ha='center', va='center', fontsize=16, fontweight='bold')
        
        # Client Layer
        client_box = FancyBboxPatch((1, 8), 3, 1, 
                                   boxstyle="round,pad=0.1", 
                                   facecolor=colors['client'], 
                                   edgecolor='#2d3748', linewidth=2)
        ax.add_patch(client_box)
        ax.text(2.5, 8.5, 'Client Applications\n(Web, Mobile, Desktop)', 
                ha='center', va='center', fontsize=10, fontweight='bold')
        
        # Load Balancer/CDN
        lb_box = FancyBboxPatch((10, 8), 3, 1,
                               boxstyle="round,pad=0.1",
                               facecolor=colors['network'],
                               edgecolor='#2d3748', linewidth=2)
        ax.add_patch(lb_box)
        ax.text(11.5, 8.5, 'Load Balancer\n& CDN',
                ha='center', va='center', fontsize=10, fontweight='bold')
        
        # API Gateway
        api_box = FancyBboxPatch((5.5, 6.5), 3, 1,
                                boxstyle="round,pad=0.1",
                                facecolor=colors['api'],
                                edgecolor='#2d3748', linewidth=2)
        ax.add_patch(api_box)
        ax.text(7, 7, f'API Gateway\n({tech_req.get("backend", "REST API")})',
                ha='center', va='center', fontsize=10, fontweight='bold')
        
        # Microservices (dynamic based on features)
        services = generate_services_from_features(features, tech_req)
        service_positions = [(2, 5), (5, 5), (8, 5), (11, 5)]
        
        for i, (service, pos) in enumerate(zip(services[:4], service_positions)):
            service_box = FancyBboxPatch((pos[0]-0.8, pos[1]-0.4), 1.6, 0.8,
                                        boxstyle="round,pad=0.05",
                                        facecolor=colors['service'],
                                        edgecolor='#2d3748', linewidth=1)
            ax.add_patch(service_box)
            ax.text(pos[0], pos[1], service, ha='center', va='center', 
                   fontsize=8, fontweight='bold')
        
        # Database Layer
        db_type = tech_req.get('database', 'Database')
        db_box = FancyBboxPatch((2, 3), 4, 1,
                               boxstyle="round,pad=0.1",
                               facecolor=colors['database'],
                               edgecolor='#2d3748', linewidth=2)
        ax.add_patch(db_box)
        ax.text(4, 3.5, f'Primary Database\n({db_type})',
                ha='center', va='center', fontsize=10, fontweight='bold')
        
        # Cache Layer
        cache_box = FancyBboxPatch((8, 3), 3, 1,
                                  boxstyle="round,pad=0.1",
                                  facecolor=colors['cache'],
                                  edgecolor='#2d3748', linewidth=2)
        ax.add_patch(cache_box)
        ax.text(9.5, 3.5, 'Cache Layer\n(Redis/Memcached)',
                ha='center', va='center', fontsize=10, fontweight='bold')
        
        # External Services
        external_services = get_external_services(category, tech_req)
        ext_positions = [(1.5, 1.5), (4.5, 1.5), (7.5, 1.5), (10.5, 1.5)]
        
        for service, pos in zip(external_services[:4], ext_positions):
            ext_box = FancyBboxPatch((pos[0]-0.7, pos[1]-0.3), 1.4, 0.6,
                                    boxstyle="round,pad=0.05",
                                    facecolor=colors['external'],
                                    edgecolor='#2d3748', linewidth=1)
            ax.add_patch(ext_box)
            ax.text(pos[0], pos[1], service, ha='center', va='center',
                   fontsize=7, fontweight='bold')
        
        # Draw connections
        draw_connections(ax, colors['connection'])
        
        # Add deployment info
        deployment = tech_req.get('deployment', 'Cloud Platform')
        ax.text(7, 0.5, f'Deployment: {deployment}',
                ha='center', va='center', fontsize=9, style='italic')
        
        # Save to memory
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight',
                   facecolor='white', edgecolor='none', pad_inches=0.2)
        plt.close()
        gc.collect()
        
        buffer.seek(0)
        img_data = buffer.read()
        buffer.close()
        
        return base64.b64encode(img_data).decode()
        
    except Exception as e:
        print(f"Diagram generation error: {e}")
        return ""

def get_category_colors(category: str) -> Dict[str, str]:
    """Get color scheme based on app category"""
    
    color_schemes = {
        'E-commerce': {
            'client': '#FFF3E0', 'network': '#E8F5E8', 'api': '#E3F2FD',
            'service': '#F3E5F5', 'database': '#FCE4EC', 'cache': '#FFF8E1',
            'external': '#F1F8E9', 'connection': '#424242'
        },
        'Social': {
            'client': '#E8EAF6', 'network': '#E0F2F1', 'api': '#FFF3E0',
            'service': '#FCE4EC', 'database': '#E1F5FE', 'cache': '#F9FBE7',
            'external': '#FFF8E1', 'connection': '#5D4037'
        },
        'Fintech': {
            'client': '#E8F5E8', 'network': '#E3F2FD', 'api': '#FFF3E0',
            'service': '#F3E5F5', 'database': '#E0F2F1', 'cache': '#FCE4EC',
            'external': '#FFF8E1', 'connection': '#37474F'
        }
    }
    
    return color_schemes.get(category, color_schemes['E-commerce'])

def generate_services_from_features(features: list, tech_req: dict) -> list:
    """Generate microservices based on app features"""
    
    services = []
    
    # Analyze features to determine services
    feature_text = ' '.join(features).lower()
    
    if 'auth' in feature_text or 'login' in feature_text or 'user' in feature_text:
        services.append('Auth Service')
    if 'payment' in feature_text or 'checkout' in feature_text or 'billing' in feature_text:
        services.append('Payment Service')
    if 'notification' in feature_text or 'message' in feature_text or 'email' in feature_text:
        services.append('Notification Service')
    if 'search' in feature_text or 'filter' in feature_text or 'discovery' in feature_text:
        services.append('Search Service')
    if 'analytics' in feature_text or 'tracking' in feature_text or 'metrics' in feature_text:
        services.append('Analytics Service')
    if 'content' in feature_text or 'media' in feature_text or 'upload' in feature_text:
        services.append('Content Service')
    
    # Add core service based on tech stack
    backend = tech_req.get('backend', '')
    if 'node' in backend.lower():
        services.insert(0, 'Core API (Node.js)')
    elif 'python' in backend.lower() or 'fastapi' in backend.lower():
        services.insert(0, 'Core API (Python)')
    elif 'java' in backend.lower():
        services.insert(0, 'Core API (Java)')
    else:
        services.insert(0, 'Core API Service')
    
    return services[:4]  # Limit to 4 services for layout

def get_external_services(category: str, tech_req: dict) -> list:
    """Get external services based on category and tech requirements"""
    
    base_services = ['Monitoring', 'Logging']
    
    # Add category-specific services
    if 'ecommerce' in category.lower() or 'shop' in category.lower():
        base_services.extend(['Payment Gateway', 'Shipping API'])
    elif 'social' in category.lower():
        base_services.extend(['Push Notifications', 'Media CDN'])
    elif 'fintech' in category.lower() or 'finance' in category.lower():
        base_services.extend(['Banking API', 'KYC Service'])
    else:
        base_services.extend(['Email Service', 'File Storage'])
    
    # Add from tech requirements
    apis = tech_req.get('apis', '')
    if 'stripe' in apis.lower():
        base_services.append('Stripe')
    if 'aws' in apis.lower():
        base_services.append('AWS Services')
    
    return base_services

def draw_connections(ax, color: str):
    """Draw connection lines between components"""
    
    # Client to Load Balancer
    ax.annotate('', xy=(10, 8.5), xytext=(4, 8.5),
                arrowprops=dict(arrowstyle='->', color=color, lw=2))
    
    # Load Balancer to API Gateway
    ax.annotate('', xy=(7, 7.5), xytext=(10.5, 8),
                arrowprops=dict(arrowstyle='->', color=color, lw=2))
    
    # API Gateway to Services
    for x in [2, 5, 8, 11]:
        ax.annotate('', xy=(x, 5.4), xytext=(7, 6.5),
                    arrowprops=dict(arrowstyle='->', color=color, lw=1.5))
    
    # Services to Database
    for x in [2, 5]:
        ax.annotate('', xy=(4, 4), xytext=(x, 4.6),
                    arrowprops=dict(arrowstyle='->', color=color, lw=1.5))
    
    # Services to Cache
    for x in [8, 11]:
        ax.annotate('', xy=(9.5, 4), xytext=(x, 4.6),
                    arrowprops=dict(arrowstyle='->', color=color, lw=1.5))
    
    # External services connections
    for x in [1.5, 4.5, 7.5, 10.5]:
        ax.annotate('', xy=(x, 2.1), xytext=(x, 4.6),
                    arrowprops=dict(arrowstyle='->', color=color, lw=1, alpha=0.7))