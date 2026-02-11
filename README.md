# MediGest - Système de Gestion de Cabinet Médical 🏥

**MediGest** est une solution logicielle complète et robuste dédiée à la gestion administrative et médicale des cabinets de santé. Conçue pour optimiser le flux de travail des secrétaires, médecins et administrateurs, elle centralise la gestion des patients, la planification des rendez-vous et le suivi de l'activité du cabinet.

Ce projet repose sur une architecture moderne alliant la puissance de **Python**, la flexibilité de **MongoDB** (NoSQL) et l'interactivité de **Streamlit** pour l'interface utilisateur.

---

## 📑 Table des Matières

1.  [Architecture du Projet](#-architecture-du-projet)
2.  [Fonctionnalités Détaillées](#-fonctionnalités-détaillées)
3.  [Modèles de Données (Schémas NoSQL)](#-modèles-de-données-schémas-nosql)
4.  [Règles Métier & Logique Interne](#-règles-métier--logique-interne)
5.  [Installation & Configuration](#-installation--configuration)
6.  [Guide d'Utilisation](#-guide-dutilisation)
7.  [Stack Technique](#-stack-technique)

---

## 🏗 Architecture du Projet

Le projet suit le modèle **MVC (Modèle-Vue-Contrôleur)** adapté pour Streamlit :

*   **Couche de Données (Model)** : Gérée par `db_manager.py`. Ce module encapsule toutes les interactions avec la base de données MongoDB via `pymongo`. Il agit comme une API interne, assurant que l'interface utilisateur ne manipule jamais directement la base de données. Il inclut désormais des méthodes pour la mise à jour des enregistrements (`update_patient`, `update_practitioner`).
*   **Couche Interface (View/Controller)** : Gérée par `app.py`. Utilise Streamlit pour le rendu des composants (formulaires, tableaux, graphiques) et la gestion de l'état de session (`st.session_state`).
*   **Base de Données** : MongoDB (instance locale ou distante). Le choix du NoSQL permet une évolution flexible du schéma des données patients (ajout de champs médicaux sans migration lourde).

### Structure des Fichiers

```bash
projet_nosql/
├── app.py              # 🖥️ Point d'entrée de l'application (Interface Streamlit)
├── db_manager.py       # ⚙️ Moteur de base de données (CRUD, Logique métier, Sécurité)
├── requirements.txt    # 📦 Liste des dépendances Python
├── run_medigest.sh     # 🚀 Script Shell d'exécution automatique
└── README.md           # 📘 Documentation du projet
```

---

## 🚀 Fonctionnalités Détaillées

### 1. Authentification & Sécurité (RBAC)
Le système intègre un contrôle d'accès basé sur les rôles (RBAC) :
*   **Secrétariat (Accueil)** : Prise de RDV, gestion patients (création, lecture, **mise à jour**), planning journalier.
*   **Responsable** : Accès aux KPIs, statistiques de performance, charge de travail.
*   **Administrateur** : Gestion complète (utilisateurs, praticiens, audit logs).
*   **Sécurité** : Les mots de passe sont hachés via **SHA-256** avant stockage. Aucune donnée sensible n'est stockée en clair.

### 2. Gestion Avancée des Rendez-vous
*   **Planification Intelligente** : Sélection du praticien, date, heure et durée.
*   **Détection de Conflits** : Algorithme vérifiant automatiquement les chevauchements de créneaux pour un même médecin avant validation.
*   **Cycle de Vie** : Statuts `Confirmé`, `Annulé`, `Absent`, `Annulé (Médecin Absent)`.
*   **Gestion des Aléas** :
    *   Signalement de retard (décale automatiquement le planning).
    *   Annulation d'urgence par le médecin.

### 3. Dossier Patient Numérique
*   **Identité** : Nom (automatiquement mis en majuscules), Prénom, Contact, Assurance.
*   **Historique Médical** : Chaque rendez-vous est automatiquement archivé dans l'historique du patient (Date, Médecin, Motif).
*   **Recherche Hybride** : Moteur de recherche acceptant soit le **Nom/Prénom** (Recherche floue insensible à la casse), soit l'**ID unique** (ObjectId MongoDB).
*   **Édition** : Modification possible des informations personnelles et médicales (Nom, Prénom, Tél, Email, Assurance, Notes) directement depuis la fiche patient.

### 4. Administration & Audit
*   **Gestion Praticiens** : Création, suppression et **modification** (Nom, Spécialité) des praticiens.
*   **Traçabilité (Logs)** : Chaque action critique (création, suppression, modification, login) est enregistrée dans une collection `logs` avec l'auteur, l'action, les détails et le timestamp.
*   **Gestion Dynamique** : Ajout/Suppression de médecins et d'utilisateurs sans redémarrage du serveur.

---

## 💾 Modèles de Données (Schémas NoSQL)

Voici la structure JSON des documents stockés dans MongoDB :

### Collection `users`
```json
{
  "_id": ObjectId("..."),
  "username": "admin",
  "password": "hashed_sha256_string",
  "role": "Administrateur",
  "created_at": ISODate("2023-10-27T10:00:00Z")
}
```

### Collection `patients`
```json
{
  "_id": ObjectId("..."),
  "nom": "DUPONT",
  "prenom": "Jean",
  "telephone": "0601020304",
  "email": "jean.dupont@email.com",
  "assurance": "1890675123456",
  "notes_medicales": "Allergie à la pénicilline.",
  "historique_visites": [
    {
      "date": ISODate("..."),
      "practitioner": "Dr. House",
      "motif": "Migraine"
    }
  ],
  "created_at": ISODate("...")
}
```

### Collection `appointments`
```json
{
  "_id": ObjectId("..."),
  "patient_id": ObjectId("..."),  // Référence vers patients
  "practitioner_name": "Dr. House",
  "date_heure_debut": ISODate("2023-10-27T14:00:00Z"),
  "date_heure_fin": ISODate("2023-10-27T14:30:00Z"),
  "duree_minutes": 30,
  "motif": "Consultation suivi",
  "statut": "Confirmé",
  "created_at": ISODate("...")
}
```

### Collection `logs`
```json
{
  "_id": ObjectId("..."),
  "user": "secr",
  "action": "CREATE_APPT",
  "details": "RDV créé pour patient 654... avec Dr. House",
  "timestamp": ISODate("...")
}
```

---

## 🧠 Règles Métier & Logique Interne

### 1. Algorithme de Chevauchement
Lors de la création ou modification d'un RDV, le système vérifie la disponibilité via la logique suivante :
Un conflit existe si : `(Start_New < End_Existing) ET (End_New > Start_Existing)`
*Condition supplémentaire* : Le RDV existant ne doit pas avoir le statut "Annulé".

### 2. Règle des 30 Minutes (Verrouillage)
Pour éviter la désorganisation du cabinet, la modification ou le déplacement d'un rendez-vous est **bloqué** si le rendez-vous a lieu dans **moins de 30 minutes** (ou s'il est déjà passé).
*Implémentation* : `if (appt_start_time - now).total_seconds() < 1800: raise Error`

### 3. Redirection Inter-Vues
L'interface utilise un système de navigation personnalisé. Par exemple, depuis la recherche patient, cliquer sur "Prendre RDV" redirige automatiquement vers l'onglet de création de RDV en pré-sélectionnant le patient trouvé, améliorant l'UX.

---

## ⚙️ Installation & Configuration

### Prérequis
*   **Python 3.8+** installé.
*   **MongoDB Community Server** installé et en cours d'exécution (port par défaut `27017`).

### Installation Rapide

1.  **Cloner le dépôt** :
    ```bash
    git clone <url-du-repo>
    cd projet_nosql
    ```

2.  **Lancer le script d'installation et de démarrage** :
    Le script `run_medigest.sh` s'occupe de tout (création du venv, installation des dépendances, lancement).
    ```bash
    chmod +x run_medigest.sh
    ./run_medigest.sh
    ```

### Installation Manuelle

1.  **Créer un environnement virtuel** :
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

2.  **Installer les dépendances** :
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configuration Environnement** :
    Par défaut, l'application cherche MongoDB sur `localhost:27017`. Pour changer cela, définissez la variable d'environnement :
    ```bash
    export MONGO_URI="mongodb://user:pass@remote-host:27017/"
    ```

4.  **Lancer l'application** :
    ```bash
    streamlit run app.py
    ```

---

## 📖 Guide d'Utilisation

### Premier Démarrage
À la première exécution, le système détecte l'absence d'utilisateurs et crée un compte administrateur par défaut :
*   **Login** : `admin`
*   **Password** : `admin123`

### Scénarios Courants

#### 👩‍💼 Secrétaire : Gestion Patients & RDV
1.  Connectez-vous avec un compte rôle "Accueil".
2.  Allez dans l'onglet **"Gestion Patients"**.
3.  Recherchez le patient.
    *   **Modification** : Dépliez la section "Modifier les informations" dans la fiche patient pour mettre à jour ses données.
    *   **Nouveau Patient** : S'il n'existe pas, créez-le via le formulaire en bas de page.
4.  Cliquez sur **"📅 Prendre RDV"** dans la fiche du patient ou allez dans l'onglet **"Nouveau Rendez-vous"**.
5.  Sélectionnez le médecin, la date, l'heure et le motif.
6.  Validez. Le système confirmera si le créneau est libre.

#### 👨‍⚕️ Médecin/Secrétaire : Gérer un Retard
1.  Allez dans l'onglet **"Liste Globale"**.
2.  Dépliez la section de votre nom.
3.  Repérez le prochain RDV.
4.  Cliquez sur le bouton **"🕒 Signaler Retard"**, entrez la durée (ex: 15 min) et validez.
5.  Le RDV est décalé et le statut mis à jour.

#### 🛠️ Administrateur : Gestion Praticiens
1.  Connectez-vous en tant qu'"Administrateur".
2.  Allez dans l'onglet **"Administration"** -> **"Gestion Praticiens"**.
3.  Utilisez le bouton **"📝 Editer"** (popover) à côté d'un praticien pour modifier son nom ou sa spécialité.
4.  Utilisez le formulaire en bas pour ajouter un nouveau praticien.

#### 📊 Responsable : Analyser l'activité
1.  Connectez-vous en tant que "Responsable".
2.  Consultez les graphiques pour voir la répartition de la charge de travail entre les médecins et surveiller le taux d'annulation.

---

## 🛠 Stack Technique

| Technologie | Usage | Justification |
| :--- | :--- | :--- |
| **Python 3** | Langage Principal | Robustesse, écosystème riche. |
| **Streamlit** | Frontend UI | Développement rapide d'interfaces Data/Web interactives sans HTML/CSS/JS. |
| **MongoDB** | Base de Données | Modèle flexible (Schemaless) idéal pour les dossiers patients évolutifs. |
| **Pymongo** | Driver DB | Communication native et performante avec MongoDB. |
| **Pandas** | Manipulation Data | Traitement des données pour les tableaux et statistiques. |
| **Plotly** | Dataviz | Génération de graphiques interactifs pour le dashboard. |
