"""
Schermata Gestione Staff/Dipendenti
"""

from gui.theme import COLORS, ICONS
from gui.components.base import BaseScreen, DataCard
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from anagrafica.models import Dipendente
from gui.forms.staff_form import StaffFormDialog

class StaffScreen(BaseScreen):
    """Schermata per visualizzare e gestire i dipendenti."""


    def __init__(self, parent):
        super().__init__(
            parent,
            title="Staff",
            icon=ICONS["staff"],
            button_text="+ Nuovo Dipendente",
            search_placeholder="Cerca per nome, cognome o ruolo..."
        )

    def _load_data(self):
        """Carica i dipendenti dal database con supporto al filtraggio."""
        self.list_container.clear()

        dipendenti = Dipendente.objects.all()

        # Applica filtro ricerca se presente
        if self.search_query:
            from django.db.models import Q
            q = self.search_query
            dipendenti = dipendenti.filter(
                Q(nome__icontains=q) | 
                Q(cognome__icontains=q) | 
                Q(ruolo__icontains=q)
            )
        
        if not dipendenti:
            msg = "Nessun dipendente trovato."
            if self.search_query:
                msg = f"Nessun risultato per '{self.search_query}'"
            
            self.list_container.show_empty_message(msg)
            return

        for dipendente in dipendenti:
            self._create_staff_card(dipendente)

    def _create_staff_card(self, dipendente):
        """Crea una card per un dipendente."""
        card = DataCard(self.list_container)
        card.pack(fill="x", pady=5)

        card.add_title(f"{dipendente.nome} {dipendente.cognome}")
        card.add_detail(f"👔 {dipendente.ruolo}", color=COLORS['accent'])
        card.add_detail(f"📞 {dipendente.telefono or 'N/D'} •  ✉️ {dipendente.email or 'N/D'}")

        # Click sulla card per modifica
        card.bind_click(lambda d=dipendente: self._on_edit_staff(d))

    def _on_edit_staff(self, dipendente):
        """Apre il form di modifica per un dipendente."""
        from gui.forms.staff_form import StaffFormDialog
        form = StaffFormDialog(self, staff=dipendente)
        self.wait_window(form)
        if form.result:
            self._load_data()

        
    def _on_add_new(self):
        """Override: gestisce click su Nuovo Dipendente."""
        form = StaffFormDialog(self)
        self.wait_window(form)
        if form.result:
            self._load_data()

