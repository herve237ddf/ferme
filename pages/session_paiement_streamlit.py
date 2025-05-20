
import streamlit as st
import sqlite3
from datetime import datetime

# Connexion à la base de données
conn = sqlite3.connect("pressing.db")
cursor = conn.cursor()

# Créer la table Paiement si elle n'existe pas
cursor.execute("""
CREATE TABLE IF NOT EXISTS Paiement (
    id_paiement INTEGER PRIMARY KEY AUTOINCREMENT,
    id_commande INTEGER,
    montant REAL NOT NULL,
    date_paiement TEXT NOT NULL,
    mode_paiement TEXT,
    FOREIGN KEY (id_commande) REFERENCES Commande(id_commande)
)
""")
conn.commit()

st.title("💳 Paiement et Facturation")

# Rechercher une commande
st.subheader("Rechercher une commande")
id_commande = st.number_input("Entrer l'identifiant de la commande", min_value=1, step=1)

if st.button("Rechercher la commande"):
    cursor.execute("SELECT * FROM Commande WHERE id_commande = ?", (id_commande,))
    commande = cursor.fetchone()
    if commande:
        st.success("Commande trouvée")
        st.write("ID Commande :", commande[0])
        st.write("ID Client :", commande[1])
        st.write("Date de commande :", commande[2])
        st.write("Montant total :", commande[3])
        st.write("Statut :", commande[4])

        st.subheader("Enregistrer le paiement")
        montant = commande[3]
        mode = st.selectbox("Mode de paiement", ["Espèces", "Orange Money", "Mobile Money", "Carte Bancaire"])
        if st.button("Valider le paiement"):
            date_paiement = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("INSERT INTO Paiement (id_commande, montant, date_paiement, mode_paiement) VALUES (?, ?, ?, ?)",
                           (id_commande, montant, date_paiement, mode))
            conn.commit()
            st.success("Paiement enregistré avec succès.")

            st.subheader("🧾 Facture")
            st.write(f"Facture pour la commande #{id_commande}")
            st.write("Date de paiement :", date_paiement)
            st.write("Montant payé :", montant)
            st.write("Mode de paiement :", mode)
    else:
        st.error("Commande non trouvée.")

conn.close()
