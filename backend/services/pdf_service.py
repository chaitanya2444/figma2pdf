from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
import os
import json
import time
import gc
from services.diagram_service import generate_architecture_diagram, get_diagram_as_base64
from services.ai_diagram_generator import generate_ai_architecture_diagram

def generate_pdf_from_data(data: dict, output_dir: str = "generated_pdfs"):
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{data.get('project_name', 'report').replace(' ', '_')}.pdf"
    pdf_path = os.path.join(output_dir, filename)
    
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle('CustomTitle', parent=styles['Title'], alignment=TA_CENTER, fontSize=24)
    story.append(Paragraph(f"<b>System Architecture Report: {data['project_name']}</b>", title_style))
    story.append(Spacer(1, 0.5*inch))
    
    # Overview
    story.append(Paragraph("<b>Overview</b>", styles['Heading2']))
    story.append(Paragraph(data['overview'], styles['Normal']))
    story.append(Spacer(1, 0.25*inch))
    
    # Pages & UI Elements
    story.append(Paragraph("<b>Pages & UI Elements</b>", styles['Heading2']))
    for page in data.get('pages', []):
        story.append(Paragraph(f"<b>Page: {page['name']}</b>", styles['Heading3']))
        for frame in page.get('key_frames', []):
            story.append(Paragraph(f"Frame: {frame['name']} ({frame.get('type', 'Unknown')})", styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
    
    for elem in data.get('ui_elements', []):
        story.append(Paragraph(f"<b>{elem['name']} ({elem['type']})</b>", styles['Heading3']))
        props = json.dumps(elem.get('properties', {}), indent=2)
        story.append(Paragraph(f"<pre>{props}</pre>", styles['Normal']))
    
    # Design System
    story.append(PageBreak())
    story.append(Paragraph("<b>Design System</b>", styles['Heading2']))
    ds = data.get('design_system', {})
    story.append(Paragraph(f"Colors: {json.dumps(ds.get('colors', {}))}", styles['Normal']))
    for ty in ds.get('typography', []):
        story.append(Paragraph(f"Typography: {ty['name']} - {ty['font_size']}px {ty['font_family']}", styles['Normal']))
    
    # User Flows & Recommendations
    story.append(Paragraph("<b>User Flows</b>", styles['Heading2']))
    for flow in data.get('main_user_flows', []):
        story.append(Paragraph(flow, styles['Normal']))
    
    story.append(Paragraph("<b>Tech Recommendations</b>", styles['Heading2']))
    story.append(Paragraph(data.get('tech_recommendations', 'N/A'), styles['Normal']))
    
    # AI-Generated Architecture Diagram (Eraser.io style)
    story.append(PageBreak())
    story.append(Paragraph("<b>AI-Generated System Architecture</b>", styles['Heading1']))
    story.append(Spacer(1, 20))
    
    try:
        from io import BytesIO
        import base64
        from reportlab.lib.utils import ImageReader
        
        # Generate AI architecture diagram
        diagram_b64 = generate_ai_architecture_diagram(data)
        
        if diagram_b64:
            # Decode base64 to image data
            img_data = base64.b64decode(diagram_b64.split(',')[1])
            
            # Create ImageReader from memory data
            img_buffer = BytesIO(img_data)
            img_reader = ImageReader(img_buffer)
            
            # Add image to PDF from memory
            story.append(Image(img_reader, width=7.5*inch, height=5.5*inch))
            print("DEBUG: AI diagram added successfully")
            
        else:
            story.append(Paragraph("AI architecture diagram could not be generated.", styles['Normal']))
            
    except Exception as e:
        print(f"DEBUG: AI diagram generation failed: {e}")
        story.append(Paragraph(f"AI diagram generation failed: {str(e)}", styles['Normal']))
    
    doc.build(story)
    return pdf_path