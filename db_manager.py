import os
import datetime
import hashlib
import pandas as pd
from pymongo import MongoClient, ASCENDING, DESCENDING
from bson.objectid import ObjectId
import streamlit as st

# Configuration de la connexion MongoDB
# Par défaut localhost, mais configurable via variable d'environnement
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "medigest_db"

class DBManager:
    def __init__(self):
        try:
            self.client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            self.db = self.client[DB_NAME]
            # Vérification de la connexion
            self.client.server_info()
            self._init_db()
        except Exception as e:
            st.error(f"Erreur de connexion à MongoDB : {e}")
            self.db = None

    def _init_db(self):
        """Initialise les index et crée un administrateur par défaut si aucun utilisateur n'existe."""
        if self.db is None: return

        # Création des index pour la performance
        self.db.patients.create_index([("nom", ASCENDING), ("prenom", ASCENDING)])
        self.db.appointments.create_index([("date_heure_debut", ASCENDING)])
        self.db.appointments.create_index([("practitioner_name", ASCENDING), ("date_heure_debut", ASCENDING)])
        self.db.logs.create_index([("timestamp", DESCENDING)])
        try:
            self.db.users.create_index("username", unique=True)
        except Exception:
            pass  # Index may already exist or duplicates prevent creation
        
        # Création d'un admin par défaut si la collection users est vide
        if self.db.users.count_documents({}) == 0:
            self.create_user("admin", "admin123", "Administrateur", "admin")

    # --- Authentification & Utilisateurs ---

    def hash_password(self, password):
        """Hachage simple SHA-256 pour les mots de passe."""
        return hashlib.sha256(password.encode()).hexdigest()

    def check_user(self, username, password):
        """Vérifie les identifiants de l'utilisateur."""
        user = self.db.users.find_one({"username": username, "password": self.hash_password(password)})
        return user

    def create_user(self, username, password, role, created_by):
        """Crée un nouvel utilisateur système."""
        if not username or not password:
            return False, "Identifiant et mot de passe requis."
        # Vérifier si l'utilisateur existe déjà
        if self.db.users.find_one({"username": username}):
            return False, f"L'utilisateur '{username}' existe déjà."
        try:
            user_data = {
                "username": username,
                "password": self.hash_password(password),
                "role": role,
                "created_at": datetime.datetime.now()
            }
            self.db.users.insert_one(user_data)
            self.log_action(created_by, "CREATE_USER", f"Utilisateur {username} créé")
            return True, f"Utilisateur {username} créé avec succès."
        except Exception as e:
            return False, str(e)

    def get_all_users(self):
        return list(self.db.users.find({}, {"password": 0})) # Exclure le mot de passe

    # --- Journalisation (Logs) ---

    def log_action(self, user, action, details):
        """Enregistre une action dans la collection logs."""
        log_entry = {
            "user": user,
            "action": action,
            "details": details,
            "timestamp": datetime.datetime.now()
        }
        self.db.logs.insert_one(log_entry)

    def get_logs(self):
        """Récupère tous les logs triés par date décroissante."""
        return list(self.db.logs.find().sort("timestamp", DESCENDING))

    # --- Gestion des Patients ---

    def create_patient(self, nom, prenom, phone, email, assurance, notes, created_by):
        """Crée un nouveau dossier patient."""
        try:
            patient = {
                "nom": nom.upper(),
                "prenom": prenom.capitalize(),
                "telephone": phone,
                "email": email,
                "assurance": assurance,
                "notes_medicales": notes, # Peut être étendu dynamiquement
                "historique_visites": [],
                "created_at": datetime.datetime.now()
            }
            res = self.db.patients.insert_one(patient)
            self.log_action(created_by, "CREATE_PATIENT", f"Patient {nom} {prenom} créé (ID: {res.inserted_id})")
            return True, f"Patient ajouté avec succès."
        except Exception as e:
            return False, str(e)

    def search_patients(self, query):
        """Recherche globale (Nom, Prénom ou ID)."""
        if not query:
            return []
        
        # Recherche par ObjectId si la requête ressemble à un ID
        if ObjectId.is_valid(query):
            return list(self.db.patients.find({"_id": ObjectId(query)}))
        
        # Recherche textuelle (regex insensible à la casse)
        regex_query = {"$regex": query, "$options": "i"}
        return list(self.db.patients.find({
            "$or": [
                {"nom": regex_query},
                {"prenom": regex_query}
            ]
        }))

    def update_patient(self, patient_id, updated_data, updated_by):
        """Met à jour les informations d'un patient."""
        try:
            self.db.patients.update_one(
                {"_id": ObjectId(patient_id)},
                {"$set": updated_data}
            )
            self.log_action(updated_by, "UPDATE_PATIENT", f"Patient {patient_id} mis à jour")
            return True, "Informations patient mises à jour."
        except Exception as e:
            return False, str(e)

    # --- Gestion des Praticiens ---
    
    def get_practitioners(self):
        """Récupère la liste des praticiens."""
        # Pour simplifier l'exemple, si la liste est vide, on en crée par défaut
        if self.db.practitioners.count_documents({}) == 0:
            defaults = [
                {"nom": "Dr. Dupont", "specialite": "Généraliste"},
                {"nom": "Dr. Martin", "specialite": "Cardiologue"},
                {"nom": "Dr. Leroy", "specialite": "Pédiatre"}
            ]
            self.db.practitioners.insert_many(defaults)
        
        return list(self.db.practitioners.find())

    def create_practitioner(self, nom, specialite, created_by):
        """Ajoute un nouveau praticien."""
        try:
            practitioner = {
                "nom": nom,
                "specialite": specialite,
                "created_at": datetime.datetime.now()
            }
            self.db.practitioners.insert_one(practitioner)
            self.log_action(created_by, "CREATE_PRACTITIONER", f"Praticien {nom} ajouté")
            return True, "Praticien ajouté avec succès."
        except Exception as e:
            return False, str(e)

    def update_practitioner(self, practitioner_id, updated_data, updated_by):
        """Met à jour les informations d'un praticien."""
        try:
            self.db.practitioners.update_one(
                {"_id": ObjectId(practitioner_id)},
                {"$set": updated_data}
            )
            self.log_action(updated_by, "UPDATE_PRACTITIONER", f"Praticien {practitioner_id} mis à jour")
            return True, "Informations praticien mises à jour."
        except Exception as e:
            return False, str(e)

    def delete_practitioner(self, practitioner_id, deleted_by):
        """Supprime un praticien après vérification des RDV futurs."""
        try:
            prac = self.db.practitioners.find_one({"_id": ObjectId(practitioner_id)})
            if not prac:
                return False, "Praticien introuvable."

            # Vérifier s'il a des rendez-vous futurs non annulés
            future_appts = self.db.appointments.count_documents({
                "practitioner_name": prac["nom"],
                "date_heure_debut": {"$gte": datetime.datetime.now()},
                "statut": {"$not": {"$regex": "^Annulé"}}
            })
            if future_appts > 0:
                return False, f"Impossible : {future_appts} rendez-vous futur(s) existent pour ce praticien."

            res = self.db.practitioners.delete_one({"_id": ObjectId(practitioner_id)})
            if res.deleted_count > 0:
                self.log_action(deleted_by, "DELETE_PRACTITIONER", f"Praticien {prac['nom']} supprimé")
                return True, "Praticien supprimé."
            return False, "Erreur lors de la suppression."
        except Exception as e:
            return False, str(e)

    # --- Gestion des Rendez-vous ---

    def check_appointment_overlap(self, practitioner_name, start_time, end_time, exclude_appt_id=None):
        """Vérifie si un créneau est déjà pris pour un praticien."""
        # Un RDV chevauche si : (StartA < EndB) et (EndA > StartB)
        query = {
            "practitioner_name": practitioner_name,
            "statut": {"$not": {"$regex": "^Annulé"}},  # Ignore tous les statuts commençant par "Annulé"
            "$and": [
                {"date_heure_debut": {"$lt": end_time}},
                {"date_heure_fin": {"$gt": start_time}}
            ]
        }
        
        # Si on modifie un RDV existant, on l'exclut de la vérification (il ne peut pas se chevaucher lui-même)
        if exclude_appt_id:
            query["_id"] = {"$ne": ObjectId(exclude_appt_id)}

        count = self.db.appointments.count_documents(query)
        return count > 0

    def create_appointment(self, patient_id, practitioner_name, start_time, duration_minutes, motif, created_by):
        """Crée un rendez-vous avec validation de chevauchement."""
        # Vérifier que le RDV n'est pas dans le passé
        if start_time < datetime.datetime.now():
            return False, "Impossible de créer un rendez-vous dans le passé."

        end_time = start_time + datetime.timedelta(minutes=duration_minutes)

        if self.check_appointment_overlap(practitioner_name, start_time, end_time):
            return False, "Le praticien n'est pas disponible sur ce créneau."

        try:
            appt = {
                "patient_id": ObjectId(patient_id),
                "practitioner_name": practitioner_name,
                "date_heure_debut": start_time,
                "date_heure_fin": end_time,
                "duree_minutes": duration_minutes,
                "motif": motif,
                "statut": "Confirmé",
                "created_at": datetime.datetime.now()
            }
            self.db.appointments.insert_one(appt)
            
            # Mise à jour de l'historique du patient
            self.db.patients.update_one(
                {"_id": ObjectId(patient_id)},
                {"$push": {"historique_visites": {
                    "date": start_time,
                    "practitioner": practitioner_name,
                    "motif": motif
                }}}
            )
            
            self.log_action(created_by, "CREATE_APPT", f"RDV créé pour patient {patient_id} avec {practitioner_name}")
            return True, "Rendez-vous confirmé."
        except Exception as e:
            return False, str(e)

    def reschedule_appointment(self, appt_id, new_start_time, new_duration, user):
        """Déplace un rendez-vous (changement date/heure/durée)."""
        try:
            # Récupérer le RDV actuel
            current_appt = self.db.appointments.find_one({"_id": ObjectId(appt_id)})
            if not current_appt:
                return False, "Rendez-vous introuvable."

            # --- RÈGLE MÉTIER : Blocage si < 30 min ---
            now = datetime.datetime.now()
            time_diff = current_appt["date_heure_debut"] - now
            
            # Si le RDV est dans le passé ou dans moins de 30 min (et qu'on n'est pas admin par exemple)
            if time_diff.total_seconds() < 1800: # 1800 secondes = 30 min
                return False, "Impossible de décaler : le rendez-vous est dans moins de 30 minutes ou déjà passé."

            new_end_time = new_start_time + datetime.timedelta(minutes=new_duration)
            
            # Vérifier chevauchement en excluant le RDV actuel
            if self.check_appointment_overlap(current_appt["practitioner_name"], new_start_time, new_end_time, exclude_appt_id=appt_id):
                return False, "Ce créneau est déjà pris."

            self.db.appointments.update_one(
                {"_id": ObjectId(appt_id)},
                {"$set": {
                    "date_heure_debut": new_start_time,
                    "date_heure_fin": new_end_time,
                    "duree_minutes": new_duration
                }}
            )
            self.log_action(user, "RESCHEDULE_APPT", f"RDV {appt_id} déplacé au {new_start_time}")
            return True, "Rendez-vous modifié avec succès."
        except Exception as e:
            return False, str(e)

    def delete_appointment(self, appt_id, user):
        """Supprime définitivement un rendez-vous."""
        try:
            res = self.db.appointments.delete_one({"_id": ObjectId(appt_id)})
            if res.deleted_count > 0:
                self.log_action(user, "DELETE_APPT", f"RDV {appt_id} supprimé définitivement")
                return True, "Rendez-vous supprimé."
            return False, "Erreur suppression."
        except Exception as e:
            return False, str(e)

    def get_appointments(self, date_filter=None):
        """Récupère les RDV, optionnellement filtrés par date (journée entière)."""
        query = {}
        if date_filter:
            start_of_day = datetime.datetime.combine(date_filter, datetime.time.min)
            end_of_day = datetime.datetime.combine(date_filter, datetime.time.max)
            query["date_heure_debut"] = {"$gte": start_of_day, "$lte": end_of_day}
        
        # On fait un lookup (join) pour avoir le nom du patient directement si besoin,
        # mais pour simplifier ici on récupère juste les objets
        appts = list(self.db.appointments.find(query).sort("date_heure_debut", ASCENDING))
        
        # Enrichissement manuel des données patient pour l'affichage
        for appt in appts:
            pat = self.db.patients.find_one({"_id": appt["patient_id"]})
            if pat:
                appt["patient_nom"] = f"{pat['nom']} {pat['prenom']}"
            else:
                appt["patient_nom"] = "Inconnu"
        return appts

    def update_appointment_status(self, appt_id, new_status, updated_by):
        """Modifie le statut d'un RDV (Annulé, Absent, etc.)."""
        try:
            self.db.appointments.update_one(
                {"_id": ObjectId(appt_id)},
                {"$set": {"statut": new_status}}
            )
            self.log_action(updated_by, "UPDATE_APPT", f"RDV {appt_id} passé à {new_status}")
            return True
        except Exception as e:
            return False

    # --- Statistiques ---

    def get_stats_cancellation_rate(self):
        """Calcule le taux d'annulation (tous types confondus)."""
        total = self.db.appointments.count_documents({})
        cancelled = self.db.appointments.count_documents({"statut": {"$regex": "^Annulé"}})
        if total == 0: return 0
        return (cancelled / total) * 100

    def get_stats_workload(self):
        """Charge de travail par médecin (nombre de RDV non annulés)."""
        pipeline = [
            {"$match": {"statut": {"$not": {"$regex": "^Annulé"}}}},
            {"$group": {"_id": "$practitioner_name", "count": {"$sum": 1}}}
        ]
        return list(self.db.appointments.aggregate(pipeline))

    def get_dashboard_stats(self):
        """Retourne les KPIs pour le tableau de bord."""
        today_start = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
        today_end = datetime.datetime.combine(datetime.date.today(), datetime.time.max)

        total_patients = self.db.patients.count_documents({})
        total_appointments = self.db.appointments.count_documents({})
        today_appointments = self.db.appointments.count_documents({
            "date_heure_debut": {"$gte": today_start, "$lte": today_end}
        })
        active_practitioners = self.db.practitioners.count_documents({})
        cancellation_rate = self.get_stats_cancellation_rate()

        recent_logs = list(self.db.logs.find().sort("timestamp", DESCENDING).limit(5))

        # Appointments by day of week
        dow_pipeline = [
            {"$match": {"statut": {"$not": {"$regex": "^Annulé"}}}},
            {"$group": {
                "_id": {"$dayOfWeek": "$date_heure_debut"},
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}
        ]
        appts_by_day = list(self.db.appointments.aggregate(dow_pipeline))
        day_names = {1: "Dim", 2: "Lun", 3: "Mar", 4: "Mer", 5: "Jeu", 6: "Ven", 7: "Sam"}
        for item in appts_by_day:
            item["jour"] = day_names.get(item["_id"], "?")

        # Patient growth (by month)
        growth_pipeline = [
            {"$group": {
                "_id": {
                    "year": {"$year": "$created_at"},
                    "month": {"$month": "$created_at"}
                },
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id.year": 1, "_id.month": 1}}
        ]
        patient_growth = list(self.db.patients.aggregate(growth_pipeline))

        return {
            "total_patients": total_patients,
            "total_appointments": total_appointments,
            "today_appointments": today_appointments,
            "active_practitioners": active_practitioners,
            "cancellation_rate": cancellation_rate,
            "recent_logs": recent_logs,
            "appts_by_day": appts_by_day,
            "patient_growth": patient_growth
        }

