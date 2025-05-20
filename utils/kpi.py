import pandas as pd

def get_kpis(conn):
    cursor = conn.cursor()

    # Budget total (dernier budget enregistré)
    cursor.execute("SELECT COALESCE(MAX(Id_budget), 0) FROM Budget")
    id_budget = cursor.fetchone()[0]
    if id_budget == 0:
        budget = 0
    else:
        cursor.execute("SELECT SUM(Montant) FROM Budget")
        total_budgets = cursor.fetchone()[0]
        cursor.execute("SELECT * FROM Budget ORDER BY Id_budget DESC LIMIT 1")
        budget = total_budgets

    # Stock total
    cursor.execute("""
            SELECT 
                IFNULL((SELECT SUM(Quantite) FROM Animaux), 0) - 
                IFNULL((SELECT SUM(Nb_animaux) FROM Vente), 0) 
            AS Stock_disponible
        """)
    animaux = cursor.fetchone()[0]

    # Nombre de clients
    cursor.execute("SELECT COUNT(*) FROM Client")
    clients = cursor.fetchone()[0]

    # Dépenses totales
    cursor.execute("SELECT COALESCE(SUM(Montant), 0) FROM Depense")
    depenses = cursor.fetchone()[0]

    return {
        'budget': budget,
        'animaux': animaux,
        'clients': clients,
        'depenses': depenses
    }
