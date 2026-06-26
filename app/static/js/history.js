// app/static/js/history.js

document.addEventListener("DOMContentLoaded", async () => {
    const historyList = document.getElementById("historyList");
    
    const userJson = localStorage.getItem("tune2score_user");
    if (!userJson) {
        historyList.innerHTML = `
            <div class="error-box">
                <p>Vous devez être connecté pour voir votre historique.</p>
                <a href="/login" class="btn-login-nav" style="display:inline-block; margin-top:10px;">Se connecter</a>
            </div>
        `;
        return;
    }

    const user = JSON.parse(userJson);

    try {
        const response = await fetch(`http://127.0.0.1:8000/api/history/${user.username}`);
        const data = await response.json();

        if (!response.ok) throw new Error(data.detail || "Impossible de charger l'historique.");

        if (data.history.length === 0) {
            historyList.innerHTML = "<p class='empty-text'>Vous n'avez pas encore généré de partitions. Importez un fichier audio sur l'accueil !</p>";
            return;
        }

        let htmlContent = `<table class="history-table">
            <thead>
                <tr>
                    <th>Fichier Audio</th>
                    <th>Tempo</th>
                    <th>Mesure</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>`;

        data.history.forEach(item => {
            htmlContent += `
                <tr>
                    <td><strong>${item.file_name}</strong></td>
                    <td>${item.tempo} BPM</td>
                    <td>${item.time_signature}</td>
                    <td>
                        <a href="${item.pdf_url}" target="_blank" class="btn-download">Télécharger PDF</a>
                    </td>
                </tr>
            `;
        });

        htmlContent += `</tbody></table>`;
        historyList.innerHTML = htmlContent;

    } catch (error) {
        historyList.innerHTML = `<p class="error-text">Erreur : ${error.message}</p>`;
    }
});