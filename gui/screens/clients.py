"""
Schermata Gestione Clienti
"""

from gui.theme import COLORS, ICONS
import customtkinter as ctk
from gui.components.base import BaseScreen, DataCard
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from anagrafica.models import Cliente
from gui.forms.client_form import ClientFormDialog
from gui.forms.client_details import ClientDetailsDialog

class ClientsScreen(BaseScreen):
    """Schermata per visualizzare e gestire i clienti."""


    def __init__(self, parent):
        super().__init__(
            parent,
            title="Clienti",
            icon=ICONS["clients"],
            button_text="+ Nuovo Cliente",
            search_placeholder="Cerca per nome, cognome o telefono..."
        )

    def _load_data(self):
        """Carica i clienti dal database con supporto al filtraggio."""
        self.list_container.clear()
        
        # Base query
        clienti = Cliente.objects.all()

        # Applica filtro ricerca se presente
        if self.search_query:
            from django.db.models import Q
            q = self.search_query
            clienti = clienti.filter(
                Q(nome__icontains=q) | 
                Q(cognome__icontains=q) | 
                Q(telefono__icontains=q)
            )
        
        if not clienti:
            msg = "Nessun cliente trovato."
            if self.search_query:
                msg = f"Nessun risultato per '{self.search_query}'"
            
            self.list_container.show_empty_message(msg)
            return
        # Logica con smart labels
        counts = {}
        for c in clienti:
            key = f"{c.nome} {c.cognome}"
            counts[key] = counts.get(key, 0) +1

        for c in clienti:
            full_name = f"{c.nome} {c.cognome}"

            # Titolo dinamico
            if counts[full_name] > 1:
                tipo = c.note if c.note else f"ID {c.id}"
                titolo_smart = f"{full_name} ({tipo})"
            else:
                titolo_smart = full_name

            # Passa il titolo calcolato alla funzione
            self._create_client_card(c, titolo_override=titolo_smart)


    def _create_client_card(self, cliente, titolo_override=None):
        """Crea una card per un cliente e usa titolo_override se c'è cliente omonimo."""
        card = DataCard(self.list_container)
        card.pack(fill="x", pady=5)

        # Usa il titolo_override se passatto altrimenti quello standard
        titolo = titolo_override if titolo_override else f"{cliente.nome} {cliente.cognome}"

        card.add_title(titolo)
        card.add_detail(f"{ICONS['calendar']} Cliente dal: {cliente.data_iscrizione}")
        card.add_detail(f"{ICONS['phone']} {cliente.telefono or 'N/D'} •  {ICONS['email']} {cliente.email or 'N/D'}")

        # Click sulla card per vedere lo storico
        card.bind_click(lambda c=cliente: self._on_show_history(c))

    def _on_show_history(self, cliente):
        """Apre il dialogo dello storico per il cliente selezionato."""
        dialog = ClientDetailsDialog(self, cliente)
        # Non serve aspettare il risultato perché è solo visualizzazione

        
    def _on_add_new(self):
        """Override: gestisce click su Nuovo cliente."""

        # Apre il form
        form = ClientFormDialog(self)
        
        # Aspetta che il popup si chiuda
        self.wait_window(form)

        # Se salvato, ricarica la lista
        if form.result:
            self._load_data()