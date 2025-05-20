import streamlit as st
from datetime import datetime
import pandas as pd
from utils.database import get_connection
from fpdf import FPDF
import io

# Définir la configuration de la page une seule fois
st.set_page_config(page_title="Enregistrement et Facture")




# Initialiser la session
def init_facture_session():
    if "facture" not in st.session_state:
        st.session_state.facture = {}

# Menu de navigation
def main():
    st.sidebar.title("Menu")
    page = st.sidebar.selectbox("Sélectionner une page", ["Enregistrer une Vente", "Facture"])
    
    if page == "Enregistrer une Vente":
        enregistrer_vente()
    elif page == "Facture":
        page_facture()

# Page d'enregistrement de vente
def enregistrer_vente():
    init_facture_session()
    st.title("🛒 Enregistrement d'une Vente")
    conn = get_connection()
    cursor = conn.cursor()
    today = datetime.today().strftime('%Y-%m-%d')

    clients_df = pd.read_sql_query("SELECT * FROM Client", conn)
    st.subheader("👤 Sélection ou création du client")
    choix = st.radio("Type de client :", ["Client existant", "Nouveau client"])

    id_client = None
    client_verifie = False

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
                id_client = id_selection
                client_verifie = True
                st.success(f"✅ Client vérifié : ID {id_client}")
            else:
                st.warning("Veuillez entrer un ID de client valide.")
    else:
        with st.form("form_nouveau_client"):
            nom = st.text_input("Nom")
            prenom = st.text_input("Prénom")
            localite = st.text_input("Localité")
            submit_client = st.form_submit_button("➕ Créer le client")

            if submit_client:
                if nom and prenom:
                    cursor.execute("INSERT INTO Client (Nom, Prenom, Localite) VALUES (?, ?, ?)", (nom, prenom, localite))
                    conn.commit()
                    id_client = cursor.lastrowid
                    client_verifie = True
                    st.success(f"✅ Nouveau client {nom} ajouté avec succès. ID : {id_client}")
                else:
                    st.error("Veuillez remplir au moins le nom et le prénom.")

    if client_verifie and id_client:
        st.subheader("📋 Informations sur la vente")
        with st.form("form_vente"):
            nb_animaux = st.number_input("Nombre d'animaux vendus", min_value=1)
            prix_total = st.number_input("Prix total", min_value=1000, step=1000)
            description = st.text_area("Description (optionnelle)")
            submit_vente = st.form_submit_button("💾 Enregistrer la vente")

            stock_query = """
                SELECT 
                    IFNULL((SELECT SUM(Quantite) FROM Animaux), 0) - 
                    IFNULL((SELECT SUM(Nb_animaux) FROM Vente), 0) 
                AS Stock_disponible
            """
            stock_dispo = pd.read_sql_query(stock_query, conn).iloc[0, 0]
            st.write(f"Stock disponible : {stock_dispo} poulets")

            if submit_vente:
                if stock_dispo >= nb_animaux:
                    # Enregistrer la vente
                    cursor.execute("""
                        INSERT INTO Vente (Id_client, Nb_animaux, Prix_total, Date_vente, Description)
                        VALUES (?, ?, ?, ?, ?)
                    """, (id_client, nb_animaux, prix_total, today, description))
                    conn.commit()
                    id_vente = cursor.lastrowid

                    # Enregistrer le paiement
                    cursor.execute("""
                        INSERT INTO Payment (Id_vente, Montant, Date_payment)
                        VALUES (?, ?, ?)
                    """, (id_vente, prix_total, today))
                    conn.commit()

                    st.session_state.facture = {
                        "id_vente": id_vente,
                        "id_client": id_client,
                        "nb_animaux": nb_animaux,
                        "prix_total": prix_total,
                        "description": description,
                        "date_vente": today
                    }
                    st.success("✅ Vente et paiement enregistrés avec succès.")
                else:
                    st.error(f"❌ Stock insuffisant. Il reste seulement {stock_dispo} poulets.")

# Page de la facture
def page_facture():
    init_facture_session()
    st.title("🧾 Détails de la Facture")
    conn = get_connection()
    ventes_df = pd.read_sql_query("SELECT * FROM Vente", conn)
    vente_id = st.selectbox("Sélectionner la vente", ventes_df["Id_vente"].tolist())

    if vente_id:
        vente = ventes_df[ventes_df["Id_vente"] == vente_id].iloc[0]
        client = pd.read_sql_query(f"SELECT * FROM Client WHERE Id_client = {vente['Id_client']}", conn).iloc[0]

        st.write(f"**Client** : {client['Nom']} {client['Prenom']}")
        st.write(f"**Date de vente** : {vente['Date_vente']}")
        st.write(f"**Nombre d'animaux** : {vente['Nb_animaux']}")
        st.write(f"**Prix total** : {vente['Prix_total']} XAF")
        if vente["Description"]:
            st.write(f"**Description** : {vente['Description']}")

        if st.button("📄 Générer la facture PDF"):
            pdf = generate_facture_pdf(vente, client)
            st.download_button("📥 Télécharger la facture", pdf, file_name=f"facture_{vente_id}.pdf", mime="application/pdf")

# Génération de la facture avec FPDF
def generate_facture_pdf(vente, client):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Facture de Vente", ln=True, align="C")
    pdf.ln(10)
    pdf.cell(100, 10, txt=f"Facture ID : {vente['Id_vente']}", ln=True)
    pdf.cell(100, 10, txt=f"Client : {client['Nom']} {client['Prenom']}", ln=True)
    pdf.cell(100, 10, txt=f"Date : {vente['Date_vente']}", ln=True)
    pdf.cell(100, 10, txt=f"Nombre d'animaux : {vente['Nb_animaux']}", ln=True)
    pdf.cell(100, 10, txt=f"Montant total : {vente['Prix_total']} XAF", ln=True)
    if vente["Description"]:
        pdf.multi_cell(0, 10, txt=f"Description : {vente['Description']}")

    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

# Démarrer l'application
if __name__ == "__main__":
    main()
