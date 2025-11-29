// frontend/script.js
const form = document.getElementById('generateForm');
const status = document.getElementById('status');

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const figmaLink = document.getElementById('figmaLink').value.trim();
    const jsonFile = document.getElementById('jsonUpload').files[0];
    
    if (!figmaLink) {
        status.innerHTML = '<span style="color:red">Please enter a Figma link</span>';
        return;
    }

    status.innerHTML = 'Generating PDF, please wait 10–25 seconds...';

    const formData = new FormData();
    formData.append('figma_link', figmaLink);
    if (jsonFile) formData.append('report_file', jsonFile);

    try {
        const res = await fetch('http://localhost:8001/api/generate-pdf', {
            method: 'POST',
            body: formData
        });

        const data = await res.json();

        if (data.success) {
            const fullUrl = `http://localhost:8001${data.pdf_url}`;
            status.innerHTML = `
                <span style="color:lime;font-weight:bold">PDF ready!</span><br>
                <a href="${fullUrl}" download="${data.pdf_filename}" 
                   style="color:#00ff00; font-size:18px; text-decoration:underline">
                   Click here if download doesn't start
                </a>
            `;
            // Auto download
            const link = document.createElement('a');
            link.href = fullUrl;
            link.download = data.pdf_filename;
            link.click();
        } else {
            status.innerHTML = `<span style="color:red">Error: ${data.detail || data.message}</span>`;
        }
    } catch (err) {
        status.innerHTML = `<span style="color:red">Network error: ${err.message}</span>`;
    }
});