# pdf_service.py
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.units import mm
from reportlab.lib import colors

def _make_styles():
    styles = getSampleStyleSheet()
    if 'DevHeading1' not in styles:
        styles.add(ParagraphStyle(name='DevHeading1', fontSize=18, leading=22, spaceAfter=8))
    if 'DevHeading2' not in styles:
        styles.add(ParagraphStyle(name='DevHeading2', fontSize=14, leading=18, spaceAfter=6))
    if 'DevNormalSmall' not in styles:
        styles.add(ParagraphStyle(name='DevNormalSmall', fontSize=9, leading=12, spaceAfter=4))
    if 'DevMono' not in styles:
        styles.add(ParagraphStyle(name='DevMono', fontName='Courier', fontSize=9))
    return styles

def _add_kv_table(story, items, styles):
    # items: list of (key, value)
    data = [[Paragraph(f"<b>{k}</b>", styles['DevNormalSmall']), Paragraph(str(v), styles['DevNormalSmall'])] for k,v in items]
    t = Table(data, colWidths=[60*mm, 110*mm], hAlign='LEFT')
    t.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.lightgrey),
        ('BOX', (0,0), (-1,-1), 0.25, colors.lightgrey),
    ]))
    story.append(t)
    story.append(Spacer(1,6))

def generate_pdf_from_structure(struct: dict, output_dir: str = "generated_pdfs") -> str:
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"{struct.get('file_name','figma')}_{struct.get('document_hash','unknown')}_{timestamp}.pdf"
    safe_name = "".join(c if c.isalnum() or c in ('-', '_', '.') else '_' for c in fname)
    pdf_path = os.path.join(output_dir, safe_name)

    styles = _make_styles()
    doc = SimpleDocTemplate(pdf_path, pagesize=A4, leftMargin=20*mm, rightMargin=20*mm, topMargin=20*mm, bottomMargin=20*mm)
    story = []

    # Title
    story.append(Paragraph(struct.get("file_name", "Figma Document"), styles['DevHeading1']))
    story.append(Paragraph(f"Generated: {datetime.now().isoformat()}", styles['DevNormalSmall']))
    story.append(Spacer(1,8))

    # Summary / metadata
    story.append(Paragraph("Document Summary", styles['DevHeading2']))
    meta_items = [
        ("File name", struct.get("file_name")),
        ("Last modified", struct.get("last_modified")),
        ("Pages", len(struct.get("pages", []))),
        ("Layers collected", len(struct.get("layers", []))),
        ("Text nodes", len(struct.get("text_nodes", []))),
        ("Components", len(struct.get("components", [])))
    ]
    _add_kv_table(story, meta_items, styles)
    story.append(PageBreak())

    # Pages & Frames overview
    story.append(Paragraph("Pages & Frames", styles['DevHeading2']))
    for page in struct.get("pages", []):
        story.append(Paragraph(f"Page: {page.get('name')} ({page.get('id')})", styles['DevHeading2']))
        # list frames in that page
        frames = [l for l in struct.get("layers", []) if l.get("page") == page.get("name") and l.get("type") == "FRAME"]
        if not frames:
            story.append(Paragraph("No frames detected on this page.", styles['DevNormalSmall']))
        else:
            for f in frames:
                items = [
                    ("Name", f.get("name")),
                    ("Type", f.get("type")),
                    ("Size (w x h)", f"{f.get('width')} x {f.get('height')}"),
                    ("Children count", f.get("children_count")),
                    ("Constraints", f.get("constraints"))
                ]
                _add_kv_table(story, items, styles)
        story.append(Spacer(1,6))
    story.append(PageBreak())

    # Components and reusable elements
    story.append(Paragraph("Components & Reusable Elements", styles['DevHeading2']))
    components = struct.get("components", [])
    if not components:
        story.append(Paragraph("No components defined in this Figma file.", styles['DevNormalSmall']))
    else:
        for comp in components:
            items = [
                ("Name", comp.get("name")),
                ("ID", comp.get("id")),
                ("Description", comp.get("description") or "—")
            ]
            _add_kv_table(story, items, styles)
    story.append(PageBreak())

    # Text content (useful for developer copy)
    story.append(Paragraph("Text Content (copy for developers)", styles['DevHeading2']))
    text_nodes = struct.get("text_nodes", [])
    if not text_nodes:
        story.append(Paragraph("No text nodes found.", styles['DevNormalSmall']))
    else:
        # Put a few per page
        for t in text_nodes:
            story.append(Paragraph(f"<b>{t.get('name') or t.get('id')}</b>", styles['DevNormalSmall']))
            content = (t.get("characters") or "").strip()
            if len(content) > 800:
                content = content[:800] + " ... (truncated)"
            story.append(Paragraph(content.replace("\n", "<br/>"), styles['DevMono']))
            style_info = t.get("style") or {}
            style_items = [("Font family", style_info.get("fontFamily")), ("Font size", style_info.get("fontSize")), ("Font weight", style_info.get("fontWeight"))]
            _add_kv_table(story, style_items, styles)
            story.append(Spacer(1,6))
    story.append(PageBreak())

    # Interactions / prototypes
    story.append(Paragraph("Prototype & Interaction Flows", styles['DevHeading2']))
    interactions = struct.get("interactions", [])
    if not interactions:
        story.append(Paragraph("No prototype interactions detected.", styles['DevNormalSmall']))
    else:
        for it in interactions:
            story.append(Paragraph(f"Node: {it.get('name')} ({it.get('id')})", styles['DevNormalSmall']))
            story.append(Paragraph(f"Prototype data: {str(it.get('prototype'))}", styles['DevNormalSmall']))
            story.append(Spacer(1,4))

    story.append(PageBreak())

    # Simple System Architecture inference
    story.append(Paragraph("Suggested System Architecture", styles['DevHeading2']))
    # Heuristic mapping: if there are many components / dynamic content, suggest microservices
    num_components = len(struct.get("components", []))
    num_pages = len(struct.get("pages", []))
    arch_lines = [
        "Based on the UI components and pages, the following architecture is suggested to support this front-end:",
        "- Frontend: Single Page Application (React / Vue) to implement screens and route flows.",
        "- API Gateway: public REST API endpoints for data, auth, and file uploads.",
        "- Auth Service: manage users and sessions (OAuth2 / JWT).",
        "- Content Service: deliver content (text, copy) used in the UI.",
        "- Component Data Service: endpoints supplying component state and dynamic data.",
        "- Storage: object storage for assets and file exports (S3-compatible).",
        "- Worker / PDF generation service: separate worker to render and build PDFs from UI metadata (already implemented).",
        "- Observability: logging, metrics, and error collection",
    ]
    if num_components > 20 or num_pages > 8:
        arch_lines.insert(0, "- Recommendation: use microservices for scalability due to large UI surface.")
    else:
        arch_lines.insert(0, "- Recommendation: monolithic backend with modular services is sufficient for small-medium apps.")
    for l in arch_lines:
        story.append(Paragraph(l, styles['DevNormalSmall']))

    # Add a brief checklist for developers
    story.append(PageBreak())
    story.append(Paragraph("Developer Handoff Checklist", styles['DevHeading2']))
    checklist = [
        ("Screen designs included", "Yes"),
        ("Text copy exported", str(bool(text_nodes))),
        ("Components documented", str(bool(components))),
        ("Prototype flows documented", str(bool(interactions))),
        ("Suggested API services", "Auth, Content, Component Data, File Export")
    ]
    _add_kv_table(story, checklist, styles)

    doc.build(story)
    return pdf_path

