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
for key in ["id_client", "client_verifie", "facture_path", "commande_enregistree"]:
    if key not in st.session_state:
        st.session_state[key] = None if key != "commande_enregistree" else False

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
                        cursor.execute(
                            "INSERT INTO Vente (Id_client, Nb_animaux, Prix_total, Description, Date_vente) VALUES (?, ?, ?, ?, ?)",
                            (st.session_state.id_client, nb_animaux, prix_total, description, today)
                        )
                        id_commande = cursor.lastrowid

                        cursor.execute(
                            "INSERT INTO Payment (Id_vente, Id_client, Montant, Date_payment) VALUES (?, ?, ?, ?)",
                            (id_commande, st.session_state.id_client, prix_total, today)
                        )
                        conn.commit()

                    infos_client = clients_df[clients_df["Id_client"] == st.session_state.id_client].iloc[0]
                    nom_client, prenom_client, localite_client = infos_client["Nom"], infos_client["Prenom"], infos_client["Localite"]

                    st.success("✅ Vente et paiement enregistrés avec succès ! 🎉")
                    st.balloons()

                    # Génération de la facture PDF
                    facture_path = f"facture_{id_commande}.pdf"
                    logo_path = "logo.jpg" 
                    cache_path = "cache.jpg" 

                    pdf = FPDF()
                    pdf.add_page()
                    pdf.image(logo_path, x=90, y=10, w=30)

                    pdf.set_font("Arial", 'B', 16)
                    pdf.ln(30)
                    pdf.cell(200, 30, txt="FACTURE DE VENTE", ln=1, align="C")
                    pdf.ln(10)

                    pdf.set_font("Arial", size=12)
                    pdf.cell(100, 10, txt=f"Date : {today}", ln=1)
                    pdf.cell(100, 10, txt=f"Nom du Client : {prenom_client} {nom_client}", ln=1)
                    pdf.cell(100, 10, txt=f"Localité : {localite_client}", ln=1)
                    pdf.cell(100, 10, txt=f"Commande numero : {id_commande}", ln=1)
                    pdf.ln(10)

                    pdf.set_fill_color(230, 230, 230)
                    pdf.set_font("Arial", 'B', 12)
                    pdf.cell(60, 10, "Désignation", 1, 0, 'C', True)
                    pdf.cell(40, 10, "Quantité", 1, 0, 'C', True)
                    pdf.cell(50, 10, "Prix Total (FCFA)", 1, 1, 'C', True)

                    pdf.set_font("Arial", size=12)
                    pdf.cell(60, 10, "Poulets", 1)
                    pdf.cell(40, 10, str(nb_animaux), 1)
                    pdf.cell(50, 10, str(prix_total), 1, 1)

                    pdf.ln(10)
                    pdf.multi_cell(0, 10, f"Description : {description if description else 'Aucune'}")

                    pdf.image(cache_path, x=165, y=200, w=30)

                    pdf.output(facture_path)
                    st.session_state.facture_path = facture_path
                    st.session_state.commande_enregistree = True

                    with st.expander("🧾 Détails de la vente"):
                        st.markdown(f"""
                        - **Client** : {prenom_client} {nom_client}  
                        - **Localité** : {localite_client}  
                        - **Nombre d'animaux** : {nb_animaux}  
                        - **Prix total** : {prix_total} FCFA  
                        - **Date** : {today}  
                        - **Description** : {description if description else "Aucune"}  
                        """)

                except Exception as e:
                    st.error(f"❌ Une erreur est survenue : {e}")
            else:
                st.error(f"❌ Stock insuffisant. Il reste seulement {stock_dispo} poulets.")

# Télécharger la facture
if st.session_state.facture_path and st.session_state.commande_enregistree:
    with open(st.session_state.facture_path, "rb") as f:
        if st.download_button(
            "📥 Télécharger la facture",
            f,
            file_name=st.session_state.facture_path,
            mime="application/pdf"
        ):
            st.session_state.id_client = None
            st.session_state.client_verifie = False
            st.session_state.facture_path = None
            st.session_state.commande_enregistree = False
            st.rerun()

# Pied de page
st.markdown("---")
st.markdown("© 2025 NovaSolution – L'innovation au service de votre réussite.")
