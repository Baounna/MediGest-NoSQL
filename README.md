# MediGest - Gestion de Cabinet Médical 🏥

MediGest est une application web complète de gestion de cabinet médical développée en **Python** avec **Streamlit** et **MongoDB**. Elle permet de gérer efficacement les rendez-vous, les dossiers patients, le planning des praticiens et l'administration du cabinet.

## 🚀 Fonctionnalités Principales

### 🔐 Authentification & Rôles
Système de connexion sécurisé avec gestion des rôles utilisateurs :
*   **Accueil / Secrétariat** : Gestion quotidienne (RDV, Patients).
*   **Responsable** : Accès aux statistiques et tableaux de bord.
*   **Administrateur** : Gestion complète du système (Utilisateurs, Praticiens, Logs).

### 📅 Gestion des Rendez-vous
*   **Prise de rendez-vous** : Vérification automatique des disponibilités et des chevauchements.
*   **Agenda** : Vue journalière des rendez-vous avec statuts (Confirmé, Annulé, Absent).
*   **Actions Rapides** : Annulation, déclaration d'absence, ou suppression de RDV.
*   **Modification** : Décalage de rendez-vous avec règle métier (blocage des modifications à moins de 30 min).
*   **Gestion des Aléas** : Signalement de retard ou d'absence médecin.

### 👤 Gestion des Patients
*   **Dossiers Complets** : Informations personnelles, assurance, notes médicales.
*   **Historique** : Suivi automatique de l'historique des visites.
*   **Recherche Avancée** : Recherche par nom, prénom ou identifiant unique.

### 👨‍⚕️ Gestion des Praticiens & Planning
*   **Multi-Praticiens** : Gestion de plusieurs médecins avec spécialités différentes.
*   **Vues Filtrées** : Planning individuel pour chaque praticien.

### 📊 Tableau de Bord & Statistiques
*   **KPIs** : Taux d'annulation, charge de travail.
*   **Visualisation** : Graphiques interactifs (via Plotly) pour l'analyse de l'activité.

### 🛠️ Administration
*   **Gestion Utilisateurs** : Création de comptes et attribution de rôles.
*   **Logs Système** : Traçabilité complète des actions (Audit Log).

## 🛠️ Stack Technique

*   **Frontend** : [Streamlit](https://streamlit.io/)
*   **Backend / Base de données** : [MongoDB](https://www.mongodb.com/)
*   **Driver Python** : `pymongo`
*   **Manipulation de données** : `pandas`
*   **Visualisation** : `plotly`

## ⚙️ Prérequis

*   Python 3.8+
*   Serveur MongoDB (local ou distant)

## 📦 Installation

1.  **Cloner le projet** (ou extraire l'archive).
2.  **Configurer l'environnement virtuel** :
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # Sur Linux/Mac
    # venv\Scripts\activate   # Sur Windows
    ```
3.  **Installer les dépendances** :
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configuration MongoDB** :
    *   Assurez-vous que MongoDB tourne sur le port par défaut `27017`.
    *   Si nécessaire, modifiez l'URI de connexion dans `db_manager.py` ou définissez la variable d'environnement `MONGO_URI`.

## ▶️ Démarrage

Pour lancer l'application, utilisez le script fourni ou la commande streamlit :

```bash
./run_medigest.sh
# Ou manuellement :
# source venv/bin/activate
# streamlit run app.py
```

### 🔑 Identifiants par défaut
Lors du premier lancement, un compte administrateur est créé automatiquement :
*   **Utilisateur** : `admin`
*   **Mot de passe** : `admin123`

## 📂 Structure du Projet

```
projet_nosql/
├── app.py              # Point d'entrée de l'application Streamlit (Interface UI)
├── db_manager.py       # Gestionnaire de base de données (Logique métier & MongoDB)
├── requirements.txt    # Liste des dépendances Python
├── run_medigest.sh     # Script de lancement rapide
└── venv/               # Environnement virtuel Python
```

## 🔮 Fonctionnalités Futures
*   Heatmap des heures de pointe pour l'analyse temporelle.
*   Système de notifications (email/SMS) pour les patients.
