"""
Schermata Storico Appuntamenti - Riepilogo e Filtri Avanzati
"""
import customtkinter as ctk
from gui.components.base import BaseScreen, DataCard
from gui.theme import COLORS, SIZES, ICONS, get_font
from datetime import date, timedelta
import django
import os
from django.db.models import Q

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from appuntamenti.models import Appuntamento
from anagrafica.models import Cliente, Dipendente

class AppointmentsScreen(BaseScreen):
    """Schermata per visualizzare lo storico completo degli appuntamenti."""

    def __init__(self, parent):
        super().__init__(
            parent,
            title="Storico App.",
            icon=ICONS["history"],
            button_text="+ Nuovo Appuntamento",
            search_placeholder="Cerca per cliente o note..."
        )

    def _create_layout(self):
        """Override del layout per aggiungere la barra dei filtri."""
        super()._create_layout()
        
        # Svuota il pack della lista per inserire i filtri tra header e lista
        self.list_container.pack_forget()

        # Barra Filtri Avanzati
        self.filter_bar = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=SIZES["corner_radius"])
        self.filter_bar.pack(fill="x", pady=(0, 15), padx=30)

        for i in range(4):
            self.filter_bar.columnconfigure(i, weight=1)

        # 1. Filtro Periodo
        filter_period_frame = ctk.CTkFrame(self.filter_bar, fg_color="transparent")
        filter_period_frame.grid(row=0, column=0, padx=15, pady=10, sticky="ew")
        ctk.CTkLabel(filter_period_frame, text="Periodo", font=get_font("small_bold")).pack(anchor="w")
        self.combo_period = ctk.CTkComboBox(
            filter_period_frame, 
            values=["Tutti", "Oggi", "Settimana", "Mese", "Anno"],
            font=get_font("small"),
            command=lambda _: self._load_data()
        )
        self.combo_period.set("Mese")
        self.combo_period.pack(fill="x")

        # 2. Filtro Stato
        filter_status_frame = ctk.CTkFrame(self.filter_bar, fg_color="transparent")
        filter_status_frame.grid(row=0, column=1, padx=15, pady=10, sticky="ew")
        ctk.CTkLabel(filter_status_frame, text="Stato", font=get_font("small_bold")).pack(anchor="w")
        stati = ["Tutti"] + [c[1] for c in Appuntamento.STATO_CHOICES]
        self.combo_status = ctk.CTkComboBox(
            filter_status_frame, 
            values=stati,
            font=get_font("small"),
            command=lambda _: self._load_data()
        )
        self.combo_status.set("Tutti")
        self.combo_status.pack(fill="x")

        # 3. Filtro Staff
        filter_staff_frame = ctk.CTkFrame(self.filter_bar, fg_color="transparent")
        filter_staff_frame.grid(row=0, column=2, padx=15, pady=10, sticky="ew")
        ctk.CTkLabel(filter_staff_frame, text="Staff", font=get_font("small_bold")).pack(anchor="w")
        staff_list = ["Tutti"] + [f"{s.nome} {s.cognome}" for s in Dipendente.objects.all()]
        self.combo_staff = ctk.CTkComboBox(
            filter_staff_frame, 
            values=staff_list,
            font=get_font("small"),
            command=lambda _: self._load_data()
        )
        self.combo_staff.set("Tutti")
        self.combo_staff.pack(fill="x")

        # 4. Riepilogo Totali
        self.stats_frame = ctk.CTkFrame(self.filter_bar, fg_color="transparent")
        self.stats_frame.grid(row=0, column=3, padx=15, pady=10, sticky="ew")
        self.lbl_total_count = ctk.CTkLabel(self.stats_frame, text="Appuntamenti: 0", font=get_font("small_bold"))
        self.lbl_total_count.pack(anchor="w")
        self.lbl_total_price = ctk.CTkLabel(self.stats_frame, text="Totale: € 0.00", font=get_font("body_bold"), text_color=COLORS["success"])
        self.lbl_total_price.pack(anchor="w")

        # Ripristina la lista sotto i filtri
        self.list_container.pack(fill="both", expand=True, padx=30, pady=(0, 30))

    def _load_data(self):
        """Carica gli appuntamenti applicando i filtri."""
        if not hasattr(self, 'list_container'): return
        self.list_container.clear()

        queryset = Appuntamento.objects.all().select_related('cliente', 'dipendente').prefetch_related('dettagli__servizio')

        if self.search_query:
            queryset = queryset.filter(
                Q(cliente__nome__icontains=self.search_query) | 
                Q(cliente__cognome__icontains=self.search_query) |
                Q(note__icontains=self.search_query)
            )

        today = date.today()
        period = self.combo_period.get()
        if period == "Oggi":
            queryset = queryset.filter(data_ora_inizio__date=today)
        elif period == "Settimana":
            start_week = today - timedelta(days=today.weekday())
            queryset = queryset.filter(data_ora_inizio__date__gte=start_week)
        elif period == "Mese":
            queryset = queryset.filter(data_ora_inizio__year=today.year, data_ora_inizio__month=today.month)
        elif period == "Anno":
            queryset = queryset.filter(data_ora_inizio__year=today.year)

        status_label = self.combo_status.get()
        if status_label != "Tutti":
            status_db = [c[0] for c in Appuntamento.STATO_CHOICES if c[1] == status_label][0]
            queryset = queryset.filter(stato=status_db)

        staff_label = self.combo_staff.get()
        if staff_label != "Tutti":
            parts = staff_label.split(" ")
            queryset = queryset.filter(dipendente__nome=parts[0], dipendente__cognome=" ".join(parts[1:]))

        queryset = queryset.order_by('-data_ora_inizio')

        total_count = queryset.count()
        total_price = sum(app.prezzo_totale for app in queryset)
        
        self.lbl_total_count.configure(text=f"Appuntamenti: {total_count}")
        self.lbl_total_price.configure(text=f"Totale: € {total_price:.2f}")

        if not queryset.exists():
            self.list_container.show_empty_message("Nessun appuntamento trovato.")
            return

        for app in queryset:
            self._create_appointment_card(app)

    def _create_appointment_card(self, app):
        card = DataCard(self.list_container)
        card.pack(fill="x", pady=5)

        stato_colors = {'prenotato': COLORS["accent"], 'in_corso': COLORS["warning"], 'completato': COLORS['success'], 'annullato': COLORS['error']}
        data_str = app.data_ora_inizio.strftime("%d/%m/%Y %H:%M")
        card.add_title(f"{app.cliente.nome} {app.cliente.cognome}")
        
        servizi = ", ".join([d.servizio.nome for d in app.dettagli.all()])
        card.add_detail(f"{ICONS['calendar']} {data_str}  •  {ICONS['staff']} {app.dipendente.nome}  •  {ICONS['time']} {app.durata_minuti} min")
        card.add_detail_row(f"✨ {servizi}", f"€{app.prezzo_totale:.2f}", right_color=COLORS["success"])

        stato_desc = [c[1] for c in Appuntamento.STATO_CHOICES]
        # Mappa per trovare l'etichetta dello stato corrente
        current_stato_label = ""
        for choice in Appuntamento.STATO_CHOICES:
            if choice[0] == app.stato:
                current_stato_label = choice[1]
                break

        note = f"  |  {ICONS['notes']} {app.note}" if app.note else ""
        if app.stato == 'annullato' and app.motivo_annullamento:
            note += f"  |  {ICONS['cancel_reason']} Motivo: {app.motivo_annullamento}"
        
        card.add_detail(f"{ICONS['status']} {current_stato_label.upper()}{note}", color=stato_colors.get(app.stato, COLORS["text_secondary"]))
        card.bind("<Button-1>", lambda e, a=app: self._on_edit_click(a))

    def _on_edit_click(self, app):
        from gui.forms.appointment_form import AppointmentFormDialog
        dialog = AppointmentFormDialog(self, appointment=app)
        self.wait_window(dialog)
        self._load_data()

    def _on_add_new(self):
        from gui.forms.appointment_form import AppointmentFormDialog
        dialog = AppointmentFormDialog(self)
        self.wait_window(dialog)
        self._load_data()
