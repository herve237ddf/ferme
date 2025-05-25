import streamlit as st
import os
from pathlib import Path

# === CONFIGURATION ===
USERNAME = st.secrets["auth"]["username"] 
PASSWORD = st.secrets["auth"]["password"] 
PAGES = {
    "Accueil": "pages/mes_pages/main.py",
    "budget": "pages/mes_pages/ajout_budget.py",
    "depense": "pages/mes_pages/ajout_depense.py",
    "vente": "pages/mes_pages/enregistrer_vente.py",
}

# === INITIALISATION DE LA SESSION ===
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# === FONCTION DE CONNEXION ===
def login():
    st.image("logo.jpg", width=150)
    st.title("Connexion sécurisée")
    username = st.text_input("Nom d'utilisateur")
    password = st.text_input("Mot de passe", type="password")
    if st.button("Se connecter"):
        if username == USERNAME and password == PASSWORD:
            st.session_state.authenticated = True
            st.success("Connexion réussie !")
            st.rerun()
        else:
            st.error("Nom d'utilisateur ou mot de passe incorrect")

# === FONCTION DE DECONNEXION ===
def logout():
    st.session_state.authenticated = False
    st.rerun()

# === AUTHENTIFICATION ===
if not st.session_state.authenticated:
    login()
    st.stop()

# === NAVIGATION ===
st.sidebar.success(f"✅ Bonjour Mr {username}")
st.markdown("---")
st.sidebar.title("Menu")
st.markdown("---")
selection = st.sidebar.radio("Navigation", list(PAGES.keys()))

st.markdown("---")
st.sidebar.button("🔓 Déconnexion", on_click=logout)

# === AFFICHAGE DES PAGES ===
selected_file = PAGES.get(selection)
if selected_file and Path(selected_file).exists():
    with open(selected_file, "r", encoding="utf-8") as f:
        code = f.read()
        exec(code, globals())  # À remplacer plus tard par importlib pour + sécurité
else:
    st.error(f"❌ Le fichier {selected_file} est introuvable.")
    st.info("Contactez le développeur à l'adresse : nguefaherve@gmail.com")
