import streamlit as st
from datetime import datetime
import pandas as pd
from utils.database import get_connection
from fpdf import FPDF
import os

st.set_page_config(page_title="Enregistrer une Vente")
st.title("🛒 Enregistrement d'une Vente")

today = datetime.today().strftime('%Y-%m-%d')

# Initialiser les variables de session
if "id_client" not in st.session_state:
    st.session_state.id_client = None
if "client_verifie" not in st.session_state:
    st.session_state.client_verifie = False
if "facture_path" not in st.session_state:
    st.session_state.facture_path = None

clients_df = pd.read_sql_query("SELECT * FROM Client", get_connection())

st.subheader("👤 Sélection ou création du client")
choix = st.radio("Type de client :", ["Client existant", "Nouveau client"])

# Client existant
if choix == "Client existant":
    recherche = st.text_input("🔍 Rechercher un client (Nom ou Prénom)")
    id_selection = None
    if recherche:
        filtres = clients_df[
            clients_df['Nom'].str.contains(recherche, case=False) |
            clients_df['Prenom'].str.contains(recherche, case=False)
        ]
        if not filtres.empty:
            st.dataframe(filtres)
            id_selection = st.number_input("ID du client à sélectionner", min_value=1, step=1)

    if st.button("🔎 Vérifier"):
        if id_selection and id_selection in clients_df['Id_client'].values:
            st.session_state.id_client = id_selection
            st.session_state.client_verifie = True
            st.success(f"✅ Client vérifié : ID {id_selection}")
        else:
            st.warning("Veuillez entrer un ID de client valide.")

# Nouveau client
else:
    with st.form("form_nouveau_client"):
        nom = st.text_input("Nom")
        prenom = st.text_input("Prénom")
        localite = st.text_input("Localité")
        submit_client = st.form_submit_button("➕ Créer le client")

        if submit_client:
            if nom and prenom:
                try:
                    with get_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute(
                            "INSERT INTO Client (Nom, Prenom, Localite) VALUES (?, ?, ?)",
                            (nom, prenom, localite)
                        )
                        conn.commit()
                        st.session_state.id_client = cursor.lastrowid
                        st.session_state.client_verifie = True
                        st.success(f"✅ Nouveau client {nom} ajouté avec succès. ID : {st.session_state.id_client}")
                except Exception as e:
                    st.error(f"❌ Erreur lors de la création du client : {e}")
            else:
                st.error("Veuillez remplir au moins le nom et le prénom.")

# Enregistrement de la vente
if st.session_state.client_verifie and st.session_state.id_client:
    st.subheader("📋 Informations sur la vente")

    with st.form("form_vente"):
        nb_animaux = st.number_input("Nombre d'animaux vendus", min_value=1)
        prix_total = st.number_input("Prix total (FCFA)", min_value=1000, step=1000)
        description = st.text_area("Description (optionnelle)")
        submit_vente = st.form_submit_button("💾 Enregistrer la vente")

        # Vérification du stock
        stock_query = """
            SELECT 
                IFNULL((SELECT SUM(Quantite) FROM Animaux), 0) - 
                IFNULL((SELECT SUM(Nb_animaux) FROM Vente), 0) 
            AS Stock_disponible
        """
        stock_dispo = pd.read_sql_query(stock_query, get_connection()).iloc[0, 0]
        st.write(f"📦 Stock disponible : {stock_dispo} poulets")

        if submit_vente:
            if stock_dispo >= nb_animaux:
                try:
                    with get_connection() as conn:
                        cursor = conn.cursor()

                        # 1. Enregistrer la vente
                        cursor.execute(
                            "INSERT INTO Vente (Id_client, Nb_animaux, Prix_total, Description, Date_vente) VALUES (?, ?, ?, ?, ?)",
                            (st.session_state.id_client, nb_animaux, prix_total, description, today)
                        )
                        id_commande = cursor.lastrowid

                        # 2. Enregistrer le paiement
                        cursor.execute(
                            "INSERT INTO Payment (Id_vente, Id_client, Montant, Date_payment) VALUES (?, ?, ?, ?)",
                            (id_commande, st.session_state.id_client, prix_total, today)
                        )
                        conn.commit()

                    st.success("✅ Vente et paiement enregistrés avec succès ! 🎉")
                    st.balloons()

                    # 3. Génération de la facture PDF
                    facture_path = f"facture_{id_commande}.pdf"
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", size=12)
                    pdf.cell(200, 10, txt="FACTURE DE VENTE", ln=1, align="C")
                    pdf.ln(10)
                    pdf.cell(200, 10, txt=f"Date : {today}", ln=1)
                    pdf.cell(200, 10, txt=f"Client ID : {st.session_state.id_client}", ln=1)
                    pdf.cell(200, 10, txt=f"Commande ID : {id_commande}", ln=1)
                    pdf.cell(200, 10, txt=f"Nombre d'animaux : {nb_animaux}", ln=1)
                    pdf.cell(200, 10, txt=f"Montant : {prix_total} FCFA", ln=1)
                    pdf.cell(200, 10, txt=f"Description : {description}", ln=1)
                    pdf.output(facture_path)
                    st.session_state.facture_path = facture_path

                    with st.expander("🧾 Détails de la vente"):
                        st.markdown(f"""
                        - **Client ID** : {st.session_state.id_client}  
                        - **Nombre d'animaux** : {nb_animaux}  
                        - **Prix total** : {prix_total} FCFA  
                        - **Date** : {today}  
                        - **Description** : {description if description else "Aucune"}  
                        """)

                except Exception as e:
                    st.error(f"❌ Une erreur est survenue : {e}")
            else:
                st.error(f"❌ Stock insuffisant. Il reste seulement {stock_dispo} poulets.")

# Téléchargement de la facture
if st.session_state.facture_path:
    with open(st.session_state.facture_path, "rb") as f:
        st.download_button("📥 Télécharger la facture", f, file_name=st.session_state.facture_path, mime="application/pdf")
