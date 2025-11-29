# backend/services/diagram_service.py
import os
import time
import gc
import base64
from pathlib import Path
from urllib.parse import quote
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from PIL import Image

# Keep temp directory outside OneDrive
TEMP_DIR = Path("C:/temp/figma2pdf")
TEMP_DIR.mkdir(parents=True, exist_ok=True)

def generate_architecture_diagram(data: dict) -> str:
    html_path = TEMP_DIR / "temp_mermaid.html"
    full_screenshot = TEMP_DIR / "temp_full.png"
    final_png = TEMP_DIR / "temp_diagram.png"

    # Build Mermaid
    mermaid_lines = ["graph TD"]
    node_id = 0
    for page in data.get("pages", []):
        page_id = f"P{node_id}"
        mermaid_lines.append(f'    {page_id}["{page["name"]}"]')
        node_id += 1
        for frame in page.get("key_frames", []):
            frame_id = f"F{node_id}"
            mermaid_lines.append(f'    {frame_id}["{frame["name"]}"]')
            mermaid_lines.append(f"    {page_id} --> {frame_id}")
            node_id += 1

    mermaid_code = "\n".join(mermaid_lines)

    html_content = f"""<!DOCTYPE html>
<html><head>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script>
  mermaid.initialize({{startOnLoad:true, theme:'forest', flowchart:{{useMaxWidth:true}}}});
</script>
</head>
<body style="margin:0;padding:40px;background:white">
<div class="mermaid">{mermaid_code}</div>
</body></html>"""

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    html_url = f"file:///{str(html_path).replace(os.sep, '/')}"

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1600,1200")
    options.add_argument("--force-device-scale-factor=2")  # Better quality

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(html_url)
    time.sleep(6)  # Let Mermaid render fully

    driver.save_screenshot(str(full_screenshot))
    driver.quit()

    # Crop only the actual diagram using PIL and ensure file is properly closed
    with Image.open(full_screenshot) as img:
        # Auto-crop white borders
        cropped = img.crop(img.getbbox())
        cropped.save(final_png, "PNG")
    
    # CRITICAL: Force garbage collection to release all file handles
    gc.collect()
    time.sleep(0.3)  # Small delay to ensure file is fully released

    # Clean up temp files
    for f in [html_path, full_screenshot]:
        if os.path.exists(f):
            try:
                os.remove(f)
            except:
                pass  # Ignore cleanup errors

    return str(final_png)

def get_diagram_as_base64(data: dict) -> str:
    """Alternative method using base64 encoding to avoid file locking completely"""
    final_png = generate_architecture_diagram(data)
    
    try:
        with open(final_png, "rb") as f:
            b64_data = base64.b64encode(f.read()).decode()
        
        # Clean up immediately after reading
        try:
            os.remove(final_png)
        except:
            pass
            
        return f"data:image/png;base64,{b64_data}"
    except Exception as e:
        print(f"Base64 encoding failed: {e}")
        return ""