# Backward compatibility function for existing code
def generate_pdf_from_data(data: dict, output_dir: str = "generated_pdfs") -> str:
    """
    Backward compatibility wrapper that converts the old format to new structure format
    """
    # Convert old format to new structure format
    if "file_name" not in data:
        # This is the old format, convert it to structure format
        structure = {
            "file_name": data.get("name", "Application"),
            "last_modified": datetime.now().isoformat(),
            "document_hash": "legacy",
            "pages": [{"id": "page1", "name": "Main Page"}],
            "layers": [],
            "text_nodes": [],
            "components": [],
            "styles": {},
            "interactions": []
        }
        
        # Convert pages and frames
        for page in data.get("pages", []):
            for frame in page.get("key_frames", []):
                structure["layers"].append({
                    "id": f"frame_{len(structure['layers'])}",
                    "type": "FRAME",
                    "name": frame.get("name", "Frame"),
                    "page": "Main Page",
                    "width": 375,
                    "height": 812,
                    "children_count": 0,
                    "visible": True
                })
        
        # Convert features to text nodes
        for i, feature in enumerate(data.get("key_features", [])):
            structure["text_nodes"].append({
                "id": f"text_{i}",
                "page": "Main Page",
                "name": f"Feature {i+1}",
                "characters": feature,
                "style": {"fontFamily": "Inter", "fontSize": 16}
            })
        
        return generate_pdf_from_structure(structure, output_dir)
    else:
        # This is already in structure format
        return generate_pdf_from_structure(data, output_dir)