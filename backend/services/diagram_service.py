# backend/services/diagram_service.py
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from PIL import Image

def generate_architecture_diagram(data: dict) -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(base_dir, "temp_diagram.html")
    screenshot_path = os.path.join(base_dir, "temp_screenshot.png")
    final_diagram_path = os.path.join(base_dir, "architecture_diagram.png")

    # Build Mermaid from real frames
    lines = ["graph TD"]
    for page in data.get("pages", []):
        page_id = page["name"].replace(" ", "_")
        lines.append(f'    {page_id}["{page["name"]}"]')
        for frame in page.get("frames", []):
            fid = frame["name"].replace(" ", "_")
            lines.append(f'    {fid}["{frame["name"]}"]')
            lines.append(f"    {page_id} --> {fid}")

    mermaid_code = "\n".join(lines)
    
    html = f"""<!DOCTYPE html>
<html><head>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script>mermaid.initialize({{startOnLoad:true, theme:'forest'}});</script>
</head><body style="margin:0;padding:60px;background:white">
<div class="mermaid">
{mermaid_code}
</div>
</body></html>"""

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    # Chrome in headless mode
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1600,1200")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("file:///" + os.path.abspath(html_path).replace("\\", "/"))
    time.sleep(5)
    driver.save_screenshot(screenshot_path)
    driver.quit()

    # Save the final diagram to disk
    cropped = Image.open(screenshot_path)
    cropped = cropped.crop(cropped.getbbox())
    
    # Save the diagram to disk using full path
    cropped.save(final_diagram_path, "PNG")

    # Clean up temp files
    try:
        os.remove(html_path)
        os.remove(screenshot_path)
    except:
        pass

    # Return the full path for ReportLab
    return final_diagram_path