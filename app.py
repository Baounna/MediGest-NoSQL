import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
from db_manager import DBManager

# --- Configuration de la page ---
st.set_page_config(
    page_title="MediGest - Gestion Cabinet Médical",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Initialisation ---
if 'db' not in st.session_state:
    st.session_state.db = DBManager()

if 'user' not in st.session_state:
    st.session_state.user = None

# --- Fonctions Utilitaires UI ---

def login_form():
    """Affiche le formulaire de connexion dans la sidebar."""
    st.sidebar.title("🔐 Connexion")
    username = st.sidebar.text_input("Identifiant")
    password = st.sidebar.text_input("Mot de passe", type="password")
    
    if st.sidebar.button("Se connecter"):
        user = st.session_state.db.check_user(username, password)
        if user:
            st.session_state.user = {
                "username": user["username"],
                "role": user["role"]
            }
            st.rerun()
        else:
            st.sidebar.error("Identifiants incorrects")

def logout():
    """Déconnecte l'utilisateur."""
    st.session_state.db.log_action(st.session_state.user["username"], "LOGOUT", "Déconnexion utilisateur")
    st.session_state.user = None
    st.rerun()

# --- Vues par Rôle ---

def view_accueil():
    st.header("🏢 Accueil & Secrétariat")
    
    # Navigation avec état pour permettre la redirection (Remplacement des st.tabs standards)
    tabs_options = ["📅 Agenda", "👤 Gestion Patients", "➕ Nouveau Rendez-vous", "📋 Liste Globale"]
    
    # Initialisation de l'onglet actif
    if "current_accueil_tab" not in st.session_state:
        st.session_state.current_accueil_tab = tabs_options[0]

    # On utilise radio horizontal. 
    # ASTUCE : On ne lie pas directement le 'key' du widget à notre variable de contrôle pour éviter le conflit.
    # On utilise 'index' pour forcer la position.
    try:
        current_index = tabs_options.index(st.session_state.current_accueil_tab)
    except ValueError:
        current_index = 0

    selected_tab = st.radio(
        "Navigation", 
        tabs_options, 
        horizontal=True, 
        label_visibility="collapsed", 
        index=current_index
    )
    
    # Mise à jour de l'état si l'utilisateur clique sur un onglet différent
    if selected_tab != st.session_state.current_accueil_tab:
        st.session_state.current_accueil_tab = selected_tab
        st.rerun()
    
    # --- Onglet Agenda ---
    if st.session_state.current_accueil_tab == "📅 Agenda":
        st.subheader("Agenda du jour")
        col1, col2 = st.columns([1, 3])
        with col1:
            selected_date = st.date_input("Choisir une date", datetime.date.today())
        
        appts = st.session_state.db.get_appointments(selected_date)
        
        if appts:
            df_appts = pd.DataFrame(appts)
            # Mise en forme pour l'affichage
            df_display = df_appts[["date_heure_debut", "date_heure_fin", "practitioner_name", "patient_nom", "motif", "statut", "_id", "duree_minutes"]]
            df_display["Heure"] = df_display["date_heure_debut"].dt.strftime("%H:%M")
            
            # Affichage interactif
            for index, row in df_display.iterrows():
                # Détermination de la couleur/emoji selon le statut
                icon = "🟢" if row['statut'] == "Confirmé" else "🔴" if row['statut'] == "Annulé" else "🟠"
                
                with st.expander(f"{icon} {row['Heure']} - {row['patient_nom']} (Dr. {row['practitioner_name']})"):
                    st.write(f"**Motif:** {row['motif']}")
                    st.write(f"**Statut:** {row['statut']}")
                    st.write(f"**Fin prévue:** {row['date_heure_fin'].strftime('%H:%M')}")
                    
                    st.markdown("---")
                    
                    # Section Actions Rapides
                    c1, c2, c3 = st.columns(3)
                    if row['statut'] != "Annulé":
                        if c1.button("Annuler RDV", key=f"cancel_{row['_id']}"):
                            st.session_state.db.update_appointment_status(row['_id'], "Annulé", st.session_state.user["username"])
                            st.rerun()
                        if c2.button("Marquer Absent", key=f"absent_{row['_id']}"):
                            st.session_state.db.update_appointment_status(row['_id'], "Absent", st.session_state.user["username"])
                            st.rerun()
                    
                    if c3.button("🗑️ Supprimer", key=f"del_{row['_id']}", help="Supprime définitivement de la base"):
                        success, msg = st.session_state.db.delete_appointment(row['_id'], st.session_state.user["username"])
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

                    # Section Modification (Décalage)
                    st.markdown("#### 🔄 Modifier / Décaler")
                    with st.form(key=f"edit_form_{row['_id']}"):
                        new_date = st.date_input("Nouvelle date", value=row['date_heure_debut'].date())
                        new_time = st.time_input("Nouvelle heure", value=row['date_heure_debut'].time())
                        new_duree = st.number_input("Durée (min)", value=int(row['duree_minutes']), step=15)
                        
                        if st.form_submit_button("Sauvegarder les changements"):
                            new_start = datetime.datetime.combine(new_date, new_time)
                            success, msg = st.session_state.db.reschedule_appointment(
                                row['_id'], new_start, new_duree, st.session_state.user["username"]
                            )
                            if success:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
        else:
            st.info("Aucun rendez-vous pour cette date.")

    # --- Onglet Gestion Patients ---
    elif st.session_state.current_accueil_tab == "👤 Gestion Patients":
        st.subheader("Dossiers Patients")
        
        # Barre de recherche globale
        search_query = st.text_input("🔍 Rechercher un patient (Nom, Prénom)", "")
        
        if search_query:
            results = st.session_state.db.search_patients(search_query)
            if results:
                st.success(f"{len(results)} patient(s) trouvé(s)")
                for pat in results:
                    with st.expander(f"📂 {pat['nom']} {pat['prenom']}"):
                        # --- Feature Request: Bouton de redirection ---
                        if st.button("📅 Prendre RDV pour ce patient", key=f"btn_nav_rdv_{pat['_id']}"):
                            st.session_state.rdv_patient_results = [pat]
                            st.session_state.rdv_search_performed = True
                            st.session_state.current_accueil_tab = "➕ Nouveau Rendez-vous"
                            st.rerun()
                        
                        #st.write(f"**ID:** {pat['_id']}")
                        st.write(f"**Tél:** {pat.get('telephone', 'N/A')}")
                        st.write(f"**Email:** {pat.get('email', 'N/A')}")
                        st.write(f"**Assurance:** {pat.get('assurance', 'N/A')}")
                        st.write("**Notes Médicales:**")
                        st.info(pat.get('notes_medicales', 'Aucune note'))
                        st.write("**Historique Visites:**")
                        st.table(pd.DataFrame(pat.get('historique_visites', [])))

                        # --- Section Modification Patient ---
                        with st.expander("📝 Modifier les informations"):
                            with st.form(key=f"edit_patient_{pat['_id']}"):
                                e_nom = st.text_input("Nom", value=pat['nom'])
                                e_prenom = st.text_input("Prénom", value=pat['prenom'])
                                e_tel = st.text_input("Téléphone", value=pat.get('telephone', ''))
                                e_email = st.text_input("Email", value=pat.get('email', ''))
                                e_assurance = st.text_input("Assurance", value=pat.get('assurance', ''))
                                e_notes = st.text_area("Notes Médicales", value=pat.get('notes_medicales', ''))
                                
                                if st.form_submit_button("Enregistrer les modifications"):
                                    updated_data = {
                                        "nom": e_nom.upper(),
                                        "prenom": e_prenom.capitalize(),
                                        "telephone": e_tel,
                                        "email": e_email,
                                        "assurance": e_assurance,
                                        "notes_medicales": e_notes
                                    }
                                    success, msg = st.session_state.db.update_patient(pat['_id'], updated_data, st.session_state.user["username"])
                                    if success:
                                        st.success(msg)
                                        st.rerun()
                                    else:
                                        st.error(msg)
            else:
                st.warning("Aucun patient trouvé.")
        
        st.markdown("---")
        st.subheader("Créer un nouveau patient")
        with st.form("new_patient_form"):
            c1, c2 = st.columns(2)
            nom = c1.text_input("Nom")
            prenom = c2.text_input("Prénom")
            tel = c1.text_input("Téléphone")
            email = c2.text_input("Email")
            assurance = st.text_input("Numéro Assurance / Sécu")
            notes = st.text_area("Notes initiales")
            
            submitted = st.form_submit_button("Enregistrer Patient")
            if submitted:
                if nom and prenom:
                    success, msg = st.session_state.db.create_patient(
                        nom, prenom, tel, email, assurance, notes, st.session_state.user["username"]
                    )
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)
                else:
                    st.error("Nom et Prénom obligatoires.")

    # --- Onglet Nouveau RDV ---
    elif st.session_state.current_accueil_tab == "➕ Nouveau Rendez-vous":
        st.subheader("Prendre un Rendez-vous")
        
        # --- Sélection du Patient (Stable avec état) ---
        # Initialisation de la liste des résultats dans la session si elle n'existe pas
        if 'rdv_patient_results' not in st.session_state:
            st.session_state.rdv_patient_results = []
        if 'rdv_search_performed' not in st.session_state:
            st.session_state.rdv_search_performed = False

        selected_patient_id = None

        # --- Section de Recherche (Toujours visible) ---
        st.markdown("##### 1. Rechercher et Sélectionner le Patient")
        col_search, col_btn = st.columns([3, 1])
        with col_search:
            search_query = st.text_input("Rechercher par Nom, Prénom ou ID", key="search_pat_input", placeholder="Ex: Dupont ou 65b...")
        with col_btn:
            st.write("") 
            st.write("") 
            if st.button("🔍 Rechercher", key="btn_search_trigger"):
                st.session_state.rdv_search_performed = True
                if search_query:
                    st.session_state.rdv_patient_results = st.session_state.db.search_patients(search_query)
                else:
                    st.session_state.rdv_patient_results = []
                    st.warning("Veuillez saisir une recherche.")

        # --- Affichage des résultats / Sélection actuelle ---
        if st.session_state.rdv_patient_results:
            # Création du dictionnaire {Label: ID}
            pat_options = {f"{p['nom']} {p['prenom']} (Tél: {p.get('telephone', 'N/A')})": p['_id'] for p in st.session_state.rdv_patient_results}
            
            # Si un seul résultat (cas de la redirection), il est sélectionné par défaut
            selected_label = st.selectbox("✅ Sélectionner le patient :", list(pat_options.keys()), key="select_pat_final")
            selected_patient_id = pat_options[selected_label]
            
            if len(st.session_state.rdv_patient_results) == 1:
                st.info(f"📍 Patient sélectionné : **{selected_label}**")
        elif st.session_state.rdv_search_performed:
            st.error("❌ Aucun patient trouvé. Veuillez vérifier l'orthographe ou l'ID.")

        st.markdown("---")
        st.markdown("##### 2. Détails du Rendez-vous")
        
        practitioners = st.session_state.db.get_practitioners()
        practitioner_names = [p["nom"] for p in practitioners]
        
        with st.form("new_appt_form"):
            practitioner = st.selectbox("Praticien", practitioner_names)
            col_d, col_t = st.columns(2)
            date_rdv = col_d.date_input("Date", datetime.date.today())
            time_rdv = col_t.time_input("Heure de début", datetime.time(9, 0))
            duree = st.number_input("Durée (minutes)", min_value=15, max_value=120, value=30, step=15)
            motif = st.text_input("Motif de la consultation")
            
            submit_rdv = st.form_submit_button("Confirmer le Rendez-vous")
            
            if submit_rdv:
                if selected_patient_id:
                    # Combinaison date et heure
                    start_datetime = datetime.datetime.combine(date_rdv, time_rdv)
                    
                    success, msg = st.session_state.db.create_appointment(
                        selected_patient_id, practitioner, start_datetime, duree, motif, st.session_state.user["username"]
                    )
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)
                else:
                    st.error("Veuillez sélectionner un patient dans la liste ci-dessus.")

    # --- Onglet Liste Globale (Planning par Praticien) ---
    elif st.session_state.current_accueil_tab == "📋 Liste Globale":
        st.subheader("🗓️ Planning par Praticien & Gestion des Aléas")
        
        all_appts = st.session_state.db.get_appointments()
        practitioners = st.session_state.db.get_practitioners()
        
        if all_appts:
            df_all = pd.DataFrame(all_appts)
            
            for prac in practitioners:
                prac_name = prac["nom"]
                with st.expander(f"👨‍⚕️ {prac_name} - {prac.get('specialite', 'Généraliste')}", expanded=True):
                    # Filtrage
                    df_prac = df_all[df_all["practitioner_name"] == prac_name]
                    
                    if not df_prac.empty:
                        # Tri
                        df_prac = df_prac.sort_values(by="date_heure_debut")
                        
                        # En-têtes de colonnes
                        h1, h2, h3, h4, h5 = st.columns([2, 3, 3, 2, 3])
                        h1.markdown("**Horaire**")
                        h2.markdown("**Patient**")
                        h3.markdown("**Motif**")
                        h4.markdown("**Statut**")
                        h5.markdown("**Actions Rapides**")
                        st.divider()

                        for idx, row in df_prac.iterrows():
                            c1, c2, c3, c4, c5 = st.columns([2, 3, 3, 2, 3])
                            
                            start_str = row["date_heure_debut"].strftime("%d/%m %H:%M")
                            c1.write(f"📅 {start_str}")
                            c2.write(f"👤 {row['patient_nom']}")
                            c3.write(f"📝 {row['motif']}")
                            
                            # Statut avec couleur
                            status_color = "green" if row['statut'] == "Confirmé" else "red" if "Annulé" in row['statut'] else "orange"
                            c4.markdown(f":{status_color}[{row['statut']}]")
                            
                            # Actions si le RDV n'est pas déjà annulé
                            if "Annulé" not in row['statut']:
                                with c5:
                                    # Calcul du temps restant pour la règle des 30 min
                                    now = datetime.datetime.now()
                                    time_diff = row["date_heure_debut"] - now
                                    is_too_close = time_diff.total_seconds() < 1800 # 30 min

                                    if is_too_close:
                                        st.caption("🔒 *Modification bloquée (<30min)*")
                                    
                                    # Formulaire compact pour le retard personnalisé
                                    with st.popover("🕒 Signaler Retard"):
                                        delay_min = st.number_input("Minutes de retard", min_value=1, max_value=120, value=15, step=5, key=f"val_delay_{row['_id']}")
                                        if st.button("Appliquer le retard", key=f"btn_apply_{row['_id']}"):
                                            new_start = row["date_heure_debut"] + datetime.timedelta(minutes=delay_min)
                                            # On tente le décalage (la DB vérifiera aussi la règle des 30min)
                                            success, msg = st.session_state.db.reschedule_appointment(
                                                row['_id'], new_start, row['duree_minutes'], st.session_state.user["username"]
                                            )
                                            if success:
                                                st.toast(f"Retard de {delay_min} min appliqué.")
                                                st.rerun()
                                            else:
                                                st.error(msg)
                                    
                                    # Bouton Absence Médecin
                                    if st.button("🚫 Absence Med.", key=f"doc_abs_{row['_id']}", help="Annuler car le médecin est absent"):
                                        st.session_state.db.update_appointment_status(row['_id'], "Annulé (Médecin Absent)", st.session_state.user["username"])
                                        st.toast("RDV annulé pour absence médecin.")
                                        st.rerun()
                            else:
                                c5.write("🔒 *Clôturé*")
                            
                            st.divider() # Séparateur entre les lignes
                    else:
                        st.info(f"Aucun rendez-vous pour Dr. {prac_name}.")
        else:
            st.info("Aucun rendez-vous dans le système.")

