import streamlit as st
from datetime import date
from utils.database import get_connection

st.set_page_config(page_title="Ajouter un Stock")
st.title("🐥 Ajouter un Stock de Poulets")

# Connexion à la base de données
conn = get_connection()
cursor = conn.cursor()

# Date actuelle
today = date.today()

# Formulaire pour ajouter un stock
with st.form("form_stock"):
    quantite = st.number_input("Quantité de poulets", min_value=1, step=1)
    submitted = st.form_submit_button("Enregistrer")

    if submitted:
        cursor.execute(
            "INSERT INTO Animaux (quantite, date_ajout) VALUES (?, ?)",
            (quantite, today.strftime('%Y-%m-%d'))
        )
        conn.commit()
        st.success(f"✅ {quantite} poulet(s) ajouté(s) au stock avec succès !")

# Pied de page
st.markdown("---")
st.markdown("© 2025 NovaSolution – L'innovation au service de votre réussite.")