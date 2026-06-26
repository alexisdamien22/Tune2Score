// app/static/js/upload.js

document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const fileInput = document.getElementById('audioFile');
    const tempo = document.getElementById('tempo').value;
    const timeSignature = document.getElementById('timeSignature').value;
    
    const noteSelect = document.getElementById('noteSelect');
    const modeSelect = document.getElementById('modeSelect');
    
    const loadingZone = document.getElementById('loadingZone');
    const resultZone = document.getElementById('resultZone');
    const svgContainer = document.getElementById('svgContainer');
    const downloadPdfBtn = document.getElementById('downloadPdfBtn');
    const submitBtn = document.getElementById('submitBtn');

    if (!fileInput.files || fileInput.files.length === 0) return;

    const formData = new FormData();
    formData.append('audio', fileInput.files[0]);
    formData.append('tempo', tempo);
    formData.append('time_signature', timeSignature);
    
    if (noteSelect) formData.append('tonic', noteSelect.value);
    if (modeSelect) formData.append('mode', modeSelect.value);

    const userJson = localStorage.getItem("tune2score_user");
    if (userJson) {
        const user = JSON.parse(userJson);
        formData.append('username', user.username);
    } else {
        formData.append('username', 'alexis_test');
    }

    if (submitBtn) submitBtn.disabled = true;
    if (loadingZone) loadingZone.style.display = "block";
    if (resultZone) resultZone.style.display = "none";

    try {
        const response = await fetch('http://127.0.0.1:8000/api/upload', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || "Erreur lors du traitement du fichier par le serveur.");
        }
        
        const data = await response.json();
        
        const svgResponse = await fetch(data.svg_url);
        const svgCode = await svgResponse.text();
        
        if (svgContainer) {
            svgContainer.innerHTML = svgCode;
        }
        
        if (downloadPdfBtn && data.pdf_url) {
            downloadPdfBtn.href = data.pdf_url;
            downloadPdfBtn.style.display = "inline-block";
        }
        
        if (resultZone) resultZone.style.display = "block";

    } catch (error) {
        alert("Une erreur est survenue : " + error.message);
        if (svgContainer) {
            svgContainer.innerHTML = `<div class="error-text" style="color: red; text-align: center; margin-top: 20px;">
                Erreur lors de la génération de la partition.
            </div>`;
        }
        console.error(error);
    } finally {
        if (loadingZone) loadingZone.style.display = "none";
        if (submitBtn) submitBtn.disabled = false;
    }
});