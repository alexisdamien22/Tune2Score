# Tune2Score

Tune2Score est une application web qui transforme vos enregistrements audio (chant, sifflement) en partitions musicales PDF automatiquement.

## 🚀 Fonctionnalités
- **Conversion** : Importez un audio, obtenez une partition.
- **Historique** : Gérez vos partitions (téléchargement, renommage, suppression).
- **Administration** : Gestion complète des utilisateurs (modification des rôles et suppression de comptes).

## 📋 Guide d'utilisation
1. **Compte** : Inscrivez-vous et connectez-vous.
2. **Dashboard** : Uploadez votre fichier pour générer la partition.
3. **Admin** : Si votre compte a le rôle "admin", un lien "⚙️ Administration" apparaîtra dans votre menu déroulant pour gérer les utilisateurs.

## 🛠 Installation pour les développeurs
1. Clonez le projet.
2. Configurez le fichier `.env` avec votre base de données (`DATABASE_URL=sqlite:///./database.db`).
3. Installez les dépendances : `pip install -r requirements.txt`.
4. Lancez le serveur : `uvicorn main:app --reload`.