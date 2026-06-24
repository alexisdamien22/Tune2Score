document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const fileInput = document.getElementById('audioFile');
    const tempo = document.getElementById('tempo').value;
    const timeSignature = document.getElementById('timeSignature').value;
    
    const formData = new FormData();
    formData.append('audio', fileInput.files[0]);
    formData.append('tempo', tempo);
    formData.append('time_signature', timeSignature);

    // Reset de l'affichage et état de chargement
    document.getElementById('actionsZone').innerHTML = "";
    document.getElementById('svgContainer').innerHTML = "<div class='loader'>Analyse et tracé en cours...</div>";
    document.getElementById('resultZone').style.display = "block";

    try {
        // Envoi des données à l'API FastAPI
        const response = await fetch('http://127.0.0.1:8000/api/upload', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error("Erreur lors du traitement du fichier par le serveur.");
        }
        
        const data = await response.json();
        
        // Récupération du SVG généré
        const svgResponse = await fetch(data.svg_url);
        const svgCode = await svgResponse.text();
        
        // Ajout dynamique du bouton de téléchargement PDF si l'URL est fournie
        if (data.pdf_url) {
            document.getElementById('actionsZone').innerHTML = `
                <a href="${data.pdf_url}" target="_blank" style="text-decoration: none;">
                    <button type="button" class="btn-pdf">Télécharger en PDF 📄</button>
                </a>
            `;
        }
        
        // Affichage du rendu visuel de la partition
        document.getElementById('svgContainer').innerHTML = svgCode;

    } catch (error) {
        document.getElementById('svgContainer').innerHTML = "<div class='error'>Erreur lors de la génération de la partition.</div>";
        console.error(error);
    }
});