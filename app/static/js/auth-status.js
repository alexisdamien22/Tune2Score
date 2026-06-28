// app/static/js/auth-status.js

function checkAuthStatus() {
    const navLoginBtn = document.getElementById("navLoginBtn");
    const navUserDropdown = document.getElementById("navUserDropdown");
    const navUsername = document.getElementById("navUsername");
    const dropdownToggle = document.getElementById("dropdownToggle");
    const dropdownMenu = document.getElementById("dropdownMenu");
    const logoutBtn = document.getElementById("logoutBtn");

    const allowedContent = document.getElementById("allowedContent");
    const blockedContent = document.getElementById("blockedContent");

    const userJson = localStorage.getItem("tune2score_user");
    
    if (userJson) {
        try {
            const user = JSON.parse(userJson);
            if (user && user.username) {
                if (navLoginBtn) navLoginBtn.style.display = "none";
                if (navUserDropdown) navUserDropdown.style.display = "inline-block";
                if (navUsername) navUsername.innerText = user.username;

                const navAdminLink = document.getElementById("navAdminLink");
                if (navAdminLink && user.role === "admin") {
                    navAdminLink.style.display = "block";
                }

                if (allowedContent) allowedContent.style.setProperty("display", "block", "important");
                if (blockedContent) blockedContent.style.setProperty("display", "none", "important");
            }
        } catch (e) {
            console.error("Erreur de décodage de la session", e);
        }
    } else {
        if (navLoginBtn) navLoginBtn.style.display = "inline-block";
        if (navUserDropdown) navUserDropdown.style.display = "none";

        if (allowedContent) allowedContent.style.setProperty("display", "none", "important");
        if (blockedContent) blockedContent.style.setProperty("display", "block", "important");
    }

    if (dropdownToggle && dropdownMenu) {
        const newToggle = dropdownToggle.cloneNode(true);
        dropdownToggle.parentNode.replaceChild(newToggle, dropdownToggle);

        newToggle.addEventListener("click", (e) => {
            e.stopPropagation();
            dropdownMenu.classList.toggle("show");
        });
    }

    if (logoutBtn) {
        logoutBtn.addEventListener("click", () => {
            localStorage.removeItem("tune2score_user");
            window.location.href = "/";
        });
    }
}

document.addEventListener("DOMContentLoaded", checkAuthStatus);

document.addEventListener("click", () => {
    const dropdownMenu = document.getElementById("dropdownMenu");
    if (dropdownMenu && dropdownMenu.classList.contains("show")) {
        dropdownMenu.classList.remove("show");
    }
});