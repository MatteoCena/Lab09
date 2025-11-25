from database.DB_connect import DBConnect


class RegioneDAO:
    """DAO per l'accesso ai dati della tabella 'regione'."""

    def get_all_regioni(self):
        """Restituisce una lista di oggetti Regione (o tuple/dizionario) con id e nome."""
        conn = DBConnect.get_connection()
        risultato = []

        if conn is None:
            return risultato

        cursor = conn.cursor(dictionary=True)
        # La query recupera l'ID e il nome di tutte le regioni
        query = "SELECT id, nome FROM regione ORDER BY nome"

        try:
            cursor.execute(query)
            # Ritorna una lista di dizionari: [{'id': 'ABR', 'nome': 'Abruzzo'}, ...]
            risultato = cursor.fetchall()
        except Exception as e:
            print(f"Errore nel recupero delle regioni: {e}")

        finally:
            cursor.close()
            conn.close()

        return risultato