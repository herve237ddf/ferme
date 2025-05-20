import streamlit as st
import pandas as pd
import plotly.express as px
from utils.kpi import get_kpis
from utils.database import get_connection

st.set_page_config(page_title="Tableau de Bord Ferme", layout="wide")
st.title("🐓 Tableau de bord - Gestion de la Ferme")



# --- Authentification simple ---
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["app_password"]:
            st.session_state["password_correct"] = True
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Mot de passe :", type="password", on_change=password_entered, key="password")
        st.stop()
    elif not st.session_state["password_correct"]:
        st.text_input("Mot de passe :", type="password", on_change=password_entered, key="password")
        st.error("Mot de passe incorrect")
        st.stop()

# check_password()

# Récupération des KPIs
conn = get_connection()
kpis = get_kpis(conn)

col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("💰 Budget (FCFA)", f"{kpis['budget']} ")
col2.metric("🐔 Stock total (poulets)", f"{kpis['animaux']} ")
col3.metric("👥 Clients", f"{kpis['clients']}")
col4.metric("📉 Dépenses (FCFA)", f"{kpis['depenses']} ")
# KPI : Recette des ventes
try:
    recette_query = "SELECT SUM(Montant) FROM Payment"
    recette_data = pd.read_sql_query(recette_query, conn)
    recette = recette_data.iloc[0, 0] if not recette_data.empty and recette_data.iloc[0, 0] else 0
    col6.metric(label="💸 Recette des ventes (FCFA)", value=f"{recette:,.0f}")
except Exception as e:
    col6.warning(f"Impossible d'afficher la recette : {e}")

# Vérification du budget actuel
budget_query = "SELECT SUM(Montant) as Montant, MAX(Date_fin) as Date_limite FROM Budget"
budget_data = pd.read_sql_query(budget_query, conn)

if not budget_data.empty and budget_data["Montant"][0]:
    budget_total = budget_data["Montant"][0]
    date_limite = pd.to_datetime(budget_data["Date_limite"][0])

    # Calcul des dépenses totales actuelles
    depense_totale_query = "SELECT SUM(Montant) as Total_depense FROM Depense"
    depense_data = pd.read_sql_query(depense_totale_query, conn)
    total_depense = depense_data["Total_depense"][0] if depense_data["Total_depense"][0] else 0
    reste_budget = budget_total - total_depense
    col5.metric("💰 Reste du budget (FCFA)", f"{reste_budget}")
    
    #st.write("Budget Actuel", f"Montant total : {budget_total} FCFA\nDépenses totales : {total_depense} FCFA\nReste : {reste_budget} FCFA")
    #st.write(f"Date limite : {date_limite.strftime('%d/%m/%Y')}")
    if pd.Timestamp.now() < date_limite:
        if total_depense > budget_total:
            st.error("🚨 Attention : Vous avez dépassé le budget défini alors que la période est encore en cours.")
        elif reste_budget < 10000:
            st.warning(f"⚠️ Alerte : Il ne reste que {reste_budget} FCFA dans le budget actuel.")
else:
    st.info("ℹ️ Aucun budget actif défini pour le moment.")

st.markdown("---")

# Graphiques (placeholder)
st.subheader("🌐 Graphiques")
col1, col2 = st.columns(2)

# Exemple de graphique ventes
# df_ventes = pd.read_sql("SELECT Date_vente, Prix_total FROM Vente", conn)
# df_ventes['Date_vente'] = pd.to_datetime(df_ventes['Date_vente'])
# fig1 = px.line(df_ventes, x='Date_vente', y='Prix_total', title="Évolution des ventes")
# col1.plotly_chart(fig1, use_container_width=True)

# Boutons d'actions rapides
st.subheader("Actions rapides")
col1, col2, col3, col4 = st.columns(4)
col1.page_link("pages/ajout_budget.py", label="Ajouter un budget", icon="💰")
col2.page_link("pages/ajout_stock.py", label="Ajouter un stock", icon="➕")
col3.page_link("pages/enregistrer_vente.py", label="Enregistrer une vente", icon="🚪")
col4.page_link("pages/ajout_depense.py", label="Ajouter une dépense", icon="💸")

# Récupérer les dépenses par type et calculer le total pour chaque type
query = """
    SELECT Type_depense, SUM(Montant) AS Montant_total
    FROM Depense
    GROUP BY Type_depense
"""
df_depenses = pd.read_sql_query(query, conn)

# Afficher le tableau des dépenses par type
if not df_depenses.empty:
    st.subheader("Dépenses par Type")
    st.dataframe(df_depenses)
else:
    st.warning("Aucune dépense enregistrée pour l'instant.")

# Historique des dépenses
st.subheader("Historique des Dépenses")
historique_depenses = pd.read_sql_query("SELECT * FROM Depense", conn)
st.dataframe(historique_depenses)

# Section : Montant total des achats par client
st.subheader("📊 Clients - Montant total des achats")

query_clients = """
    SELECT 
        Client.Id_client,
        Client.Nom || ' ' || Client.Prenom AS Nom_Complet,
        SUM(Vente.Prix_total) AS Total_achat
    FROM 
        Client
    JOIN 
        Vente ON Client.Id_client = Vente.Id_client
    GROUP BY 
        Client.Id_client
    ORDER BY 
        Total_achat DESC
"""
df_clients_achat = pd.read_sql_query(query_clients, conn)

if not df_clients_achat.empty:
    st.dataframe(df_clients_achat, use_container_width=True)
else:
    st.info("Aucun achat enregistré pour le moment.")

st.markdown("---")
st.subheader("🧹 Réinitialisation de la base de données")

if "confirm_reset" not in st.session_state:
    st.session_state.confirm_reset = False

if not st.session_state.confirm_reset:
    if st.button("🗑️ Réinitialiser toutes les données"):
        st.session_state.confirm_reset = True
        st.warning("⚠️ Êtes-vous sûr de vouloir effacer toutes les données ? Cette action est irréversible.")
        st.button("❌ Annuler", on_click=lambda: st.session_state.update({"confirm_reset": False}))
        st.button("✅ Confirmer la suppression", key="confirm_reset_db")
else:
    st.warning("⚠️ Êtes-vous sûr de vouloir effacer toutes les données ? Cette action est irréversible.")
    if st.button("✅ Confirmer la suppression", key="confirm_reset_db"):
        try:
            with conn:
                conn.execute("DELETE FROM Vente")
                conn.execute("DELETE FROM Depense")
                conn.execute("DELETE FROM Budget")
                conn.execute("DELETE FROM Payment")
                conn.execute("DELETE FROM Client")
                conn.execute("DELETE FROM Animaux")
                # Ajoute d'autres tables ici si nécessaire
            st.success("✅ Toutes les données ont été supprimées avec succès.")
        except Exception as e:
            st.error(f"❌ Une erreur est survenue : {e}")
        finally:
            st.session_state.confirm_reset = False

    st.button("❌ Annuler", on_click=lambda: st.session_state.update({"confirm_reset": False}))
    st.session_state.confirm_reset = False

# Pied de page
st.markdown("---")
st.markdown("© 2025 NovaSolution – L'innovation au service de votre réussite.")    