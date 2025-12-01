import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from services.diagram_service import generate_architecture_diagram

def generate_pdf_from_data(data: dict, output_dir: str = "generated_pdfs") -> str:
    os.makedirs(output_dir, exist_ok=True)
    
    # Unique filename every time
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    project_name = data.get("name", data.get("project_name", "Untitled")).replace(" ", "_")
    pdf_path = os.path.join(output_dir, f"{project_name}_Architecture_Report_{timestamp}.pdf")

    doc = SimpleDocTemplate(pdf_path, pagesize=A4, topMargin=1*inch, bottomMargin=1*inch)
    styles = getSampleStyleSheet()
    
    # Custom styles
    styles.add(ParagraphStyle(name='Title', fontSize=28, leading=34, alignment=TA_CENTER, spaceAfter=30))
    styles.add(ParagraphStyle(name='Heading', fontSize=18, spaceAfter=14, textColor='#1e40af'))
    styles.add(ParagraphStyle(name='Body', fontSize=12, leading=18, spaceAfter=12, alignment=TA_JUSTIFY))

    story = []

    # Title
    story.append(Paragraph(f"System Architecture Report: {data.get('name', data.get('project_name', 'Untitled'))}", styles['Title']))
    story.append(Spacer(1, 20))

    # Overview - DYNAMIC based on actual Figma data
    story.append(Paragraph("Overview", styles['Heading']))
    
    # Extract real frames from Figma data
    frames = []
    if "document" in data:
        for page in data.get("document", {}).get("children", []):
            if page.get("type") == "CANVAS":
                for child in page.get("children", []):
                    if child.get("type") == "FRAME":
                        frames.append(child["name"])
    else:
        # LLM-parsed data
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
    story.append(Paragraph(overview, styles['Body']))
    story.append(Spacer(1, 20))

    # Pages & UI Elements - DYNAMIC from actual Figma data
    story.append(Paragraph("Pages & UI Elements", styles['Heading']))
    
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
        story.append(Paragraph(f"• <b>{frame}</b> — {description}", styles['Body']))
    
    story.append(Spacer(1, 20))
    story.append(PageBreak())

    # Tech Stack + User Flow
    story.append(Paragraph("Recommended Tech Stack & User Flow", styles['Heading']))
    stack_text = f"""
    • <b>Frontend:</b> React + TypeScript + Tailwind CSS<br/>
    • <b>Backend:</b> FastAPI (Python) or Node.js + Express<br/>
    • <b>Database:</b> PostgreSQL + Redis for caching<br/>
    • <b>Auth:</b> NextAuth / Firebase Auth<br/>
    • <b>Deployment:</b> Vercel + Railway<br/><br/>
    <b>Primary User Journey:</b> {' → '.join([f.split()[0] for f in frames[:6]])}
    """
    story.append(Paragraph(stack_text, styles['Body']))
    story.append(PageBreak())

    # AI-Generated System Architecture
    story.append(Paragraph("AI-Generated System Architecture", styles['Heading']))
    story.append(Spacer(1, 20))

    try:
        diagram_path = generate_architecture_diagram(data)   # ← This now returns a STRING path
        
        if os.path.exists(diagram_path):
            img = Image(diagram_path, width=7*inch, height=4.5*inch)
            img.hAlign = 'CENTER'
            story.append(img)
            story.append(Spacer(1, 30))
            
            # Optional: clean up the diagram file after embedding
            try:
                os.remove(diagram_path)
            except:
                pass
        else:
            story.append(Paragraph("Diagram generated but file not found.", styles['Normal']))
            
    except Exception as e:
        story.append(Paragraph(f"Diagram error: {str(e)}", styles['Normal']))

    # Build PDF
    doc.build(story)
    print(f"Dynamic architecture report generated: {pdf_path}")
    return pdf_path