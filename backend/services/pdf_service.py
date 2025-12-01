import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.colors import HexColor
from services.ai_diagram_generator import generate_ai_architecture_diagram
import base64
from io import BytesIO

def generate_pdf_from_data(data: dict, output_dir: str = "generated_pdfs") -> str:
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    project_name = data.get("name", "AI_Analysis").replace(" ", "_")
    pdf_path = os.path.join(output_dir, f"{project_name}_Comprehensive_Analysis_{timestamp}.pdf")

    doc = SimpleDocTemplate(pdf_path, pagesize=A4, topMargin=0.8*inch, bottomMargin=0.8*inch)
    styles = getSampleStyleSheet()
    
    # Enhanced custom styles
    if 'CustomTitle' not in styles:
        styles.add(ParagraphStyle(name='CustomTitle', fontSize=24, leading=30, alignment=TA_CENTER, spaceAfter=20, textColor=HexColor('#1a365d')))
    if 'CustomHeading1' not in styles:
        styles.add(ParagraphStyle(name='CustomHeading1', fontSize=18, leading=22, spaceAfter=12, textColor=HexColor('#2d3748'), spaceBefore=20))
    if 'CustomHeading2' not in styles:
        styles.add(ParagraphStyle(name='CustomHeading2', fontSize=14, leading=18, spaceAfter=8, textColor=HexColor('#4a5568'), spaceBefore=15))
    if 'CustomBody' not in styles:
        styles.add(ParagraphStyle(name='CustomBody', fontSize=11, leading=16, spaceAfter=8, alignment=TA_JUSTIFY))
    if 'CustomFeature' not in styles:
        styles.add(ParagraphStyle(name='CustomFeature', fontSize=10, leading=14, spaceAfter=6, leftIndent=20))

    story = []

    # Title Page
    story.append(Paragraph(f"Comprehensive Design Analysis", styles['CustomTitle']))
    story.append(Paragraph(f"{data.get('name', 'Application')}", styles['CustomTitle']))
    story.append(Spacer(1, 30))
    
    # Executive Summary
    story.append(Paragraph("Executive Summary", styles['CustomHeading1']))
    story.append(Paragraph(data.get('description', 'Comprehensive analysis of the design system and application architecture.'), styles['CustomBody']))
    
    summary_data = [
        ['Category', data.get('category', 'Application')],
        ['Target Audience', data.get('target_audience', 'End users')],
        ['Business Model', data.get('business_model', 'To be determined')],
        ['Development Timeline', data.get('development_timeline', 'Phased approach')]
    ]
    
    summary_table = Table(summary_data, colWidths=[2*inch, 4*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), HexColor('#f7fafc')),
        ('TEXTCOLOR', (0, 0), (-1, -1), HexColor('#2d3748')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, HexColor('#e2e8f0'))
    ]))
    story.append(summary_table)
    story.append(PageBreak())

    # Key Features Analysis
    story.append(Paragraph("Key Features & Functionality", styles['CustomHeading1']))
    features = data.get('key_features', [])
    for i, feature in enumerate(features, 1):
        story.append(Paragraph(f"{i}. {feature}", styles['CustomFeature']))
    story.append(Spacer(1, 20))

    # UI Components Analysis
    story.append(Paragraph("UI Components Architecture", styles['CustomHeading1']))
    components = data.get('ui_components', [])
    for component in components:
        story.append(Paragraph(f"• {component}", styles['CustomBody']))
    story.append(Spacer(1, 20))

    # Screen Flow Analysis
    story.append(Paragraph("Screen Flow & User Journey", styles['CustomHeading1']))
    pages = data.get('pages', [])
    for page in pages:
        story.append(Paragraph(f"Flow: {page.get('name', 'Main Flow')}", styles['CustomHeading2']))
        frames = page.get('key_frames', [])
        for frame in frames:
            frame_name = frame.get('name', 'Screen')
            frame_desc = frame.get('description', 'User interface screen')
            story.append(Paragraph(f"<b>{frame_name}:</b> {frame_desc}", styles['CustomBody']))
    
    story.append(Paragraph(f"<b>Complete User Journey:</b> {data.get('user_flows', 'User interaction flow')}", styles['CustomBody']))
    story.append(PageBreak())

    # Design System
    story.append(Paragraph("Design System Specifications", styles['CustomHeading1']))
    
    # Color Palette
    colors = data.get('colors', {})
    if colors:
        story.append(Paragraph("Color Palette", styles['CustomHeading2']))
        color_data = [[color_name, color_value] for color_name, color_value in colors.items()]
        color_table = Table(color_data, colWidths=[1.5*inch, 1.5*inch])
        color_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#4a5568')),
            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#ffffff')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#e2e8f0'))
        ]))
        story.append(color_table)
        story.append(Spacer(1, 15))

    # Typography
    typography = data.get('typography', {})
    if typography:
        story.append(Paragraph("Typography System", styles['CustomHeading2']))
        story.append(Paragraph(f"Primary Font: {typography.get('primary_font', 'System font')}", styles['CustomBody']))
        story.append(Paragraph(f"Secondary Font: {typography.get('secondary_font', 'System font')}", styles['CustomBody']))
        
        font_sizes = typography.get('font_sizes', {})
        if font_sizes:
            for size_type, size_value in font_sizes.items():
                story.append(Paragraph(f"{size_type.title()}: {size_value}", styles['CustomBody']))
    
    story.append(PageBreak())

    # Technical Architecture
    story.append(Paragraph("Technical Architecture & Requirements", styles['CustomHeading1']))
    tech_req = data.get('technical_requirements', {})
    
    tech_sections = [
        ('Frontend Technology', tech_req.get('frontend', 'Modern web framework')),
        ('Backend Infrastructure', tech_req.get('backend', 'Scalable server architecture')),
        ('Database Strategy', tech_req.get('database', 'Optimized data storage')),
        ('API Integrations', tech_req.get('apis', 'Third-party services')),
        ('Deployment Strategy', tech_req.get('deployment', 'Cloud-based deployment'))
    ]
    
    for section_name, section_content in tech_sections:
        story.append(Paragraph(section_name, styles['CustomHeading2']))
        story.append(Paragraph(section_content, styles['CustomBody']))

    # Scalability & Security
    story.append(Paragraph("Scalability Considerations", styles['CustomHeading2']))
    story.append(Paragraph(data.get('scalability_considerations', 'Designed for horizontal scaling and performance optimization.'), styles['CustomBody']))
    
    story.append(Paragraph("Security Requirements", styles['CustomHeading2']))
    story.append(Paragraph(data.get('security_requirements', 'Industry-standard security measures and data protection protocols.'), styles['CustomBody']))
    
    story.append(PageBreak())

    # AI Architecture Diagram
    story.append(Paragraph("AI-Generated System Architecture", styles['CustomHeading1']))
    story.append(Spacer(1, 10))

    try:
        diagram_base64 = generate_ai_architecture_diagram(data)
        
        if diagram_base64 and diagram_base64.startswith("data:image/png;base64,"):
            base64_data = diagram_base64.split(',')[1]
            img_data = base64.b64decode(base64_data)
            img_buffer = BytesIO(img_data)
            
            img = Image(img_buffer, width=7*inch, height=4.5*inch)
            img.hAlign = 'CENTER'
            story.append(img)
            story.append(Spacer(1, 20))
        else:
            story.append(Paragraph("Architecture diagram generation in progress...", styles['CustomBody']))
            
    except Exception as e:
        story.append(Paragraph(f"Architecture visualization: {str(e)}", styles['CustomBody']))

    # Competitive Analysis & Market Position
    story.append(Paragraph("Market Analysis", styles['CustomHeading1']))
    story.append(Paragraph(data.get('competitive_analysis', 'Positioned to compete effectively in the target market with unique value propositions.'), styles['CustomBody']))

    # Build PDF
    doc.build(story)
    print(f"Comprehensive AI analysis report generated: {pdf_path}")
    return pdf_path