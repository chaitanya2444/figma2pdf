import os
import json
import re
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv
import httpx

load_dotenv()

from services.pdf_service import generate_pdf_from_data, generate_pdf_from_structure
from services.figma_service import parse_figma_with_llm, parse_figma_file_from_url
from services.dynamic_pdf_generator import generate_dynamic_pdf

app = FastAPI(title="FigmaToPDF-Pro")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],                  # ← Allow everything (temp fix)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FIGMA_TOKEN = os.getenv("FIGMA_TOKEN")

def extract_figma_key(figma_url: str) -> str:
    """
    Works with ALL Figma URLs in 2025:
    - file/...
    - design/...
    - proto/...
    - community/file/...
    - with or without version numbers
    """
    patterns = [
        r"figma\.com/(?:file|design|proto)/([a-zA-Z0-9]+)",
        r"figma\.com/community/file/(\d+)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, figma_url)
        if match:
            key = match.group(1)
            # Remove version suffix if exists (e.g., :v123)
            return key.split(":")[0]
    
    raise ValueError("Invalid Figma URL — could not extract file key")

def get_figma_file(file_key: str, max_retries=3):
    url = f"https://api.figma.com/v1/files/{file_key}"
    headers = {"X-Figma-Token": FIGMA_TOKEN}
    
    for attempt in range(max_retries):
        response = httpx.get(url, headers=headers)
        
        if response.status_code == 200:
            print(f"✅ Figma data fetched successfully!")
            return response.json()
        
        elif response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 60))
            wait_time = retry_after * (2 ** attempt)
            print(f"⚠️ Rate limit hit (429). Waiting {wait_time}s before retry {attempt + 1}/{max_retries}...")
            time.sleep(wait_time)
            continue
        
        else:
            response.raise_for_status()
    
    raise HTTPException(status_code=429, detail="Figma API rate limited after retries. Try again later.")

class GenerateRequest(BaseModel):
    figma_link: str
    report_data: dict = None

class DiagramRequest(BaseModel):
    prompt: str
    diagram_type: str = "architecture"

@app.get("/api/health")
async def health():
    return {"status": "healthy", "service": "FigmaToPDF-Pro"}

@app.post("/api/generate-pdf")
async def generate_pdf(figma_link: str = Form(...), report_file: UploadFile = File(default=None)):
    try:
        # Handle JSON upload
        json_data = None
        if report_file and report_file.filename:
            report_content = await report_file.read()
            json_data = json.loads(report_content)
        
        # Parse Figma link with LLM and merge with JSON
        figma_data = parse_figma_with_llm(figma_link, json_data)
        
        # Generate PDF
        pdf_path = generate_pdf_from_data(figma_data)
        
        return {
            "success": True,
            "pdf_url": f"/api/download/{os.path.basename(pdf_path)}",
            "pdf_filename": os.path.basename(pdf_path)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate")
async def generate_pdf_simple(request: Request):
    data = await request.json()
    figma_url = data.get("figma_url", "").strip()
    
    # Extract file_key using universal parser
    try:
        file_key = extract_figma_key(figma_url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    try:
        # Use LLM parsing (more reliable than API due to rate limits)
        print("DEBUG: Using LLM to parse Figma design")
        from services.figma_service import parse_figma_with_llm
        processed_data = parse_figma_with_llm(figma_url)
        
        pdf_path = generate_pdf_from_data(processed_data)
        
        project_name = processed_data.get('project_name', processed_data.get('name', 'Untitled'))
        return FileResponse(pdf_path, media_type="application/pdf", 
                          filename=f"{project_name.replace(' ', '_')}.pdf")
        
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 403:
            raise HTTPException(status_code=403, detail="Private file - check your FIGMA_TOKEN in .env")
        raise HTTPException(status_code=500, detail=f"Figma API error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-diagram")
async def generate_diagram_only(req: DiagramRequest):
    """Generate standalone architecture diagram (Eraser.io style)"""
    try:
        from services.ai_diagram_generator import create_architecture_diagram
        
        # Create diagram from prompt
        diagram_b64 = create_architecture_diagram(req.prompt)
        
        return {
            "success": True,
            "image_b64": f"data:image/png;base64,{diagram_b64}",
            "prompt": req.prompt
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate_pdf_from_figma")
async def generate_pdf_from_figma(figma_url: str = Form(...)):
    """Generate developer documentation PDF from Figma API data"""
    try:
        struct = parse_figma_file_from_url(figma_url)
        pdf_path = generate_pdf_from_structure(struct)
        filename = os.path.basename(pdf_path)
        return {"status": "ok", "pdf": f"/api/download/{filename}", "filename": filename}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/generate_dynamic_pdf")
async def generate_dynamic_pdf_endpoint(figma_url: str = Form(...)):
    """✅ Generate truly dynamic PDF that fetches Figma data every time"""
    try:
        pdf_path = generate_dynamic_pdf(figma_url)
        filename = os.path.basename(pdf_path)
        return {"status": "success", "pdf": f"/api/download/{filename}", "filename": filename}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/download/{filename}")
async def download_pdf(filename: str):
    file_path = os.path.join("generated_pdfs", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="PDF not found")
    return FileResponse(file_path, media_type="application/pdf", filename=filename)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)