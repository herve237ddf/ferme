import streamlit as st
from datetime import datetime, date
from utils.database import get_connection

#st.set_page_config(page_title="Ajouter une Dépense")
st.title("💸 Ajouter une Dépense")

conn = get_connection()
cursor = conn.cursor()

# Variables de session
if "form_data" not in st.session_state:
    st.session_state.form_data = None
if "confirmation" not in st.session_state:
    st.session_state.confirmation = False

if not st.session_state.confirmation:
    with st.form("form_depense"):
        st.write("Veuillez entrer les détails de la dépense :")

        type_depense = st.selectbox("Type de dépense", ["Alimentation", "Aménagement", "Soins", "Achat d'animaux", "Main d'œuvre"])
        montant = st.number_input("Montant", min_value=0, step=100)
        date_depense = st.date_input("Date de la dépense", value=datetime.today().date())
        description = st.text_area("Description (optionnelle)")

        submitted = st.form_submit_button("Enregistrer la dépense")

        if submitted:
            st.session_state.form_data = {
                "type_depense": type_depense,
                "montant": montant,
                "date_depense": date_depense.strftime('%Y-%m-%d'),
                "description": description
            }
            st.session_state.confirmation = True
            st.rerun()

else:
    data = st.session_state.form_data
    st.write("### Confirmez les informations suivantes avant d'enregistrer :")
    st.markdown(f"- **Type de dépense** : {data['type_depense']}")
    st.markdown(f"- **Montant** : {data['montant']} FCFA")
    st.markdown(f"- **Date de la dépense** : {data['date_depense']}")
    st.markdown(f"- **Description** : {data['description'] if data['description'] else 'Aucune'}")

    # Si type = Achat d'animaux, on demande la quantité
    quantite_animaux = None
    if data["type_depense"] == "Achat d'animaux":
        st.title("Ajouter au stock")
        quantite_animaux = st.number_input("Quantité de poulets à ajouter au stock", min_value=1, step=1)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Confirmer"):
            try:
                # Enregistrement de la dépense
                cursor.execute("""
                    INSERT INTO Depense (Type_depense, Montant, Date, Description)
                    VALUES (?, ?, ?, ?)
                """, (data['type_depense'], data['montant'], data['date_depense'], data['description']))
                conn.commit()

                # Ajout au stock si c'est un achat d'animaux
                if data["type_depense"] == "Achat d'animaux" and quantite_animaux:
                    today = date.today()
                    cursor.execute(
                        "INSERT INTO Animaux (quantite, date_ajout) VALUES (?, ?)",
                        (quantite_animaux, today.strftime('%Y-%m-%d'))
                    )
                    conn.commit()
                    st.success(f"✅ {quantite_animaux} poulet(s) ajouté(s) au stock avec succès !")

                st.success("✅ Dépense enregistrée avec succès !")
            except Exception as e:
                st.error(f"❌ Erreur lors de l'enregistrement : {e}")

            # Réinitialisation
            st.session_state.form_data = None
            st.session_state.confirmation = False
            st.rerun()

    with col2:
        if st.button("❌ Annuler"):
            st.info("Enregistrement annulé.")
            st.session_state.form_data = None
            st.session_state.confirmation = False
            st.experimental_rerun()

# Pied de page
st.markdown("---")
st.markdown("© 2025 NovaSolution – L'innovation au service de votre réussite.")