def view_responsable():
    st.header("📊 Tableau de Bord - Responsable")
    
    st.subheader("Indicateurs Clés (KPI)")
    
    # Récupération des stats
    cancel_rate = st.session_state.db.get_stats_cancellation_rate()
    workload_data = st.session_state.db.get_stats_workload()
    
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Taux d'annulation", f"{cancel_rate:.1f}%")
    kpi2.metric("Total Praticiens", len(st.session_state.db.get_practitioners()))
    # kpi3 libre pour autre stat
    
    st.markdown("---")
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Charge de travail par médecin")
        if workload_data:
            df_workload = pd.DataFrame(workload_data)
            fig = px.bar(df_workload, x="_id", y="count", 
                         labels={"_id": "Médecin", "count": "Nombre de RDV"},
                         title="RDV Confirmés/Réalisés")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Pas assez de données pour les graphiques.")
            
    with c2:
        st.subheader("Répartition temporelle")
        st.info("Fonctionnalité à venir : Heatmap des heures de pointe.")

def view_admin():
    st.header("🛠️ Administration Système")
    
    tab_users, tab_practitioners, tab_logs = st.tabs(["Gestion Utilisateurs", "Gestion Praticiens", "Logs Système"])
    
    with tab_users:
        st.subheader("Utilisateurs existants")
        users = st.session_state.db.get_all_users()
        st.dataframe(pd.DataFrame(users))
        
        st.markdown("### Créer un nouvel utilisateur")
        with st.form("create_user"):
            new_user = st.text_input("Nouvel Identifiant")
            new_pass = st.text_input("Mot de passe", type="password")
            new_role = st.selectbox("Rôle", ["Accueil", "Responsable", "Administrateur"])
            
            if st.form_submit_button("Créer"):
                if st.session_state.db.create_user(new_user, new_pass, new_role, st.session_state.user["username"]):
                    st.success(f"Utilisateur {new_user} créé !")
                    st.rerun()
                else:
                    st.error("Erreur lors de la création.")

    with tab_practitioners:
        st.subheader("Praticiens")
        practitioners = st.session_state.db.get_practitioners()
        
        if practitioners:
            # Affichage en liste avec bouton de suppression
            for p in practitioners:
                col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                col1.write(f"**{p['nom']}**")
                col2.write(f"_{p['specialite']}_")
                
                # Modification
                with col3.popover("📝 Editer"):
                    with st.form(key=f"edit_prac_{p['_id']}"):
                        e_nom = st.text_input("Nom", value=p['nom'])
                        e_spec = st.text_input("Spécialité", value=p['specialite'])
                        if st.form_submit_button("Enregistrer"):
                            updated_data = {"nom": e_nom, "specialite": e_spec}
                            success, msg = st.session_state.db.update_practitioner(p['_id'], updated_data, st.session_state.user["username"])
                            if success:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)

                if col4.button("🗑️ Supprimer", key=f"del_prac_{p['_id']}"):
                    success, msg = st.session_state.db.delete_practitioner(p['_id'], st.session_state.user["username"])
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
        else:
            st.info("Aucun praticien enregistré.")

        st.markdown("---")
        st.subheader("Ajouter un Praticien")
        with st.form("add_practitioner"):
            nom_prac = st.text_input("Nom (ex: Dr. House)")
            spec_prac = st.text_input("Spécialité (ex: Diagnosticien)")
            
            if st.form_submit_button("Ajouter"):
                if nom_prac and spec_prac:
                    success, msg = st.session_state.db.create_practitioner(nom_prac, spec_prac, st.session_state.user["username"])
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.error("Tous les champs sont requis.")

    with tab_logs:
        st.subheader("Journal d'audit")
        logs = st.session_state.db.get_logs()
        if logs:
            df_logs = pd.DataFrame(logs)
            st.dataframe(df_logs)
        else:
            st.info("Aucun log disponible.")

