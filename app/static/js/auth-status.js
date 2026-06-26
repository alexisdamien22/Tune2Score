// app/static/js/auth-status.js

document.addEventListener("DOMContentLoaded", () => {
    const navLoginBtn = document.getElementById("navLoginBtn");
    const navUserDropdown = document.getElementById("navUserDropdown");
    const navUsername = document.getElementById("navUsername");
    const dropdownToggle = document.getElementById("dropdownToggle");
    const dropdownMenu = document.getElementById("dropdownMenu");
    const logoutBtn = document.getElementById("logoutBtn");

    const userJson = localStorage.getItem("tune2score_user");
    
    if (userJson) {
        try {
            const user = JSON.parse(userJson);
            if (user && user.username) {
                if (navLoginBtn) navLoginBtn.style.display = "none";
                if (navUserDropdown) navUserDropdown.style.display = "inline-block";
                if (navUsername) navUsername.innerText = user.username;
            }
        } catch (e) {
            console.error("Erreur de lecture de la session utilisateur", e);
        }
    } else {
        if (navLoginBtn) navLoginBtn.style.display = "inline-block";
        if (navUserDropdown) navUserDropdown.style.display = "none";
    }

    if (dropdownToggle && dropdownMenu) {
        dropdownToggle.addEventListener("click", (e) => {
            e.stopPropagation();
            dropdownMenu.classList.toggle("show");
        });
    }

    document.addEventListener("click", () => {
        if (dropdownMenu && dropdownMenu.classList.contains("show")) {
            dropdownMenu.classList.remove("show");
        }
    });

    if (logoutBtn) {
        logoutBtn.addEventListener("click", () => {
            localStorage.removeItem("tune2score_user");
            window.location.href = "/";
        });
    }
});