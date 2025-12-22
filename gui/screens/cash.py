"""
Schermata Cassa - Registrazione transazioni e lista transazioni recenti
"""
import customtkinter as ctk 
from gui.components.base import BaseScreen, KPICard, DataCard
from gui.theme import COLORS, SIZES, get_font, PAYMENT_ICONS, ICONS
from datetime import date
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from cassa.models import Transazione
from gui.forms.transaction_form import TransactionFormDialog

class CashScreen(BaseScreen):
    """Schermata che visualizza la cassa e le transazioni"""
    def __init__(self, parent):
        super().__init__(
            parent,
            title="Cassa",
            icon=ICONS["cash"],
            button_text="+ Nuova Transazione",
            search_placeholder="Cerca transazioni..."
        )
    
    def _create_layout(self):
        """Override del layout base per la cassa."""
        super()._create_layout()
        # Il layout viene costruito dinamicamente in _load_data

    def _on_search_change(self, query):
        """Gestisce la ricerca nelle transazioni"""
        self.search_query = query
        self._load_data()

    def _load_data(self):
        """Carica i dati per la cassa ricostruendo il layout."""
        self.list_container.clear()
        
        # Sezione KPI cassa
        self.kpi_frame = ctk.CTkFrame(self.list_container, fg_color="transparent")
        self.kpi_frame.pack(fill="x", pady=(0, 20))
        for i in range(4):
            self.kpi_frame.columnconfigure(i, weight=1)

        self._load_kpis()

        # Sezione Transazioni Recenti (Titolo)
        self.trans_title = ctk.CTkLabel(
            self.list_container,
            text=f"{PAYMENT_ICONS['altro']} Transazioni Recenti",
            font=get_font("heading"),
            text_color=COLORS["text_primary"]
        )
        self.trans_title.pack(anchor="w", pady=(10, 15))

        self._load_transactions()

    def _load_kpis(self):
        """Carica i KPI della cassa."""
        today = date.today()
        
        contanti = Transazione.objects.incassi_giorno_per_metodo(today, 'contanti')
        kpi1 = KPICard(
            self.kpi_frame,
            title=f"{PAYMENT_ICONS['contanti']} Contanti",
            value=f"€{contanti['totale']:.2f}",
            subtitle=f"{contanti['numero_transazioni']} transazioni",
            color=COLORS["success"]
        )
        kpi1.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        carta = Transazione.objects.incassi_giorno_per_metodo(today, 'carta')
        kpi2 = KPICard(
            self.kpi_frame,
            title=f"{PAYMENT_ICONS['carta']} Carta",
            value=f"€{carta['totale']:.2f}",
            subtitle=f"{carta['numero_transazioni']} transazioni",
            color=COLORS["accent"]
        )
        kpi2.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        altro = Transazione.objects.incassi_giorno_per_metodo(today, escludi=['contanti', 'carta'])
        kpi3 = KPICard(
            self.kpi_frame,
            title=f"{PAYMENT_ICONS['bonifico']} Altro",
            value=f"€{altro['totale']:.2f}",
            subtitle=f"{altro['numero_transazioni']} transazioni",
            color=COLORS["warning"]
        )
        kpi3.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")

        totale = Transazione.objects.incassi_giorno_per_metodo(today)
        kpi4 = KPICard(
            self.kpi_frame,
            title=f"{ICONS['dashboard']} Totale",
            value=f"€{totale['totale']:.2f}",
            subtitle=f"{totale['numero_transazioni']} transazioni",
            color=COLORS["text_primary"]
        )
        kpi4.grid(row=0, column=3, padx=5, pady=5, sticky="nsew")
        

    def _load_transactions(self):
        """Carica le transazioni recenti."""
        # Query ultime 10 transazioni con filtro
        today = date.today()
        transazioni = Transazione.objects.filter(data_ora_pagamento__date=today)
        
        if self.search_query:
            from django.db.models import Q
            q = self.search_query
            transazioni = transazioni.filter(
                Q(note__icontains=q) | 
                Q(metodo_pagamento__icontains=q)
            )
            
        transazioni = transazioni.order_by('-data_ora_pagamento')[:10]

        # Gestione lista vuota
        if not transazioni:
            self.list_container.show_empty_message("Nessuna transazione registrata per oggi.")
            return
        
        # Per ogni transazione crea una riga
        for trans in transazioni:
            self._create_transaction_row(trans)

    
    def _create_transaction_row(self, transazione):
        """Crea una card per ogni transazione."""
        card = DataCard(self.list_container)
        card.pack(fill="x", pady=5)

        # Ora
        ora = transazione.data_ora_pagamento.strftime("%H:%M")
        icon = PAYMENT_ICONS.get(transazione.metodo_pagamento, PAYMENT_ICONS['altro'])
        
        # Titolo: Ora + Metodo
        card.add_title(f"{ora}  •  {icon} {transazione.metodo_pagamento.capitalize()}")
        
        # Dettaglio: Note e Importo
        note_text = transazione.note or "Nessuna nota"
        if len(note_text) > 40:
            note_text = note_text[:37] + "..."
            
        card.add_detail_row(
            note_text,
            f"€{transazione.importo_totale:.2f}",
            right_color=COLORS["success"]
        )

    def _on_add_new(self):
        """Apre il form nuova transazione"""
        form = TransactionFormDialog(self)
        self.wait_window(form)
        if form.result:
            self._load_data() # Ricarica tutto (KPI e Lista)

        






        

     


