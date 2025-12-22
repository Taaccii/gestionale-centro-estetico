"""
Dashboard - Panoramica del Centro Estetico
"""
import customtkinter as ctk 
from gui.components.base import ScreenHeader, DataCard, KPICard
from gui.theme import COLORS, SIZES, ICONS, get_font
from datetime import date

import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from appuntamenti.models import Appuntamento
from anagrafica.models import Cliente, Dipendente
from servizi.models import Servizio
from cassa.models import Transazione

from gui.components.base import BaseScreen, ScreenHeader, DataCard, KPICard

class DashboardScreen(BaseScreen):
    """Dashboard con KPI e panoramica del centro."""

    def __init__(self, parent):
        super().__init__(
            parent, 
            title="Dashboard", 
            icon=ICONS["dashboard"]
        )

    def _create_layout(self):
        """Override del layout base per inserire la struttura dashboard tra header e footer."""
        super()._create_layout()
        
        # Rimuove la lista standard di BaseScreen per usare il layout dashboard
        self.list_container.pack_forget()

        # Container principale scrollabile
        self.main_container = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent"
        )
        self.main_container.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        # Riga KPI principali
        self.kpi_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.kpi_frame.pack(fill="x", pady=(0, 20))

        # Configurazione griglia 4 colonne per i KPI
        for i in range(4):
            self.kpi_frame.columnconfigure(i, weight=1)

        # Sezione Appuntamenti di oggi
        self.appointments_frame = ctk.CTkFrame(
            self.main_container,
            fg_color=COLORS["bg_card"],
            corner_radius=SIZES["corner_radius"]
        )
        self.appointments_frame.pack(fill="x", pady=(0, 20))

    def _load_data(self):
        """Carica i dati per la dashboard."""
        # Pulisce i container prima di ricaricare
        for child in self.kpi_frame.winfo_children():
            child.destroy()
        for child in self.appointments_frame.winfo_children():
            child.destroy()
            
        self._load_kpis()
        self._load_today_appointments()

    def _load_kpis(self):
        """Carica i KPI principali."""
        today = date.today()

        # Incasso di oggi
        incasso = Transazione.objects.incassi_giorno(today)
        kpi1 = KPICard(
            self.kpi_frame,
            title="Incasso di Oggi",
            value=f"€{incasso['totale']:.2f}",
            subtitle=f"{incasso['numero_transazioni']} transazioni",
            color=COLORS["success"]
        )
        kpi1.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # Appuntamenti di oggi ( conteggio )
        appuntamenti_oggi = Appuntamento.objects.filter(
            data_ora_inizio__date=today,
            stato__in=['prenotato', 'in_corso']
        ).count()
        
        kpi2 = KPICard(
            self.kpi_frame,
            title="Appuntamenti di Oggi",
            value=str(appuntamenti_oggi),
            subtitle="da completare",
            color=COLORS["accent"]
        )
        kpi2.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        # Clienti totali
        clienti = Cliente.objects.count()
        kpi3 = KPICard(
            self.kpi_frame,
            title="Clienti Totali",
            value=str(clienti),
            subtitle="registrati",
            color=COLORS["text_primary"]
        )
        kpi3.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")

        # Incasso settimana
        incasso_settimana = Transazione.objects.incassi_settimana()
        kpi4 = KPICard(
            self.kpi_frame,
            title="Incasso della Settimana",
            value=f"€{incasso_settimana['totale']:.2f}",
            subtitle=f"{incasso_settimana['numero_transazioni']} transazioni",
            color=COLORS["warning"]
        )
        kpi4.grid(row=0, column=3, padx=5, pady=5, sticky="nsew")

    def _load_today_appointments(self):
        """Carica gli appuntamenti di oggi"""
        today = date.today()

        # Titolo sezione
        title = ctk.CTkLabel(
            self.appointments_frame,
            text=f"{ICONS['calendar']} Appuntamenti di Oggi",
            font=get_font("heading"),
            text_color=COLORS["text_primary"]
        )
        title.pack(anchor="w", padx=20, pady=(20, 10))

        # Lista appuntamenti ( i prossimi 5 appuntamenti di oggi )
        appuntamenti = Appuntamento.objects.filter(
            data_ora_inizio__date=today
        ).order_by('data_ora_inizio')[:5] # Massimo 5 appuntamenti

        if not appuntamenti:
            empty = ctk.CTkLabel(
                self.appointments_frame,
                text="Nessun appuntamento per oggi",
                font=get_font("body"),
                text_color=COLORS["text_secondary"]
            )
            empty.pack(anchor='w', padx=20, pady=(0, 20))
            return
        
        for app in appuntamenti:
            self._create_appointment_row(app)

    def _create_appointment_row(self, appuntamento):
        """Crea una riga per un appuntamento usando il componente standard DataCard."""
        card = DataCard(self.appointments_frame)
        card.pack(fill="x", pady=5)
        
        # Recupera i servizi
        nome_servizi = [d.servizio.nome for d in appuntamento.dettagli.all()]
        servizi_str = ", ".join(nome_servizi) if nome_servizi else "Nessun Servizio"

        # Ora
        ora = appuntamento.data_ora_inizio.strftime("%H:%M")

        # Titolo: Cliente
        card.add_title(str(appuntamento.cliente))
        
        # Dettaglio 1: Ora e Staff
        card.add_detail(f"{ICONS['calendar']} {ora}  •  {ICONS['staff']} {appuntamento.dipendente.nome}")
        
        # Dettaglio 2: Servizi e Stato
        stato_colors = {
            'prenotato': COLORS["warning"],
            'in_corso': COLORS["accent"],
            'completato': COLORS['success'],
            'annullato': COLORS['error']
        }
        
        card.add_detail_row(
            f"{ICONS['services']} {servizi_str}",
            appuntamento.stato.upper(),
            right_color=stato_colors.get(appuntamento.stato, COLORS["text_secondary"])
        )

        # Rende la card cliccabile (e tutti i suoi figli)
        card.bind_click(lambda a=appuntamento: self._on_appointment_click(a))

    def _on_appointment_click(self, appuntamento):
        """Apre il form di modifica per l'appuntamento selezionato."""
        from gui.forms.appointment_form import AppointmentFormDialog
        dialog = AppointmentFormDialog(self, appointment=appuntamento)
        self.wait_window(dialog)
        if dialog.result:
            self._load_data()




