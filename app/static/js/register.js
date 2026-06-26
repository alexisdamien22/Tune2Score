document.getElementById('registerForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const messageZone = document.getElementById('messageZone');

    messageZone.className = "message-zone";
    messageZone.innerText = "Création du compte en cours...";

    try {
        const response = await fetch('http://127.0.0.1:8000/api/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, email, password })
        });
        
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Une erreur est survenue lors de l'inscription.");
        }
        
        messageZone.className = "message-zone success";
        messageZone.innerText = "Compte créé avec succès ! Redirection...";
        
        setTimeout(() => {
            window.location.href = "/";
        }, 2000);

    } catch (error) {
        messageZone.className = "message-zone error";
        messageZone.innerText = error.message;
    }
});