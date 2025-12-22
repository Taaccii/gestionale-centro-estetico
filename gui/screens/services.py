"""
Schermata Gestione Servizi
"""

from gui.forms.service_form import ServiceFormDialog
import django
import customtkinter as ctk
from gui.components.base import BaseScreen, DataCard
from gui.theme import COLORS, ICONS
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from servizi.models import Servizio

class ServicesScreen(BaseScreen):
    """Schermata per visualizzare e gestire i servizi."""

    def __init__(self, parent):
        # Chiama BaseScreen con titolo, icona e testo pulsante
        super().__init__(parent,
        title="Servizi",
        icon=ICONS["services"],
        button_text="+ Nuovo Servizio"
    )
    

    def _load_data(self):
        """Carica i servizi dal database."""
        # Pulisce la lista esistente
        self.list_container.clear()

        # Carica i servizi con filtro
        if self.search_query:
            servizi = Servizio.objects.filter(nome__icontains=self.search_query)
        else:
            servizi = Servizio.objects.all()

        if not servizi:
            # Messaggio se non ci sono servizi
            self.list_container.show_empty_message(
                "Nessun servizio trovato.\nClicca '+ Nuovo Servizio' per aggiungerne uno"
            )
            return

        # Crea una card per ogni servizio
        for servizio in servizi:
            self._create_service_card(servizio)
    

    def _create_service_card(self, servizio):
        """Crea una card per un servizio (Ultra Compatta)."""
        card = DataCard(self.list_container)
        card.pack(fill="x", pady=5) # Distanza equilibrata tra card

        # Titolo
        card.add_title(servizio.nome)

        # Riga unica: Dettagli (Sinistra) + Stato (Destra)
        dettagli = f"{ICONS['time']} {servizio.durata_minuti} min  •  {ICONS['cash']} €{servizio.prezzo}"
        stato_text = "✓ Attivo" if servizio.attivo else "✗ Disattivo"
        stato_color = COLORS["success"] if servizio.attivo else COLORS["error"]
        
        card.add_detail_row(dettagli, stato_text, right_color=stato_color)

        # Click sulla card per modifica
        card.bind_click(lambda s=servizio: self._on_edit_service(s))

    def _on_edit_service(self, servizio):
        """Apre il form di modifica per un servizio."""
        form = ServiceFormDialog(self, service=servizio)
        self.wait_window(form)
        if form.result:
            self._load_data()

    def _on_add_new(self):
        """Gestisce il click su Nuovo Servizio."""
        
         # Apre il form
        form = ServiceFormDialog(self)
        
        # Aspetta che il popup si chiuda
        self.wait_window(form)

        # Se salvato, ricarica la lista
        if form.result:
            self._load_data()

