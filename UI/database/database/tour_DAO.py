from database.DB_connect import DBConnect


class TourDAO:
    """DAO per l'accesso ai dati delle tabelle 'tour', 'attrazione' e 'tour_attrazione'."""

    def get_tours_by_regione(self, id_regione: str):
        """
        Recupera tutti i tour e le loro attrazioni per una data regione.

        Restituisce un dizionario: {id_tour: oggetto_Tour}
        (dove oggetto_Tour è un DTO con info base + lista attrazioni).

        Assumiamo che il DTO Tour esista e che gli oggetti Attrazione DTO esistano.
        In assenza del DTO, usiamo un dizionario grezzo.
        """
        # Se Tour è un DTO: from model.tour import Tour
        # Se Attrazione è un DTO: from model.attrazione import Attrazione

        conn = DBConnect.get_connection()
        if conn is None:
            return {}

        # Usa un cursore non dictionary per maneggiare l'aggregazione dei dati
        cursor = conn.cursor()

        # Query che recupera: Tour info, Attrazione info, e Calcola il Valore Culturale Totale per Tour.
        # Raggruppiamo per tour per usare GROUP_CONCAT e ottenere le attrazioni in un'unica riga per tour.
        query = """
            SELECT 
                t.id, 
                t.nome, 
                t.durata_giorni, 
                t.costo, 
                GROUP_CONCAT(a.id) AS attrazioni_ids,
                SUM(a.valore_culturale) AS valore_culturale_totale
            FROM tour t
            INNER JOIN tour_attrazione ta ON t.id = ta.id_tour
            INNER JOIN attrazione a ON ta.id_attrazione = a.id
            WHERE t.id_regione = %s
            GROUP BY t.id, t.nome, t.durata_giorni, t.costo
            ORDER BY t.id
        """

        tours = {}
        try:
            cursor.execute(query, (id_regione,))

            for row in cursor:
                # Esempio di mapping grezzo in assenza dei DTO:
                tour_id, nome, durata, costo, attrazioni_ids_str, valore_culturale = row

                tour_data = {
                    "id": tour_id,
                    "nome": nome,
                    "durata_giorni": durata,
                    "costo": costo,
                    "valore_culturale": valore_culturale,
                    # Lista di ID delle attrazioni (per i vincoli)
                    "attrazioni_ids": set(attrazioni_ids_str.split(','))
                }
                tours[tour_id] = tour_data

        except Exception as e:
            print(f"Errore nel recupero dei tour: {e}")

        finally:
            cursor.close()
            conn.close()

        return tours

# Nota: tour_DAO.py non necessita di get_attrazioni_by_tour() o attrazione_DAO.py
# se la query precedente aggrega già tutti i dati necessari in modo efficiente.