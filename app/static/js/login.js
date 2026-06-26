// app/static/js/login.js

document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const messageZone = document.getElementById('messageZone');

    messageZone.className = "message-zone";
    messageZone.innerText = "Vérification de vos identifiants...";

    try {
        const response = await fetch('http://127.0.0.1:8000/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Une erreur est survenue lors de l'connexion.");
        }
        
        localStorage.setItem("tune2score_user", JSON.stringify({ username: data.user.username }));

        messageZone.className = "message-zone success";
        messageZone.innerText = "Connexion réussie ! Redirection vers l'accueil...";
        
        setTimeout(() => {
            window.location.href = "/";
        }, 1500);

    } catch (error) {
        messageZone.className = "message-zone error";
        messageZone.innerText = error.message;
    }
});