import streamlit as st
from datetime import datetime
from utils.database import get_connection

st.set_page_config(page_title="Ajouter une Dépense")
st.title("💸 Ajouter une Dépense")

# Connexion à la base de données
conn = get_connection()
cursor = conn.cursor()

# Formulaire pour enregistrer une dépense
with st.form("form_depense"):
    st.write("Veuillez entrer les détails de la dépense :")
    
    # Type de dépense
    type_depense = st.selectbox("Type de dépense", ["Alimentation", "Aménagement", "Soins", "Achat d'animaux", "Main d'œuvre"])
    
    # Montant de la dépense
    montant = st.number_input("Montant", min_value=0, step=100)
    
    # Date de la dépense (automatique ou personnalisée)
    date_depense = st.date_input("Date de la dépense", value=datetime.today().date())
    
    # Description de la dépense
    description = st.text_area("Description (optionnelle)")
    
    # Bouton d'enregistrement
    submitted = st.form_submit_button("Enregistrer la dépense")
    
    if submitted:
        cursor.execute("""
            INSERT INTO Depense (Type_depense, Montant, Date, Description)
            VALUES (?, ?, ?, ?)
        """, (type_depense, montant, date_depense.strftime('%Y-%m-%d'), description))
        
        conn.commit()
        st.success(f"✅ Dépense enregistrée avec succès !")
