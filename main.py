import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Tableau de Bord Ferme", layout="wide")


# === CONFIGURATION ===
PASSWORD = "supersecret"
USERNAME = "Fabrice"
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
    # CSS pour centrer et fixer largeur à 60%
    st.markdown("""
        <style>
            .login-container {
                max-width: 60%;
                margin-left: auto;
                margin-right: auto;
                text-align: center;
            }
            .login-container img {
                display: block;
                margin-left: auto;
                margin-right: auto;
                margin-bottom: 20px;
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.image("logo.jpg", width=150)
    st.title("Connexion sécurisée")
    username = st.text_input("Nom d'utilisateur")
    password = st.text_input("Mot de passe", type="password")
    if st.button("Se connecter"):
        if username == USERNAME and password == PASSWORD:
            st.session_state.authenticated = True
            st.success("Connexion réussie !")
            st.rerun()  # Remplace st.rerun() qui est deprecated
        else:
            st.error("Nom d'utilisateur ou mot de passe incorrect")
    st.markdown('</div>', unsafe_allow_html=True)

# === FONCTION DE DECONNEXION ===
def logout():
    st.session_state.authenticated = False

# === AUTHENTIFICATION ===
if not st.session_state.authenticated:
    login()
    st.stop()

# === NAVIGATION ===
st.sidebar.success(f"✅ Bonjour Mr {USERNAME}")
st.sidebar.markdown("---")
st.sidebar.title("Menu")
st.sidebar.markdown("---")
selection = st.sidebar.radio("Navigation", list(PAGES.keys()))
st.sidebar.markdown("---")
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
