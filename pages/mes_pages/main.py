import streamlit as st
import pandas as pd
import plotly.express as px
from utils.kpi import get_kpis
from utils.database import get_connection



# Style CSS pour centrer le contenu sur 80% de la page + styles KPI
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
  <div class="kpi-title"><span class="kpi-emoji">🐔</span>Stock total</div>
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

st.markdown("--------")

# gestion des donnees 

st.title("📁 Gestion des Données")
st.markdown("Gérez les enregistrements de la base de données (🔎 recherche, ✏️ modification, 🗑️ suppression).")

# Dictionnaire des tables disponibles
tables = {
    "Clients": "Client",
    "Dépenses": "Depense",
    "Ventes": "Vente",
    "Paiements": "Payment",
    "Budgets": "Budget",
    "Stock Animaux": "Animaux"
}

selected_label = st.selectbox("📂 Choisissez la table à gérer :", list(tables.keys()))
selected_table = tables[selected_label]

# Charger la table 
try:
    df = pd.read_sql_query(f"SELECT * FROM {selected_table}", conn)
except Exception as e:
    st.error(f"Erreur lors du chargement de la table : {e}")
    st.stop()

# Zone de recherche
search_input = st.text_input("🔎 Rechercher (nom, ID, etc.)", "")
if search_input:
    df_filtered = df[df.apply(lambda row: row.astype(str).str.contains(search_input, case=False).any(), axis=1)]
else:
    df_filtered = df.copy()

# Affichage des enregistrements filtrés
st.markdown("### 📋 Enregistrements disponibles")

if not df_filtered.empty:
    selected_index = st.selectbox(
        "Sélectionnez une ligne :",
        df_filtered.index,
        format_func=lambda i: f"ID {df_filtered.iloc[i, 0]} - {df_filtered.iloc[i].to_dict()}"
    )
    selected_row = df_filtered.loc[selected_index]
    st.dataframe(pd.DataFrame([selected_row]), use_container_width=True)

    # Formulaire de modification
    st.markdown("### ✏️ Modifier les données")
    primary_key = df.columns[0]
    st.write(primary_key)
    updated_values = {}

    with st.form("update_form"):
        for col in df.columns:
            if col == primary_key:
                st.text_input(f"{col} (clé primaire)", value=(selected_row[col]), disabled=True, key=f"{col}_disabled")
            else:
                updated_values[col] = st.text_input(col, value=str(selected_row[col]), key=f"{col}_update")
        submit_modif = st.form_submit_button("✅ Appliquer les modifications")

    if submit_modif:
        try:
            primary_key_value = int(selected_row[primary_key])  # force le type selon besoin
            set_clause = ", ".join([f"{col} = ?" for col in updated_values.keys()])
            values = list(updated_values.values()) + [primary_key_value]
            query = f"UPDATE {selected_table} SET {set_clause} WHERE {primary_key} = ?"
            
            st.code(query)
            st.write("Valeurs :", values)

            cursor = conn.cursor()
            cursor.execute(query, values)
            conn.commit()

            if cursor.rowcount > 0:
                st.success("✅ Modification enregistrée avec succès.")
                st.rerun()
            else:
                st.warning("⚠️ Aucune ligne modifiée. Clé ou valeurs inchangées.")
        except Exception as e:
            st.error(f"❌ Erreur lors de la mise à jour : {e}")

# Suppression avec confirmation
st.markdown("---")
st.markdown("### 🗑️ Supprimer cet enregistrement")

if st.checkbox("⚠️ Je confirme vouloir supprimer cette ligne."):
    if st.button("🚨 Supprimer définitivement"):
        try:
            # Forcer un type standard (int ou str) selon ce que la BDD attend
            primary_key_value = selected_row[primary_key]
            if isinstance(primary_key_value, (pd._libs.missing.NAType, type(None))):
                raise ValueError("Clé primaire invalide ou manquante.")
            if isinstance(primary_key_value, (pd.Series, pd.DataFrame, list)):
                raise ValueError("Clé primaire mal formatée.")
            
            # Forcer le type vers int si possible, sinon laisser str
            try:
                primary_key_value = int(primary_key_value)
            except:
                primary_key_value = str(primary_key_value)

            cursor = conn.cursor()
            delete_query = f"DELETE FROM {selected_table} WHERE {primary_key} = ?"
            st.code(delete_query)
            st.write("Valeur utilisée :", primary_key_value)

            cursor.execute(delete_query, (primary_key_value,))
            conn.commit()

            if cursor.rowcount > 0:
                st.success("✅ Ligne supprimée avec succès.")
                st.rerun()
            else:
                st.warning("❗Aucune ligne supprimée. Vérifie la clé primaire.")
        except Exception as e:
            st.error(f"❌ Erreur lors de la suppression : {e}")


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
