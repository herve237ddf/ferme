import streamlit as st
import os

# === CONFIGURATION ===
USERNAME = st.secrets["auth"]["username "] 
PASSWORD = st.secrets["auth"]["password"] 
PAGES = {
    "Accueil": "pages/mes_pages/main.py",
    "budget": "pages/mes_pages/ajout_budget.py",
    "depense": "pages/mes_pages/ajout_depense.py",
    "vente": "pages/mes_pages/enregistrer_vente.py",
}

# === INITIALISATION SESSION ===
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# === FONCTION DE CONNEXION ===
def login():
    st.image("logo.jpg", width=150) 
    st.title("Connexion sécurisée")
    username = st.text_input("nom utilisateur", type="text")
    password = st.text_input("Mot de passe", type="password")
    if st.button("Se connecter"):
        if password == PASSWORD AND username == USERNAME:
            st.session_state.authenticated = True
            st.success("Connexion réussie !")
            st.rerun()

        else:
            st.error("Mot de passe incorrect")

# === FONCTION DE DECONNEXION ===
def logout():
    st.session_state.authenticated = False
    st.rerun()

# === LOGIQUE PRINCIPALE ===
if not st.session_state.authenticated:
    login()
    st.stop()

# Affichage des pages
selection = st.sidebar.radio("Navigation", list(PAGES.keys()))

try:
    with open(PAGES[selection], "r", encoding="utf-8") as file:
        code = file.read()
        exec(code, globals())
except FileNotFoundError:
    st.error(f"❌ Le fichier {PAGES[selection]} est introuvable.")
    st.write("Contactez le developpeur a l'adress mail : nguefaherve@gmail.com")