# --- Point d'entrée Principal ---

def main():
    # Vérification DB
    if st.session_state.db.db is None:
        st.error("❌ Impossible de se connecter à la base de données. Vérifiez que MongoDB est lancé.")
        return

    # Gestion de la Sidebar (Navigation / User Info)
    with st.sidebar:
        st.title("MediGest 🏥")
        if st.session_state.user:
            st.success(f"Connecté en tant que : **{st.session_state.user['username']}**")
            st.info(f"Rôle : {st.session_state.user['role']}")
            if st.button("Déconnexion"):
                logout()
        else:
            login_form()

    # Routing des vues
    if st.session_state.user:
        role = st.session_state.user["role"]
        
        # Logique simple de permission hiérarchique ou stricte
        if role == "Administrateur":
            # L'admin a accès à tout, on lui met un sélecteur
            view_choice = st.sidebar.radio("Navigation", ["Accueil", "Statistiques", "Administration"])
            if view_choice == "Accueil":
                view_accueil()
            elif view_choice == "Statistiques":
                view_responsable()
            else:
                view_admin()
        
        elif role == "Responsable":
            view_choice = st.sidebar.radio("Navigation", ["Accueil", "Statistiques"])
            if view_choice == "Accueil":
                view_accueil()
            else:
                view_responsable()
                
        elif role == "Accueil":
            view_accueil()
            
    else:
        st.title("Bienvenue sur MediGest")
        st.markdown("""
        Veuillez vous connecter via le menu latéral pour accéder au système.
        
        **Identifiants par défaut (si première installation) :**
        * User: `admin`
        * Pass: `admin123`
        """)
        st.image("https://img.freepik.com/free-vector/health-professional-team-concept-illustration_114360-1618.jpg?w=826&t=st=1706000000~exp=1706000600~hmac=fake", width=400)

if __name__ == "__main__":
    main()
