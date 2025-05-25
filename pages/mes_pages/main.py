import streamlit as st
import pandas as pd
from utils.kpi import get_kpis
from utils.database import get_connection



# Style CSS styles KPI
st.markdown("""
    <style>
        .main-container {
            max-width: 90%;
            margin: auto;
        }
        .kpi-box {
            background: linear-gradient(135deg, #004080 0%, #0066cc 100%);
            color: white;
            padding: 20px 30px;
            border-radius: 15px;
            box-shadow: 2px 4px 10px rgb(0 70 150 / 0.4);
            text-align: center;
            font-weight: 600;
            margin-bottom: 20px;
            user-select: none;
        }
        .kpi-title {
            font-size: 20px;
            margin-bottom: 5px;
            font-weight: 700;
        }
        .kpi-value {
            font-size: 28px;
        }
        .kpi-emoji {
            font-size: 24px;
            margin-right: 8px;
            vertical-align: middle;
        }
    </style>
    <div class="main-container">
""", unsafe_allow_html=True)

# Titre
st.title("🐓 Tableau de bord - Gestion de la Ferme")

# Connexion à la base de données et récupération des KPI
conn = get_connection()
kpis = get_kpis(conn)

# Calcul reste_budget pour affichage
try:
    budget_query = "SELECT SUM(Montant) as Montant, MAX(Date_fin) as Date_limite FROM Budget"
    budget_data = pd.read_sql_query(budget_query, conn)
    if not budget_data.empty and budget_data["Montant"][0]:
        budget_total = budget_data["Montant"][0]
        date_limite = pd.to_datetime(budget_data["Date_limite"][0])
        depense_totale_query = "SELECT SUM(Montant) as Total_depense FROM Depense"
        depense_data = pd.read_sql_query(depense_totale_query, conn)
        total_depense = depense_data["Total_depense"][0] if depense_data["Total_depense"][0] else 0
        reste_budget = budget_total - total_depense
    else:
        reste_budget = 0
except Exception as e:
    reste_budget = 0

# 1re rangée de 3 colonnes avec KPIs stylisés
col1, col2, col3 = st.columns(3)

col1.markdown(f"""
<div class="kpi-box" style="background: linear-gradient(135deg, #004080 0%, #0066cc 100%); box-shadow: 2px 4px 10px rgba(0, 70, 128, 0.4);">
  <div class="kpi-title"><span class="kpi-emoji">💰</span>Budget (FCFA)</div>
  <div class="kpi-value">{kpis['budget']}</div>
</div>
""", unsafe_allow_html=True)

col2.markdown(f"""
<div class="kpi-box" style="background: linear-gradient(135deg, #cc3300 0%, #ff6600 100%); box-shadow: 2px 4px 10px rgba(204, 51, 0, 0.4);">
  <div class="kpi-title"><span class="kpi-emoji">📉</span>Dépenses (FCFA)</div>
  <div class="kpi-value">{kpis['depenses']}</div>
</div>
""", unsafe_allow_html=True)

col3.markdown(f"""
<div class="kpi-box" style="background: linear-gradient(135deg, #009933 0%, #33cc33 100%); box-shadow: 2px 4px 10px rgba(0, 153, 51, 0.4);">
  <div class="kpi-title"><span class="kpi-emoji">💰</span>Reste du budget (FCFA)</div>
  <div class="kpi-value">{reste_budget}</div>
</div>
""", unsafe_allow_html=True)

# Alertes budget
if 'budget_total' in locals() and 'date_limite' in locals() and 'total_depense' in locals():
    if pd.Timestamp.now() < date_limite:
        if total_depense > budget_total:
            st.error("🚨 Attention : Vous avez dépassé le budget défini alors que la période est encore en cours.")
        elif reste_budget < 10000:
            st.warning(f"⚠️ Alerte : Il ne reste que {reste_budget} FCFA dans le budget actuel.")

st.markdown("---")

# 2e rangée de 3 colonnes avec KPIs stylisés
col4, col5, col6 = st.columns(3)

col4.markdown(f"""
<div class="kpi-box" style="background: linear-gradient(135deg, #663399 0%, #9966cc 100%); box-shadow: 2px 4px 10px rgba(102, 51, 153, 0.4);">
  <div class="kpi-title"><span class="kpi-emoji">🐔</span>Stock total (poulets)</div>
  <div class="kpi-value">{kpis['animaux']}</div>
</div>
""", unsafe_allow_html=True)

col5.markdown(f"""
<div class="kpi-box" style="background: linear-gradient(135deg, #006666 0%, #339999 100%); box-shadow: 2px 4px 10px rgba(0, 102, 102, 0.4);">
  <div class="kpi-title"><span class="kpi-emoji">👥</span>Clients</div>
  <div class="kpi-value">{kpis['clients']}</div>
</div>
""", unsafe_allow_html=True)

# KPI : Recette des ventes
try:
    recette_query = "SELECT SUM(Montant) FROM Payment"
    recette_data = pd.read_sql_query(recette_query, conn)
    recette = recette_data.iloc[0, 0] if not recette_data.empty and recette_data.iloc[0, 0] else 0
except Exception as e:
    recette = 0

col6.markdown(f"""
<div class="kpi-box" style="background: linear-gradient(135deg, #cc9900 0%, #ffcc33 100%); box-shadow: 2px 4px 10px rgba(204, 153, 0, 0.4); color: #333;">
  <div class="kpi-title"><span class="kpi-emoji">💸</span>Recette(FCFA)</div>
  <div class="kpi-value">{recette:,.0f}</div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

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

# Fermeture du bloc .main-container
st.markdown("</div>", unsafe_allow_html=True)
