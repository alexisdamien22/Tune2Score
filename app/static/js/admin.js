// app/static/js/admin.js

document.addEventListener("DOMContentLoaded", loadUsers);

function createEl(tag, options = {}) {
    const el = document.createElement(tag);
    if (options.text) el.textContent = options.text;
    if (options.id) el.id = options.id;
    if (options.className) el.className = options.className;
    
    if (options.styles) {
        Object.assign(el.style, options.styles);
    }
    return el;
}

async function loadUsers() {
    const adminList = document.getElementById("adminList");
    const userJson = localStorage.getItem("tune2score_user");
    
    if (!userJson) {
        window.location.href = "/";
        return;
    }

    const currentUser = JSON.parse(userJson);
    if (currentUser.role !== "admin") {
        alert("Accès refusé. Vous n'êtes pas administrateur.");
        window.location.href = "/";
        return;
    }

    try {
        const response = await fetch("http://127.0.0.1:8000/api/admin/users", {
            headers: { "x-user-name": currentUser.username }
        });
        const data = await response.json();

        if (!response.ok) throw new Error(data.detail || "Erreur de chargement.");

        adminList.textContent = "";

        const table = createEl("table", { className: "history-table" });
        const thead = createEl("thead");
        const headerRow = createEl("tr");

        const headers = ["ID", "Nom d'utilisateur", "Email", "Rôle", "Actions"];
        headers.forEach(headerText => {
            headerRow.appendChild(createEl("th", { text: headerText }));
        });

        thead.appendChild(headerRow);
        table.appendChild(thead);

        const tbody = createEl("tbody");

        data.users.forEach(user => {
            const tr = createEl("tr", { id: `user-row-${user.id}` });

            tr.appendChild(createEl("td", { text: user.id }));

            const tdUser = createEl("td");
            tdUser.appendChild(createEl("strong", { text: user.username }));
            tr.appendChild(tdUser);

            tr.appendChild(createEl("td", { 
                text: user.email, 
                id: `email-${user.id}` 
            }));

            const tdRole = createEl("td", { id: `role-${user.id}` });
            const spanRole = createEl("span", { 
                text: user.role,
                className: user.role === 'admin' ? 'role-admin' : 'role-user'
            });
            tdRole.appendChild(spanRole);
            tr.appendChild(tdRole);

            const tdActions = createEl("td");

            const btnEdit = createEl("button", {
                text: "Modifier",
                className: "btn-secondary btn-action-small btn-edit"
            });
            btnEdit.addEventListener("click", () => editUser(user.id, user.email, user.role));

            const btnDelete = createEl("button", {
                text: "Supprimer",
                className: "btn-action-small btn-delete"
            });
            btnDelete.addEventListener("click", () => deleteUser(user.id));

            tdActions.appendChild(btnEdit);
            tdActions.appendChild(btnDelete);
            tr.appendChild(tdActions);

            tbody.appendChild(tr);
        });

        table.appendChild(tbody);
        adminList.appendChild(table);

    } catch (error) {
        adminList.textContent = "";
        
        const errText = createEl("p", { 
            text: `Erreur : ${error.message}`,
            className: "admin-error-text"
        });
        adminList.appendChild(errText);
    }
}

async function editUser(userId, currentEmail, currentRole) {
    const newEmail = prompt("Modifier l'adresse email :", currentEmail);
    if (newEmail === null) return; 

    const newRole = prompt("Modifier le rôle ('admin' ou 'user') :", currentRole);
    if (newRole === null) return;

    if (newRole !== "admin" && newRole !== "user") {
        alert("Le rôle doit être strictement 'admin' ou 'user'.");
        return;
    }

    const currentUser = JSON.parse(localStorage.getItem("tune2score_user"));

    try {
        const response = await fetch(`http://127.0.0.1:8000/api/admin/users/${userId}`, {
            method: 'PUT',
            headers: { 
                'Content-Type': 'application/json',
                'x-user-name': currentUser.username
            },
            body: JSON.stringify({ email: newEmail.trim(), role: newRole.trim() })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert("Utilisateur mis à jour avec succès !");
            loadUsers();
        } else {
            alert("Erreur : " + data.detail);
        }
    } catch (err) {
        console.error(err);
    }
}

async function deleteUser(userId) {
    const currentUser = JSON.parse(localStorage.getItem("tune2score_user"));
    
    if (confirm("Êtes-vous sûr de vouloir supprimer ce compte ET toutes ses partitions définitivement ?")) {
        try {
            const response = await fetch(`http://127.0.0.1:8000/api/admin/users/${userId}`, {
                method: 'DELETE',
                headers: { 'x-user-name': currentUser.username }
            });
            
            const data = await response.json();

            if (response.ok) {
                const rowToDelete = document.getElementById(`user-row-${userId}`);
                if (rowToDelete) rowToDelete.remove();
                alert("Utilisateur supprimé !");
            } else {
                alert("Erreur : " + data.detail);
            }
        } catch (err) {
            console.error(err);
        }
    }
}