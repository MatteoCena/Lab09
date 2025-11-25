from database.regione_DAO import RegioneDAO
from database.tour_DAO import TourDAO


class Model:
    def __init__(self):
        self._regione_dao = RegioneDAO()
        self._tour_dao = TourDAO()

        # Cache per i tour di una regione
        self.tours_regione = {}

        # Variabili globali per la ricorsione e il backtracking
        self.best_valore_culturale = -1
        self.best_pacchetto_ids = []
        self.all_tours_list = []  # Lista piatta di tour per accesso ricorsivo

    # --- 1. Interfaccia Dati ---

    def get_all_regioni(self):
        """Restituisce le regioni per popolare il Dropdown (Controller -> View)."""
        return self._regione_dao.get_all_regioni()

    def get_tours_della_regione(self, id_regione: str):
        """Carica i tour e li formatta internamente (chiamato una volta per regione)."""
        if id_regione not in self.tours_regione:
            # {id_tour: tour_data_dict}
            self.tours_regione[id_regione] = self._tour_dao.get_tours_by_regione(id_regione)

        # Converte il dizionario in una lista per l'accesso ricorsivo basato sull'indice
        self.all_tours_list = list(self.tours_regione[id_regione].values())
        return self.all_tours_list

    # --- 2. Algoritmo Ricorsivo ---

    def _ricorsione_pacchetto(self, level, durata_corrente, costo_corrente, valore_corrente, attrazioni_usate,
                              pacchetto_corrente_ids, durata_max, budget_max):
        """
        Algoritmo ricorsivo con backtracking per massimizzare il valore culturale.

        :param level: Indice del tour da considerare nella lista self.all_tours_list.
        :param durata_corrente, costo_corrente, valore_corrente: Stato attuale del pacchetto.
        :param attrazioni_usate: Set di ID delle attrazioni già incluse (vincolo duplicato).
        :param pacchetto_corrente_ids: Lista di ID dei tour attualmente selezionati.
        """

        # A. Istruzioni che dovrebbero sempre essere eseguite (Backtracking)
        # Se il pacchetto corrente è migliore del migliore finora trovato, aggiornalo.
        if valore_corrente > self.best_valore_culturale:
            self.best_valore_culturale = valore_corrente
            # Copia la lista per evitare modifiche future
            self.best_pacchetto_ids = pacchetto_corrente_ids[:]

        # B. Condizione Terminale
        # Abbiamo considerato tutti i tour disponibili nella lista
        if level == len(self.all_tours_list):
            return

            # Loop principale: per ogni tour, abbiamo due opzioni (prendere o non prendere)
        current_tour = self.all_tours_list[level]

        # --- Opzione 1: NON includere il tour corrente (Vai al livello successivo) ---
        self._ricorsione_pacchetto(
            level + 1,
            durata_corrente,
            costo_corrente,
            valore_corrente,
            attrazioni_usate,
            pacchetto_corrente_ids,
            durata_max,
            budget_max
        )

        # --- Opzione 2: INCLUDERE il tour corrente (Solo se rispetta i vincoli) ---

        nuova_durata = durata_corrente + current_tour["durata_giorni"]
        nuovo_costo = costo_corrente + current_tour["costo"]

        # C. Vincoli (Filtro prima della ricorsione)

        # 1. Vincolo di Durata
        if nuova_durata <= durata_max:

            # 2. Vincolo di Budget
            if nuovo_costo <= budget_max:

                # 3. Vincolo Attrazioni Duplicate (intersezione tra attrazioni usate e quelle del tour corrente)
                attrazioni_nuove = current_tour["attrazioni_ids"] - attrazioni_usate
                if len(attrazioni_nuove) == len(current_tour["attrazioni_ids"]):
                    # Nessuna attrazione duplicata!

                    # D. Compute Partial (Aggiorna lo stato)
                    nuovo_valore = valore_corrente + current_tour["valore_culturale"]
                    nuove_attrazioni_usate = attrazioni_usate.copy()
                    nuove_attrazioni_usate.update(current_tour["attrazioni_ids"])

                    # E. Ricorsione (Passa al livello successivo)
                    pacchetto_corrente_ids.append(current_tour["id"])

                    self._ricorsione_pacchetto(
                        level + 1,
                        nuova_durata,
                        nuovo_costo,
                        nuovo_valore,
                        nuove_attrazioni_usate,
                        pacchetto_corrente_ids,
                        durata_max,
                        budget_max
                    )

                    # F. Backtracking (Rimuove il tour corrente per permettere altre scelte)
                    pacchetto_corrente_ids.pop()

    def trova_pacchetto_ottimale(self, id_regione: str, durata_max: int, budget_max: float):
        """
        Funzione principale per l'ottimizzazione.

        Restituisce (costo_ottimo, valore_culturale_ottimo, lista_tour_ottimale).
        """

        # 1. Carica e prepara i tour
        self.get_tours_della_regione(id_regione)

        # Reset stato globale
        self.best_valore_culturale = -1
        self.best_pacchetto_ids = []

        # 2. Avvia la ricorsione
        # Assumiamo che la durata e il budget massimo
        # non siano trattati come vincoli se l'utente li lascia vuoti (come da nota bene)

        # Inizio: level=0, stato=0, attrazioni_usate=set(), pacchetto_ids=[]
        self._ricorsione_pacchetto(
            level=0,
            durata_corrente=0,
            costo_corrente=0.0,
            valore_corrente=0,
            attrazioni_usate=set(),
            pacchetto_corrente_ids=[],
            durata_max=durata_max,
            budget_max=budget_max
        )

        # 3. Formatta i risultati

        # Calcola il costo totale e recupera i dettagli del tour finale
        costo_finale = 0.0
        lista_tour_dettagliata = []

        if self.best_valore_culturale > -1:
            for tour_id in self.best_pacchetto_ids:
                tour = self.tours_regione[id_regione].get(tour_id)
                if tour:
                    costo_finale += tour["costo"]
                    lista_tour_dettagliata.append(tour)

        return costo_finale, self.best_valore_culturale, lista_tour_dettagliata