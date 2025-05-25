import streamlit as st
import os
st.write(st.secrets)
# === CONFIGURATION ===
PASSWORD = st.secrets["auth"]["password"] 
PAGES = {
    "Accueil": "pages/mes_pages/main.py",
    "budget": "pages/mes_pages/ajout_budget.py",
    "depense": "pages/mes_pages/ajout_depense.py",
    "vente": "pages/mes_pages/enregistrer_vente.py",
    # ajoute les autres pages ici si besoin
}

# === INITIALISATION SESSION ===
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# === FONCTION DE CONNEXION ===
def login():
    st.image("logo.jpg", width=150)  # optionnel
    st.title("Connexion sécurisée")
    password = st.text_input("Mot de passe", type="password")
    if st.button("Se connecter"):
        if password == PASSWORD:
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

# === SI CONNECTÉ ===
st.sidebar.success("Connecté ✅")
st.sidebar.button("Se déconnecter", on_click=logout)

# Affichage des pages
selection = st.sidebar.radio("Navigation", list(PAGES.keys()))
import os

st.write("📁 Fichier actuel :", PAGES[selection])
st.write("✅ Existe ? ", os.path.exists(PAGES[selection]))
try:
    with open(PAGES[selection], "r", encoding="utf-8") as file:
        code = file.read()
        exec(code, globals())
except FileNotFoundError:
    st.error(f"❌ Le fichier {PAGES[selection]} est introuvable.")
