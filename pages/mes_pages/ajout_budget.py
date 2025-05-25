import streamlit as st
import sqlite3
from datetime import date
from utils.database import get_connection

#st.set_page_config(page_title="Ajouter un Budget")
st.title("💰 Ajouter un Budget")

conn = get_connection()
cursor = conn.cursor()

with st.form("form_budget"):
    st.write("Veuillez entrer les détails du budget :")
    montant = st.number_input("Montant du budget", min_value=0, step=1000)
    date_debut = st.date_input("Date de début", value=date.today())
    date_fin = st.date_input("Date de fin", min_value = date_debut)
    submitted = st.form_submit_button("Enregistrer")

    if submitted:
        if (date_debut > date_fin):
            st.error("La date de début ne peut pas être après la date de fin.")
        elif montant <= 1000:
            st.error("Le montant doit être supérieur à 1000 FCFA.")    
        else:
            try:
                cursor.execute("INSERT INTO Budget (Date_debut, Date_fin, Montant) VALUES (?, ?, ?)",
                               (date_debut.strftime('%Y-%m-%d'), date_fin.strftime('%Y-%m-%d'), montant))
                conn.commit()
                st.success("✅ Budget enregistré avec succès !")
            except sqlite3.OperationalError:
                st.error("❌ Assurez-vous que la colonne 'Montant' existe déjà dans la table Budget.")


# Pied de page
st.markdown("---")
st.markdown("© 2025 NovaSolution – L'innovation au service de votre réussite.")
