import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from services.ai_diagram_generator import generate_ai_architecture_diagram
import base64
from io import BytesIO

def generate_pdf_from_data(data: dict, output_dir: str = "generated_pdfs") -> str:
    os.makedirs(output_dir, exist_ok=True)
    
    # Unique filename every time
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    project_name = data.get("name", data.get("project_name", "Untitled")).replace(" ", "_")
    pdf_path = os.path.join(output_dir, f"{project_name}_Architecture_Report_{timestamp}.pdf")

    doc = SimpleDocTemplate(pdf_path, pagesize=A4, topMargin=1*inch, bottomMargin=1*inch)
    styles = getSampleStyleSheet()
    
    # Custom styles - check if they exist first
    if 'CustomTitle' not in styles:
        styles.add(ParagraphStyle(name='CustomTitle', fontSize=28, leading=34, alignment=TA_CENTER, spaceAfter=30))
    if 'CustomHeading' not in styles:
        styles.add(ParagraphStyle(name='CustomHeading', fontSize=18, spaceAfter=14, textColor='#1e40af'))
    if 'CustomBody' not in styles:
        styles.add(ParagraphStyle(name='CustomBody', fontSize=12, leading=18, spaceAfter=12, alignment=TA_JUSTIFY))

    story = []

    # Title
    story.append(Paragraph(f"System Architecture Report: {data.get('name', data.get('project_name', 'Untitled'))}", styles['CustomTitle']))
    story.append(Spacer(1, 20))

    # Overview - DYNAMIC based on actual Figma data
    story.append(Paragraph("Overview", styles['CustomHeading']))
    
    # Extract real frames from Figma data
    frames = []
    for page in data.get('pages', []):
        for frame in page.get('key_frames', []):
            frames.append(frame.get('name', 'Component'))
    
    # Determine app type from actual frame names
    app_type = "e-commerce" if any(word in ' '.join(frames).lower() for word in ['shop', 'product', 'cart', 'checkout', 'store']) else "content management"
    
    overview = f"""
    <b>Design file:</b> {data.get('name', data.get('project_name', 'Untitled'))}<br/><br/>
    This Figma file contains <b>{len(frames)} screens/frames</b>. 
    The design suggests a <b>{app_type}</b> application with modern UI patterns.
    Key screens detected: <b>{', '.join(frames[:5])}</b>{'...' if len(frames) > 5 else ''}.
    """
    story.append(Paragraph(overview, styles['CustomBody']))
    story.append(Spacer(1, 20))

    # Pages & UI Elements - DYNAMIC from actual Figma data
    story.append(Paragraph("Pages & UI Elements", styles['CustomHeading']))
    
    screen_descriptions = {
        "landing": "Primary entry point with hero section and navigation",
        "home": "Main dashboard with personalized content",
        "product": "Detailed product view with images and pricing",
        "shop": "Product catalog with filtering and search",
        "about": "Company information and team profiles",
        "article": "Long-form content reading experience",
        "blog": "Content hub with article previews",
        "dashboard": "User control panel with analytics",
        "profile": "User account management interface",
        "cart": "Shopping cart with item management",
        "checkout": "Multi-step payment flow"
    }
    
    for i, frame in enumerate(frames, 1):
        frame_key = next((key for key in screen_descriptions.keys() if key in frame.lower()), None)
        description = screen_descriptions.get(frame_key, "Interactive screen with modern UI patterns")
        story.append(Paragraph(f"• <b>{frame}</b> — {description}", styles['CustomBody']))
    
    story.append(Spacer(1, 20))
    story.append(PageBreak())

    # Tech Stack + User Flow
    story.append(Paragraph("Recommended Tech Stack & User Flow", styles['CustomHeading']))
    stack_text = f"""
    • <b>Frontend:</b> React + TypeScript + Tailwind CSS<br/>
    • <b>Backend:</b> FastAPI (Python) or Node.js + Express<br/>
    • <b>Database:</b> PostgreSQL + Redis for caching<br/>
    • <b>Auth:</b> NextAuth / Firebase Auth<br/>
    • <b>Deployment:</b> Vercel + Railway<br/><br/>
    <b>Primary User Journey:</b> {' → '.join([f.split()[0] for f in frames[:6]])}
    """
    story.append(Paragraph(stack_text, styles['CustomBody']))
    story.append(PageBreak())

    # AI-Generated System Architecture
    story.append(Paragraph("AI-Generated System Architecture", styles['CustomHeading']))
    story.append(Spacer(1, 20))

    try:
        diagram_base64 = generate_ai_architecture_diagram(data)
        
        if diagram_base64 and diagram_base64.startswith("data:image/png;base64,"):
            # Extract base64 data and create BytesIO object
            base64_data = diagram_base64.split(',')[1]
            img_data = base64.b64decode(base64_data)
            img_buffer = BytesIO(img_data)
            
            img = Image(img_buffer, width=7*inch, height=4.5*inch)
            img.hAlign = 'CENTER'
            story.append(img)
            story.append(Spacer(1, 30))
        else:
            story.append(Paragraph("AI diagram generation failed.", styles['Normal']))
            
    except Exception as e:
        story.append(Paragraph(f"Diagram error: {str(e)}", styles['Normal']))

    # Build PDF
    doc.build(story)
    print(f"Dynamic architecture report generated: {pdf_path}")
    return pdf_path