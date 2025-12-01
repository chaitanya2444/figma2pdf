# dynamic_pdf_generator.py - PDF Generator Using Real Figma Data
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.colors import HexColor
from io import BytesIO
import base64

from .figma_parser import parse_figma_url
from .architecture_generator import generate_architecture_from_figma, create_flow_diagram

def generate_dynamic_pdf(figma_url: str, output_dir: str = "generated_pdfs") -> str:
    """
    ✅ 4. PDF GENERATOR USING PARSED CONTENT - NO TEMPLATES
    """
    
    print(f"GENERATING DYNAMIC PDF FOR: {figma_url}")
    
    # ✅ 1. Fetch fresh Figma data every time
    figma_data = parse_figma_url(figma_url)
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Create unique filename based on actual content
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = figma_data.get('file_name', 'figma_design').replace(' ', '_')
    content_hash = figma_data.get('content_hash', 'unknown')
    
    pdf_filename = f"{file_name}_{content_hash}_{timestamp}.pdf"
    pdf_path = os.path.join(output_dir, pdf_filename)
    
    # Setup PDF document
    doc = SimpleDocTemplate(pdf_path, pagesize=A4, topMargin=0.8*inch, bottomMargin=0.8*inch)
    styles = getSampleStyleSheet()
    
    # Custom styles
    if 'DynamicTitle' not in styles:
        styles.add(ParagraphStyle(name='DynamicTitle', fontSize=24, leading=30, alignment=TA_CENTER, spaceAfter=20))
    if 'DynamicHeading' not in styles:
        styles.add(ParagraphStyle(name='DynamicHeading', fontSize=18, leading=22, spaceAfter=12, textColor=HexColor('#2d3748')))
    if 'DynamicBody' not in styles:
        styles.add(ParagraphStyle(name='DynamicBody', fontSize=11, leading=16, spaceAfter=8, alignment=TA_JUSTIFY))
    if 'DynamicCode' not in styles:
        styles.add(ParagraphStyle(name='DynamicCode', fontName='Courier', fontSize=9, leading=12, spaceAfter=4))
    
    story = []
    
    # ✅ DYNAMIC TITLE FROM ACTUAL FIGMA FILE
    story.append(Paragraph(f"Design Analysis: {figma_data['file_name']}", styles['DynamicTitle']))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['DynamicBody']))
    story.append(Paragraph(f"Content Hash: {figma_data['content_hash']}", styles['DynamicCode']))
    story.append(Spacer(1, 20))
    
    # ✅ DYNAMIC SCREEN ANALYSIS FROM PARSED DATA
    story.append(Paragraph("Screen Analysis", styles['DynamicHeading']))
    story.append(Paragraph(figma_data['screen_analysis'], styles['DynamicCode']))
    story.append(Spacer(1, 15))
    
    # ✅ DYNAMIC COMPONENT ANALYSIS FROM PARSED DATA  
    story.append(Paragraph("Component Analysis", styles['DynamicHeading']))
    story.append(Paragraph(figma_data['component_analysis'], styles['DynamicCode']))
    story.append(Spacer(1, 15))
    
    # ✅ DYNAMIC PAGE STRUCTURE FROM PARSED DATA
    story.append(Paragraph("Page Structure", styles['DynamicHeading']))
    story.append(Paragraph(figma_data['page_structure'], styles['DynamicCode']))
    story.append(Spacer(1, 15))
    
    # ✅ DYNAMIC TEXT CONTENT FROM PARSED DATA
    story.append(Paragraph("Text Content Analysis", styles['DynamicHeading']))
    story.append(Paragraph(figma_data['text_analysis'], styles['DynamicCode']))
    
    story.append(PageBreak())
    
    # ✅ DETAILED FRAME BREAKDOWN FROM ACTUAL DATA
    story.append(Paragraph("Detailed Frame Breakdown", styles['DynamicHeading']))
    
    frames = figma_data.get('frames', [])
    if frames:
        # Create table with actual frame data
        frame_data = [['Frame Name', 'Page', 'Dimensions', 'Children']]
        for frame in frames:
            frame_data.append([
                frame['name'],
                frame['page'], 
                f"{frame['width']} x {frame['height']}",
                str(frame['children_count'])
            ])
        
        frame_table = Table(frame_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1*inch])
        frame_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#f7fafc')),
            ('TEXTCOLOR', (0, 0), (-1, -1), HexColor('#2d3748')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#e2e8f0'))
        ]))
        story.append(frame_table)
    else:
        story.append(Paragraph("No frames detected in this Figma file.", styles['DynamicBody']))
    
    story.append(PageBreak())
    
    # ✅ COMPONENT DETAILS FROM ACTUAL DATA
    story.append(Paragraph("Component Details", styles['DynamicHeading']))
    
    components = figma_data.get('components', [])
    if components:
        for comp in components:
            story.append(Paragraph(f"<b>{comp['name']}</b> ({comp['type']})", styles['DynamicBody']))
            story.append(Paragraph(f"Page: {comp['page']}", styles['DynamicCode']))
            if comp.get('description'):
                story.append(Paragraph(f"Description: {comp['description']}", styles['DynamicBody']))
            story.append(Spacer(1, 8))
    else:
        story.append(Paragraph("No reusable components found in this Figma file.", styles['DynamicBody']))
    
    story.append(PageBreak())
    
    # ✅ 3. UNIQUE ARCHITECTURE DIAGRAM FROM FIGMA DATA
    story.append(Paragraph("System Architecture (Generated from Figma Structure)", styles['DynamicHeading']))
    story.append(Spacer(1, 10))
    
    try:
        # Generate unique architecture diagram from actual Figma data
        arch_diagram_b64 = generate_architecture_from_figma(figma_data)
        
        if arch_diagram_b64:
            img_data = base64.b64decode(arch_diagram_b64)
            img_buffer = BytesIO(img_data)
            
            img = Image(img_buffer, width=7*inch, height=5*inch)
            img.hAlign = 'CENTER'
            story.append(img)
            story.append(Spacer(1, 20))
        
        # Add architecture explanation based on actual complexity
        frames_count = len(frames)
        components_count = len(components)
        
        if frames_count > 10 or components_count > 5:
            arch_text = f"Complex application with {frames_count} screens and {components_count} components requires microservices architecture with API gateway, multiple databases, and scalable infrastructure."
        elif frames_count > 5:
            arch_text = f"Medium complexity application with {frames_count} screens suggests modular monolith with clear service boundaries and database separation."
        else:
            arch_text = f"Simple application with {frames_count} screens can use single-service architecture with unified database and straightforward deployment."
        
        story.append(Paragraph(arch_text, styles['DynamicBody']))
        
    except Exception as e:
        story.append(Paragraph(f"Architecture diagram generation failed: {str(e)}", styles['DynamicBody']))
    
    story.append(PageBreak())
    
    # ✅ USER FLOW DIAGRAM FROM ACTUAL FRAMES
    if frames:
        story.append(Paragraph("User Flow (Based on Figma Frames)", styles['DynamicHeading']))
        story.append(Spacer(1, 10))
        
        try:
            flow_diagram_b64 = create_flow_diagram(frames)
            
            if flow_diagram_b64:
                img_data = base64.b64decode(flow_diagram_b64)
                img_buffer = BytesIO(img_data)
                
                img = Image(img_buffer, width=7*inch, height=3*inch)
                img.hAlign = 'CENTER'
                story.append(img)
                story.append(Spacer(1, 15))
            
            # Dynamic flow description
            flow_description = f"User journey flows through {len(frames)} main screens: "
            flow_description += " → ".join([f['name'] for f in frames[:5]])
            if len(frames) > 5:
                flow_description += f" → ... and {len(frames) - 5} more screens"
            
            story.append(Paragraph(flow_description, styles['DynamicBody']))
            
        except Exception as e:
            story.append(Paragraph(f"Flow diagram generation failed: {str(e)}", styles['DynamicBody']))
    
    # ✅ TECHNICAL RECOMMENDATIONS BASED ON ACTUAL COMPLEXITY
    story.append(PageBreak())
    story.append(Paragraph("Technical Recommendations", styles['DynamicHeading']))
    
    # Dynamic tech recommendations based on actual Figma analysis
    total_complexity = len(frames) + len(components) * 2
    text_nodes = figma_data.get('raw_data', {}).get('total_text_nodes', 0)
    
    if total_complexity > 20:
        tech_stack = "Enterprise-scale: React/Vue.js + Node.js/Python + PostgreSQL + Redis + Kubernetes + AWS/GCP"
        deployment = "Microservices with container orchestration, API gateway, and distributed caching"
    elif total_complexity > 10:
        tech_stack = "Medium-scale: React + Express.js + PostgreSQL + Docker + Cloud deployment"
        deployment = "Modular monolith with service separation and horizontal scaling capability"
    else:
        tech_stack = "Simple-scale: React + FastAPI/Express + SQLite/PostgreSQL + Vercel/Netlify"
        deployment = "Single service deployment with CDN and basic scaling"
    
    story.append(Paragraph(f"<b>Recommended Tech Stack:</b> {tech_stack}", styles['DynamicBody']))
    story.append(Paragraph(f"<b>Deployment Strategy:</b> {deployment}", styles['DynamicBody']))
    story.append(Paragraph(f"<b>Complexity Score:</b> {total_complexity} (Frames: {len(frames)}, Components: {len(components)}, Text: {text_nodes})", styles['DynamicBody']))
    
    # Build PDF
    doc.build(story)
    
    print(f"SUCCESS: DYNAMIC PDF GENERATED: {pdf_filename}")
    print(f"   File size: {os.path.getsize(pdf_path):,} bytes")
    print(f"   Content: {len(frames)} frames, {len(components)} components")
    
    return pdf_path