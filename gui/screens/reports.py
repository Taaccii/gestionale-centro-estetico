"""
Schermata Report - Statistiche e Incassi
"""
import customtkinter as ctk 
from gui.components.base import BaseScreen, KPICard, DataCard
from gui.theme import COLORS, SIZES, get_font, PAYMENT_ICONS, ICONS
from datetime import date, timedelta
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from cassa.models import Transazione
from anagrafica.models import Dipendente

class ReportsScreen(BaseScreen):
    """Schermata per visualizzare report e statistiche."""
    def __init__(self, parent):
        # Inizializzazione dati e stato PRIMA di super().__init__
        # perché super() chiama _create_layout e _load_data immediatamente
        self.staff_members = []
        self._init_staff_data()
        
        # Stato filtri
        self.current_period = "Mese"
        self.current_staff_id = None
        self.custom_start_date = None
        self.custom_end_date = None

        super().__init__(
            parent,
            title="Report",
            icon=ICONS["reports"],
            button_text="Aggiorna Report", # Pulsante nell'header per uniformità
            search_placeholder="" 
        )

    def _on_add_new(self):
        """Gestisce il click sul pulsante 'Aggiorna Report' nell'header."""
        self._load_data()

    def _init_staff_data(self):
        """Carica i membri dello staff per il filtro."""
        self.staff_members = list(Dipendente.objects.all())
        self.staff_options = ["Tutti"] + [f"{s.nome} {s.cognome}" for s in self.staff_members]

    def _create_layout(self):
        """Override del layout base per i report con toolbar filtri stile Calendario (trasparente)."""
        super()._create_layout()
        
        # Rimuove il pack della lista per inserire i filtri
        self.list_container.pack_forget()

        # --- TOOLBAR FILTRI (Stile Calendario - Trasparente) ---
        self.filter_toolbar = ctk.CTkFrame(self, fg_color="transparent")
        self.filter_toolbar.pack(fill="x", padx=30, pady=(0, 15))

        # Container interno per allineamento orizzontale
        filter_container = ctk.CTkFrame(self.filter_toolbar, fg_color="transparent")
        filter_container.pack(side="left")

        # 1. Filtro Periodo
        period_wrap = ctk.CTkFrame(filter_container, fg_color="transparent")
        period_wrap.pack(side="left", padx=(0, 25)) 
        
        ctk.CTkLabel(
            period_wrap,
            text=f"{ICONS['calendar']} Periodo:",
            font=get_font("small"),
            text_color=COLORS["text_secondary"]
        ).pack(side="left", padx=(0, 10))

        self.period_menu = ctk.CTkOptionMenu(
            period_wrap,
            values=["Oggi", "Settimana", "Mese", "Anno"], 
            command=self._on_period_change,
            width=160, # Allungato
            height=34,
            fg_color=COLORS["bg_card"],
            button_color=COLORS["border"],     
            button_hover_color=COLORS["accent"],
            dynamic_resizing=False,
            text_color=COLORS["text_primary"],
            dropdown_fg_color=COLORS["bg_card"],
            dropdown_hover_color=COLORS["accent"],
            font=get_font("small"),
            dropdown_font=get_font("small")
        )
        self.period_menu.set("Mese")
        self.period_menu.pack(side="left")

        # 2. Filtro Staff
        staff_wrap = ctk.CTkFrame(filter_container, fg_color="transparent")
        staff_wrap.pack(side="left", padx=(0, 25))

        ctk.CTkLabel(
            staff_wrap,
            text=f"{ICONS['staff']} Staff:",
            font=get_font("small"),
            text_color=COLORS["text_secondary"]
        ).pack(side="left", padx=(0, 10))

        self.staff_menu = ctk.CTkOptionMenu(
            staff_wrap,
            values=self.staff_options,
            command=self._on_staff_change,
            width=260, 
            height=34,
            fg_color=COLORS["bg_card"],
            button_color=COLORS["border"],     
            button_hover_color=COLORS["accent"],
            dynamic_resizing=False,
            text_color=COLORS["text_primary"],
            dropdown_fg_color=COLORS["bg_card"],
            dropdown_hover_color=COLORS["accent"],
            font=get_font("small"),
            dropdown_font=get_font("small")
        )
        self.staff_menu.set("Tutti")
        self.staff_menu.pack(side="left")

        # 3. Date (Dal/Al)
        date_wrap = ctk.CTkFrame(filter_container, fg_color="transparent")
        date_wrap.pack(side="left", padx=(0, 15))

        # Dal
        ctk.CTkLabel(
            date_wrap,
            text="Dal:",
            font=get_font("small"),
            text_color=COLORS["text_secondary"]
        ).pack(side="left", padx=(0, 8))
        self.entry_start = ctk.CTkEntry(
            date_wrap, 
            width=120,
            height=34, 
            justify="center", 
            font=get_font("small"),
            fg_color=COLORS["bg_card"],
            border_color=COLORS["border"]
        )
        self.entry_start.pack(side="left", padx=(0, 15))

        # Al
        ctk.CTkLabel(
            date_wrap,
            text="Al:",
            font=get_font("small"),
            text_color=COLORS["text_secondary"]
        ).pack(side="left", padx=(0, 8))
        self.entry_end = ctk.CTkEntry(
            date_wrap, 
            width=120, # Allargato
            height=34, 
            justify="center", 
            font=get_font("small"),
            fg_color=COLORS["bg_card"],
            border_color=COLORS["border"]
        )
        self.entry_end.pack(side="left")

        # Inizializza date
        self._set_range_entries()

        # Ripristina la lista
        self.list_container.pack(fill="both", expand=True, padx=30, pady=(0, 30))

    def _on_period_change(self, value):
        self.current_period = value
        self._set_range_entries()
        self._load_data()

    def _set_range_entries(self):
        """Aggiorna i campi di testo delle date in base al periodo."""
        from datetime import datetime
        start_date, end_date = self._get_active_range(from_entries=False)
        
        self.entry_start.delete(0, "end")
        self.entry_start.insert(0, start_date.strftime("%d/%m/%Y"))
        
        self.entry_end.delete(0, "end")
        self.entry_end.insert(0, end_date.strftime("%d/%m/%Y"))

    def _on_staff_change(self, value):
        if value == "Tutti":
            self.current_staff_id = None
        else:
            for s in self.staff_members:
                if f"{s.nome} {s.cognome}" == value:
                    self.current_staff_id = s.id
                    break
        self._load_data()

    def _get_active_range(self, from_entries=True):
        """Calcola l'intervallo di date basato su entry o periodo."""
        from datetime import datetime
        today = date.today()

        # Se forziamo la lettura dalle entry (es. click su Aggiorna)
        if from_entries:
            try:
                start = datetime.strptime(self.entry_start.get(), "%d/%m/%Y").date()
                end = datetime.strptime(self.entry_end.get(), "%d/%m/%Y").date()
                return start, end
            except:
                pass # Fallback al calcolo periodo se errori

        # Logica calcolo basata sul periodo
        if self.current_period == "Oggi":
            return today, today
        elif self.current_period == "Settimana":
            start = today - timedelta(days=today.weekday())
            return start, start + timedelta(days=6)
        elif self.current_period == "Mese":
            if today.month == 12:
                next_month = today.replace(year=today.year + 1, month=1, day=1)
            else:
                next_month = today.replace(month=today.month + 1, day=1)
            last_day = next_month - timedelta(days=1)
            return today.replace(day=1), last_day
        elif self.current_period == "Anno":
            return today.replace(month=1, day=1), today.replace(month=12, day=31)
            
        return today, today

    def _on_search_change(self, query):
        """La ricerca testuale nei report ora ha meno senso, la lasciamo vuota."""
        pass

    def _load_data(self):
        """Carica i dati per i report ricostruendo il layout."""
        if not hasattr(self, 'list_container'): return
        self.list_container.clear()
        
        start_date, end_date = self._get_active_range()

        # Sezione KPI Incassi
        self.kpi_frame = ctk.CTkFrame(self.list_container, fg_color="transparent")
        self.kpi_frame.pack(fill="x", pady=(0, 20))
        for i in range(4):
            self.kpi_frame.columnconfigure(i, weight=1)

        self._load_income_kpis(start_date, end_date)

        # Sezione Staff (Nuova)
        self.staff_title = ctk.CTkLabel(
            self.list_container,
            text=f"{ICONS['staff']} Incassi per Staff",
            font=get_font("heading"),
            text_color=COLORS["text_primary"]
        )
        self.staff_title.pack(anchor="w", pady=(20, 15))
        self._load_staff_stats(start_date, end_date)

        # Titolo Metodi di Pagamento
        self.payment_title = ctk.CTkLabel(
            self.list_container,
            text=f"{PAYMENT_ICONS['carta']} Incassi per Metodo di Pagamento",
            font=get_font("heading"),
            text_color=COLORS["text_primary"]
        )
        self.payment_title.pack(anchor="w", pady=(20, 15))

        self._load_payment_methods(start_date, end_date)

    def _load_income_kpis(self, start_date, end_date):
        """Carica i KPI degli incassi filtrati."""
        
        # 1. Incasso del periodo selezionato
        incasso_periodo = Transazione.objects.incassi_per_periodo(start_date, end_date, self.current_staff_id)
        kpi1 = KPICard(
            self.kpi_frame,
            title="Incasso nel Periodo",
            value=f"€{incasso_periodo['totale']:.2f}",
            subtitle=f"{incasso_periodo['numero_transazioni']} transazioni",
            color=COLORS["success"]
        )
        kpi1.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        # 2. Incasso Oggi (per riferimento rapido)
        incasso_oggi = Transazione.objects.incassi_giorno()
        kpi2 = KPICard(
            self.kpi_frame,
            title="Oggi (Totale)",
            value=f"€{incasso_oggi['totale']:.2f}",
            subtitle=f"{incasso_oggi['numero_transazioni']} transazioni",
            color=COLORS["accent"]
        )
        kpi2.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        # 3. Incasso Mese Corrente (per riferimento rapido)
        incasso_mese = Transazione.objects.incassi_mese()
        kpi3 = KPICard(
            self.kpi_frame,
            title="Mese Corrente",
            value=f"€{incasso_mese['totale']:.2f}",
            subtitle=f"{incasso_mese['numero_transazioni']} transazioni",
            color=COLORS["warning"]
        )
        kpi3.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")

        # 4. Numero Clienti (Esempio stat extra)
        kpi4 = KPICard(
            self.kpi_frame,
            title="Media Transazione",
            value=f"€{(incasso_periodo['totale'] / incasso_periodo['numero_transazioni']):.2f}" if incasso_periodo['numero_transazioni'] > 0 else "€0.00",
            subtitle="Valore medio scontrino",
            color=COLORS["text_secondary"]
        )
        kpi4.grid(row=0, column=3, padx=5, pady=5, sticky="nsew")


    def _load_payment_methods(self, start_date, end_date):
        """Carica statistiche per metodo di pagamento filtrate."""
        incassi_per_metodo = Transazione.objects.incassi_per_metodo(
            data_inizio=start_date, 
            data_fine=end_date, 
            dipendente_id=self.current_staff_id
        )

        if not incassi_per_metodo:
            lbl = ctk.CTkLabel(self.list_container, text="Nessun dato per i metodi di pagamento.", font=get_font("small"))
            lbl.pack(pady=10)
            return

        for metodo in incassi_per_metodo:
            metodo_nome = metodo['metodo_pagamento'] or "altro"
            self._create_payment_row(
                metodo_nome,
                metodo['totale'],
                metodo['numero'],
                PAYMENT_ICONS.get(metodo_nome.lower(), PAYMENT_ICONS['altro'])
            )

    def _load_staff_stats(self, start_date, end_date):
        """Carica le statistiche per ogni membro dello staff."""
        incassi_staff = Transazione.objects.incassi_per_staff(start_date, end_date)
        
        if not incassi_staff:
            lbl = ctk.CTkLabel(self.list_container, text="Nessun dato per lo staff nel periodo selezionato.", font=get_font("small"))
            lbl.pack(pady=10)
            return

        for s in incassi_staff:
            nome_val = s['appuntamento__dipendente__nome']
            cognome_val = s['appuntamento__dipendente__cognome']
            
            if nome_val and cognome_val:
                nome_completo = f"{nome_val} {cognome_val}"
            elif nome_val or cognome_val:
                nome_completo = nome_val or cognome_val
            else:
                nome_completo = "Vendita Manuale / Nessun Dipendente"

            card = DataCard(self.list_container)
            card.pack(fill="x", pady=5)
            card.add_title(nome_completo)
            card.add_detail_row(
                f"Appuntamenti completati: {s['numero']}",
                f"€{s['totale']:.2f}",
                right_color=COLORS["accent"]
            )

    def _create_payment_row(self, metodo, totale, conteggio, icon):
        """Crea una card per metodo di pagamento"""
        card = DataCard(self.list_container)
        card.pack(fill="x", pady=5)

        card.add_title(f"{icon} {metodo.capitalize()}")
        card.add_detail_row(
            f"Numero transazioni: {conteggio}",
            f"€{totale:.2f}",
            right_color=COLORS["success"]
        )



