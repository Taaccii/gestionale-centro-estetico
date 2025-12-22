"""
Schermata Calendario - Agenda Appuntamenti
"""

import customtkinter as ctk 
from gui.components.base import BaseScreen, ScreenHeader
from gui.forms.appointment_form import AppointmentFormDialog
from gui.theme import COLORS, SIZES, ICONS, get_font
from datetime import date, datetime, timedelta
from gui.components.toast import ToastNotification
import locale # serve per formattare le date nella lingua del sistema
import calendar

import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from anagrafica.models import Dipendente
from appuntamenti.models import Appuntamento

# Imposta locale italiano per i nomi dei giorni
try:
    locale.setlocale(locale.LC_TIME, "it_IT.UTF-8")
except:
        pass # Fallback se non disponibile


class CalendarScreen(BaseScreen):
    def __init__(self, parent):
        # 1. Carica i dati IMMEDIATAMENTE (fondamentale per _create_layout chiamato da super().__init__)
        self._init_staff_data()

        super().__init__(
            parent,
            title="Calendario",
            icon=ICONS["calendar"],
            button_text="+ Nuovo Appuntamento"
        )

        # Stato corrente (giorno visualizzato)
        self.current_date = date.today()
        
        # Dizionario per le caselle (slot)
        self.slots = {}

        # Stato per vista giorno, settimana, mese
        self.view_mode = "Giorno"
        
        # Memorizza il dipendente selezionato (None = Tutti)
        self.staff_filter_id = None 
        
        # Memorizza il dipendente che stiamo guardando per la vista settimana 
        # (usiamo il primo se disponibile per default quando non "Tutti")
        self.current_staff_filter = self.staff_members[0] if self.staff_members else None

        # Lista per tenere traccia delle card appuntamento create (per distruggerle)
        self.appointment_widgets = []
        
        # Riferimento per il toast (per evitare Garbage Collection)
        self.notification = None

        self._create_widgets()
        # _load_appointments viene chiamato da _rebuild_grid, non serve chiamarlo qui

    def _init_staff_data(self):
        """Inizializza i dati dei dipendenti se non già presenti."""
        if not hasattr(self, 'staff_members'):
            self.staff_members = list(Dipendente.objects.all())
            self.staff_options = ["Tutti"] + [f"{s.nome} {s.cognome}" for s in self.staff_members]

    def _on_staff_filter_change(self, value):
        """Gestisce il cambio del filtro dipendente nell'header."""
        if value == "Tutti":
            self.staff_filter_id = None
        else:
            # Trova l'ID del dipendente selezionato
            for s in self.staff_members:
                if f"{s.nome} {s.cognome}" == value:
                    self.staff_filter_id = s.id
                    # Aggiorna anche il filtro per la vista settimana
                    self.current_staff_filter = s
                    break
        
        # Forza la ricostruzione della griglia
        self._rebuild_grid()

    def _create_layout(self):
        """
        Override del layout base per un header moderno con controlli centrali.
        """
        # Sicurezza: Assicurati che i dati siano carichi prima di creare i widget dell'header
        self._init_staff_data()
        
        self.header = ScreenHeader(
            self,
            title=self.title,
            icon=self.icon
        )
        self.header.pack(fill="x", padx=30, pady=(30, 10))

        # --- CONVERSIONE DA PACK A GRID ---
        # Nasconde il titolo pack di default (lo ricreiamo nel left_container)
        self.header.title_label.pack_forget()
        
        # Configura la griglia a 3 colonne (Sinistra, Centro, Destra)
        self.header.grid_columnconfigure(0, weight=0)  # Sinistra (Titolo)
        self.header.grid_columnconfigure(1, weight=1)  # Centro (Controlli - Espandibile)
        self.header.grid_columnconfigure(2, weight=0)  # Destra (Vista/Nuovo)
        
        # Posiziona i container
        self.header.left_container.grid(row=0, column=0, sticky="w", padx=(0, 20))
        self.header.center_container.grid(row=0, column=1, sticky="nsew")
        self.header.right_container.grid(row=0, column=2, sticky="e", padx=(20, 0))
        
        # Ricrea il titolo nel left_container
        title_label = ctk.CTkLabel(
            self.header.left_container,
            text=f"{self.icon} {self.title}",
            font=get_font("title"),
            text_color=COLORS["text_primary"],
            pady=2
        )
        title_label.pack(side="left", pady=5)

        # --- CONTROLLI NELL'HEADER (Centro) ---
        # Container centrale per navigazione e filtro
        nav_frame = ctk.CTkFrame(self.header.center_container, fg_color="transparent")
        nav_frame.pack(expand=True) # Centra nel center_container

        # Container Bottoni Navigazione (Navigazione compatta)
        btns_container = ctk.CTkFrame(nav_frame, fg_color="transparent")
        btns_container.pack(side="left", padx=(0, 15))

        self.btn_prev = ctk.CTkButton(
            btns_container, text=ICONS["prev"], width=35, height=35,
            fg_color=COLORS["bg_card"], text_color=COLORS["text_primary"],
            hover_color=COLORS["accent_hover"], command=self._navigate_prev
        )
        self.btn_prev.pack(side="left", padx=2)

        btn_today = ctk.CTkButton(
            btns_container, text="Oggi", width=70, height=35,
            fg_color=COLORS["bg_card"], text_color=COLORS["text_primary"],
            hover_color=COLORS["accent_hover"], command=self._today
        )
        btn_today.pack(side="left", padx=5)

        self.btn_next = ctk.CTkButton(
            btns_container, text=ICONS["next"], width=35, height=35,
            fg_color=COLORS["bg_card"], text_color=COLORS["text_primary"],
            hover_color=COLORS["accent_hover"], command=self._navigate_next
        )
        self.btn_next.pack(side="left", padx=2)

        # Label Data (AUMENTATO width a 350 per contenere "Settimana...")
        date_container = ctk.CTkFrame(nav_frame, fg_color="transparent", width=350, height=35)
        date_container.pack(side="left")
        date_container.pack_propagate(False) 

        self.date_label = ctk.CTkLabel(
            date_container, text="", font=get_font("heading"),
            text_color=COLORS["text_primary"]
        )
        self.date_label.place(relx=0.5, rely=0.5, anchor="center") 

        self.date_label.place(relx=0.5, rely=0.5, anchor="center") 

        # --- CONTROLLI NELL'HEADER (Destra) ---
        # Selettore vista e bottone nuovo appuntamento
        right_frame = ctk.CTkFrame(self.header.right_container, fg_color="transparent")
        right_frame.pack(side="right")

        self.view_selector = ctk.CTkSegmentedButton(
            right_frame,
            values=["Giorno", "Settimana", "Mese"],
            selected_color=COLORS["accent"],
            selected_hover_color=COLORS["accent_hover"],
            unselected_hover_color=COLORS["bg_card"],
            text_color=COLORS["text_primary"],
            command=self._on_view_change,
            height=35
        )
        self.view_selector.set("Giorno")
        self.view_selector.pack(side="left", padx=(0, 15))
        
        # Inizializza colori testo
        self.after(100, self._update_selector_text_colors)

        btn_add = ctk.CTkButton(
            right_frame, text=self.button_text,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            text_color=COLORS["text_on_accent"], font=get_font("button"),
            width=180, height=35, corner_radius=SIZES["corner_radius"],
            command=self._on_add_new
        )
        btn_add.pack(side="left")

        # Toolbar filtri sotto header
        self.filter_toolbar = ctk.CTkFrame(self, fg_color="transparent")
        self.filter_toolbar.pack(fill="x", padx=30, pady=(0, 15))

        # Container interno per allineamento
        filter_container = ctk.CTkFrame(self.filter_toolbar, fg_color="transparent")
        filter_container.pack(side="left")

        # Etichetta Filtro
        ctk.CTkLabel(
            filter_container,
            text=f"{ICONS['staff']} Filtra per Staff:",
            font=get_font("small"),
            text_color=COLORS["text_secondary"]
        ).pack(side="left", padx=(5, 10))

        # Filtro dipendenti
        self.staff_selector = ctk.CTkOptionMenu(
            filter_container,
            values=self.staff_options,
            width=220,
            height=32,
            fg_color=COLORS["bg_card"],
            button_color=COLORS["border"],     
            button_hover_color=COLORS["accent"],
            dynamic_resizing=False,
            text_color=COLORS["text_primary"],
            dropdown_fg_color=COLORS["bg_card"],
            dropdown_hover_color=COLORS["accent"],
            dropdown_text_color=COLORS["text_primary"],
            font=get_font("small"),
            dropdown_font=get_font("small"),
            command=self._on_staff_filter_change,
        )
        self.staff_selector.set("Tutti")
        self.staff_selector.pack(side="left")

    def _create_widgets(self):
        """Metodo per l'inizializzazione dei widget della griglia."""
        # Evita di ricreare la griglia se esiste già (fix per duplicazione)
        if hasattr(self, 'grid_container'):
            return

        # --- FOOTER (Copyright & Firma) ---
        self.footer = ctk.CTkFrame(self, fg_color="transparent")
        self.footer.pack(side="bottom", fill="x", pady=(5, 20))
        
        copyright_text = "© 2025 Gestionale Centro Estetico Tacci • Tutti i diritti riservati • Sviluppato col ❤️ da TacciDev • taccidev@gmail.com"
        ctk.CTkLabel(
            self.footer,
            text=copyright_text,
            font=get_font("small"),
            text_color=COLORS["text_secondary"],
            anchor="center",
            height=15
        ).pack(fill="x")

        # Main Grid (Scrollable)
        self.grid_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.grid_container.pack(fill="both", expand=True, padx=20, pady=(0, 5))

        # Costruisce la struttura interna in base alla vista
        self._rebuild_grid()
        self._update_date_label()


    def _create_slot(self, row, col, staff, time_str, day_index=None):
        """Helper per creare un singolo quadratino (slot)"""
        slot = ctk.CTkFrame(
            self.grid_container,
            fg_color=COLORS["bg_card"],
            corner_radius=4,
            height=50,
            border_width=1,
            border_color=COLORS["border"] 
        )
        slot.grid(row=row, column=col, sticky="nsew", padx=1, pady=1)
        
        # Stato dello slot
        slot.is_occupied = False
        slot.appointment = None
        # Rendo cliccabile gli slot usando lambda per bloccare i valori staff e orario
        slot.bind("<Button-1>", lambda e, s=staff, h=time_str: self._on_slot_click(e, s, h))
        
        # Effetto hovering del mouse sugli slot solo se non occupato
        slot.bind("<Enter>", lambda e, s=slot: s.configure(
            fg_color=COLORS["border"],
            border_color=COLORS["accent"]
        ) if not s.is_occupied else None)
        
        slot.bind("<Leave>", lambda e, s=slot: s.configure(
            fg_color=COLORS["bg_card"],
            border_color=COLORS["bg_card"]
        ) if not s.is_occupied else None)
        # Salva lo slot nel dizionario (chiave diversa in base alla vista)
        if self.view_mode == "Giorno":
            self.slots[(staff.id, time_str)] = slot
        else:
            self.slots[(staff.id, time_str, day_index)] = slot
    
    def _rebuild_grid(self):
        """Ricostruisce la struttura delle colonne in base alla vista (Giorno/Settimana/Mese)"""
        
        # Svuota tutti i widget e i dati vecchi
        for widget in self.grid_container.winfo_children():
            widget.destroy()
        self.slots.clear()
        self.appointment_widgets.clear()

        # Reset dello scroll (torna in cima)
        try:
            self.grid_container._parent_canvas.yview_moveto(0)
        except:
            pass

        # RESET: Svuota widget e buffer prima di ricostruire per evitare crash
        for widget in self.grid_container.winfo_children():
            widget.destroy()
        self.slots.clear()
        self.appointment_widgets.clear()

        # RESET: Svuota le configurazioni delle colonne precedenti
        for i in range(25):
            self.grid_container.grid_columnconfigure(i, weight=0, uniform="")

        if self.view_mode == "Mese":
            self._draw_monthly_view()
            return

        # Configura le colonne in base alla vista
        if self.view_mode == "Giorno":
            # Filtra i dipendenti da mostrare se il filtro è attivo
            if self.staff_filter_id:
                active_staff = [s for s in self.staff_members if s.id == self.staff_filter_id]
            else:
                active_staff = self.staff_members

            # La colonna 0 è per l'orario e le altre per i dipendenti
            headers = ["Orario"] + [f"{s.nome} {s.cognome[0]}." for s in active_staff]
            self.current_visible_staff = active_staff # Salva per _create_slot
        else: # Vista Settimana
            # Calcola i giorni della settimana corrente
            start_of_week = self.current_date - timedelta(days=self.current_date.weekday())
            day_names = ["Lun", "Mar", "Mer", "Gio", "Ven", "Sab"]
            headers = ["Orario"]
            for i, name in enumerate(day_names):
                day_date = start_of_week + timedelta(days=i)
                headers.append(f"{name} {day_date.day}")
        # Applica i pesi alle colonne per allargarle equamente
        self.grid_container.grid_columnconfigure(0, weight=0, minsize=60) # Orario fisso
        for i in range(1, len(headers)):
            self.grid_container.grid_columnconfigure(i, weight=1, uniform="colonna") # Staff/Giorni dinamici
        # Disegna l'intestazione (Riga 0)
        for i, text in enumerate(headers):
            ctk.CTkLabel(self.grid_container, text=text, font=get_font("button")).grid(row=0, column=i, sticky="nsew", padx=5, pady=10)
        # Genera le righe orari (dalle 8 alle 20 ogni 30 min)
        start_hour = 8
        end_hour = 20
        current_row = 1 # Per partire dalla riga 1 perchè la riga 0 contiene l'header
        for hour in range(start_hour, end_hour):
            for minute in [0, 30]:
                # 0: se è più corto di 2 cifre, aggiungi uno 0 davanti
                time_str = f"{hour:02d}:{minute:02d}"
                
                # Etichetta Orario (Colonna 0)
                ctk.CTkLabel(
                    self.grid_container, 
                    text=time_str, 
                    font=get_font("small"), 
                    text_color=COLORS["text_secondary"]
                ).grid(row=current_row, column=0, padx=5, pady=15)
                # Genera le colonne dei dati
                if self.view_mode == "Giorno":
                    # Slot per ogni dipendente visibile
                    for i, staff in enumerate(self.current_visible_staff):
                        self._create_slot(current_row, i + 1, staff, time_str)
                else: # Settimana
                    for i in range(6): # 6 giorni (Lun-Sab)
                        self._create_slot(current_row, i + 1, self.current_staff_filter, time_str, day_index=i)
                current_row += 1
        
        # Carica gli appuntamenti (chiamato alla fine della costruzione della griglia)
        self._load_appointments()


    def _load_appointments(self):
        """Carica gli appuntamenti nella griglia"""
        
        # Svuota tutti i widget appuntamento esistenti
        for widget in self.appointment_widgets:
            widget.destroy()
        self.appointment_widgets.clear() # Svuota la lista

        # Svuota tutti gli slot (e rimuove etichette/testi all'interno per evitare duplicati nel Mese)
        for slot in self.slots.values():
            slot.is_occupied = False # Torna libero lo slot
            slot.configure(fg_color=COLORS["bg_card"], border_color=COLORS["bg_card"]) # Torna colore originale
            # Pulisce i figli dello slot (es. label del mese) 
            for child in slot.winfo_children():
                # Non distruggiamo la label del numero del giorno (nel Mese è il primo figlio)
                if isinstance(child, ctk.CTkLabel) and child.cget("text").isdigit():
                    continue
                child.destroy()

        # Query per prendere gli appuntamenti
        if self.view_mode == "Giorno":
            start_date = end_date = self.current_date
        elif self.view_mode == "Settimana":
            start_date = self.current_date - timedelta(days=self.current_date.weekday())
            end_date = start_date + timedelta(days=6)
        else: # Mese
            start_date = self.current_date.replace(day=1)
            _, last = calendar.monthrange(self.current_date.year, self.current_date.month)
            end_date = self.current_date.replace(day=last)

        appuntamenti = Appuntamento.objects.filter(
            data_ora_inizio__date__range=[start_date, end_date]
        ).select_related('cliente', 'dipendente').prefetch_related('dettagli__servizio')

        # Applica il filtro dipendente se selezionato
        if self.staff_filter_id:
            appuntamenti = appuntamenti.filter(dipendente_id=self.staff_filter_id)
        elif self.view_mode == "Settimana":
            # In vista settimana, se non c'è un filtro globale, usiamo quello di default per la settimana
            appuntamenti = appuntamenti.filter(dipendente=self.current_staff_filter)

        # Scrive gli appuntamenti ricavando la chiave per trovare lo slot giusto
        for app in appuntamenti:

            # Mappa dei colori per stato appuntamento
            status_color = {
                'prenotato': COLORS["accent"],
                'in_corso': COLORS["warning"],
                'completato': COLORS["success"],
                'annullato': COLORS["text_secondary"]
            }
            colore_card = status_color.get(app.stato, COLORS["accent"])

            # Calcola il numero di blocci da 30 minut (minimo 1)
            num_slot = max(1, app.durata_minuti // 30)

            # Trova lo slot di partenza per avere le coordinate (riga, colonna)
            ora_inizio = app.data_ora_inizio.strftime("%H:%M")
            if self.view_mode == "Giorno":
                chiave_inizio = (app.dipendente.id, ora_inizio)
            elif self.view_mode == "Settimana":
                chiave_inizio = (app.dipendente.id, ora_inizio, app.data_ora_inizio.weekday())
            else: # Mese
                chiave_inizio = app.data_ora_inizio.date()
            
            if chiave_inizio in self.slots:
                if self.view_mode != "Mese":
                    slot_base = self.slots[chiave_inizio]
                    # Recupera le coordinate grid dello slot base
                    # grid_info() dice esattamente dove si trova nella griglia
                    info = slot_base.grid_info()
                    riga = info['row']
                    colonna = info['column']


                    # Segna tutti gli slot coperti come occupati
                    for i in range(num_slot):
                        # Calcola orario dello slot corrente
                        nuova_ora = (app.data_ora_inizio + timedelta(minutes=i*30)).strftime("%H:%M")
                        if self.view_mode == "Settimana":
                            chiave_extra = (app.dipendente.id, nuova_ora, app.data_ora_inizio.weekday())
                        else:
                            chiave_extra = (app.dipendente.id, nuova_ora)

                        # Controlla se lo slot esiste nella nostra griglia
                        if chiave_extra in self.slots:
                            target_slot = self.slots[chiave_extra] # Prende lo slot giusto
                            target_slot.is_occupied = True
                            target_slot.appointment = app

                    # Carica i nomi dei servizi
                    nomi_servizi = [d.servizio.nome for d in app.dettagli.all()]
                    
                    # Crea la CARD come Frame per avere controllo totale sugli stili interni
                    card = ctk.CTkFrame(
                        self.grid_container,
                        fg_color=colore_card,
                        corner_radius=4
                    )
                    self.appointment_widgets.append(card)
                    card.grid(row=riga, column=colonna, rowspan=num_slot, sticky="nsew", padx=2, pady=2)
                    
                    # Bindings per il click (apre modifica)
                    card.bind("<Button-1>", lambda e, a=app: self._on_appointment_click(a))
                    
                    # Effetto Hover
                    def on_enter(e, c=card): c.configure(fg_color=COLORS["accent_hover"])
                    def on_leave(e, c=card, col=colore_card): c.configure(fg_color=col)
                    
                    card.bind("<Enter>", on_enter)
                    card.bind("<Leave>", on_leave)

                    # Testo Cliente
                    lbl_cliente = ctk.CTkLabel(
                        card,
                        text=f"{app.cliente.nome} {app.cliente.cognome}",
                        font=get_font("body_bold") if self.view_mode == "Giorno" else get_font("small_bold"),
                        text_color=COLORS["text_on_accent"],
                        height=45 if self.view_mode == "Giorno" else 35,
                        pady=5,
                        justify="center",
                        wraplength=150
                    )
                    lbl_cliente.pack(pady=(10, 2), padx=5)
                    lbl_cliente.bind("<Button-1>", lambda e, a=app: self._on_appointment_click(a))
                    lbl_cliente.bind("<Enter>", on_enter)
                    lbl_cliente.bind("<Leave>", on_leave)

                    # Testo Servizi 
                    testo_servizi = "\n".join([f"• {s}" for s in nomi_servizi]) if nomi_servizi else "Nessun Servizio"
                    lbl_servizi = ctk.CTkLabel(
                        card,
                        text=testo_servizi,
                        font=get_font("small"),
                        text_color=COLORS["text_on_accent"],
                        height=30,
                        pady=2,
                        justify="center"
                    )
                    lbl_servizi.pack(pady=2, padx=5)
                    lbl_servizi.bind("<Button-1>", lambda e, a=app: self._on_appointment_click(a))
                    lbl_servizi.bind("<Enter>", on_enter)
                    lbl_servizi.bind("<Leave>", on_leave)

                    # Se in vista settimana, mostra anche l'operatore
                    if self.view_mode == "Settimana":
                        lbl_staff = ctk.CTkLabel(
                            card,
                            text=f"{ICONS['staff']} {app.dipendente.nome}",
                            font=("Helvetica Neue", 10),
                            text_color=COLORS["text_on_accent"],
                            height=25,
                            pady=2
                        )
                        lbl_staff.pack(side="bottom", pady=5)
                        lbl_staff.bind("<Button-1>", lambda e, a=app: self._on_appointment_click(a))
                        lbl_staff.bind("<Enter>", on_enter)
                        lbl_staff.bind("<Leave>", on_leave)
                else:
                    # Vista Mese
                    nomi_servizi = [d.servizio.nome for d in app.dettagli.all()]
                    servizi_str = "\n".join([f"• {n}" for n in nomi_servizi]) if nomi_servizi else "(Nessun servizio)"
                    
                    testo_titolo = f"{app.cliente.nome} {app.cliente.cognome}"
                    testo_info = (
                        f"{servizi_str}\n"
                        f"[{app.dipendente.nome}]"
                    )
                    
                    # Frame per l'appuntamento ("sticker")
                    app_sticker = ctk.CTkFrame(
                        self.slots[chiave_inizio], 
                        fg_color="transparent",
                        corner_radius=4
                    )
                    app_sticker.pack(fill="x", padx=4, pady=1)
                    self.appointment_widgets.append(app_sticker)
                    
                    # Riferimento alla cella del giorno (lo slot vero e proprio)
                    day_frame = self.slots[chiave_inizio]

                    # Effetto Hover per il Mese
                    def on_enter_mese(e, s=day_frame): s.configure(border_width=2, border_color=COLORS["accent"])
                    def on_leave_mese(e, s=day_frame): s.configure(border_width=1, border_color=COLORS["border"])
                    
                    app_sticker.bind("<Enter>", on_enter_mese)
                    app_sticker.bind("<Leave>", on_leave_mese)

                    # Click sullo sticker: Vai al giorno corrispondente
                    app_sticker.bind("<Button-1>", lambda e, d=app.data_ora_inizio.date(): self._on_month_app_click(d))

                    # Nome Cliente 
                    lbl_cliente_mese = ctk.CTkLabel(
                        app_sticker,
                        text=testo_titolo,
                        font=get_font("small_bold"),
                        text_color=colore_card,
                        height=25,
                        pady=2,
                        justify="left"
                    )
                    lbl_cliente_mese.pack(anchor="w")
                    lbl_cliente_mese.bind("<Button-1>", lambda e, d=app.data_ora_inizio.date(): self._on_month_app_click(d))
                    lbl_cliente_mese.bind("<Enter>", on_enter_mese)
                    lbl_cliente_mese.bind("<Leave>", on_leave_mese)

                    # Dettagli servizi e dipendente 
                    lbl_details = ctk.CTkLabel(
                        app_sticker,
                        text=testo_info,
                        font=("Helvetica Neue", 10), # Font extra-piccolo per pulizia estrema
                        text_color=COLORS["text_secondary"],
                        justify="left"
                    )
                    lbl_details.pack(anchor="w")
                    lbl_details.bind("<Button-1>", lambda e, d=app.data_ora_inizio.date(): self._on_month_app_click(d))
                    lbl_details.bind("<Enter>", on_enter_mese)
                    lbl_details.bind("<Leave>", on_leave_mese)



    def _navigate_prev(self):
        """Sposta la data indietro in base alla vista"""
        if self.view_mode == "Giorno":
            self.current_date -= timedelta(days=1)
        elif self.view_mode == "Settimana":
            self.current_date -= timedelta(days=7)
        else: # Mese
            # Sposta al primo del mese precedente
            first = self.current_date.replace(day=1)
            self.current_date = (first - timedelta(days=1)).replace(day=1)
            
        self._update_date_label()
        if self.view_mode == "Mese":
            self._rebuild_grid() # Rebuild include load_appointments
        else:
            self._load_appointments()

    def _navigate_next(self):
        """Sposta la data in avanti in base alla vista"""
        if self.view_mode == "Giorno":
            self.current_date += timedelta(days=1)
        elif self.view_mode == "Settimana":
            self.current_date += timedelta(days=7)
        else: # Mese
            # Sposta al primo del mese successivo
            # (Giorno 28 + 4 giorni garantisce di arrivare al mese dopo)
            first = self.current_date.replace(day=28) + timedelta(days=4)
            self.current_date = first.replace(day=1)

        self._update_date_label()
        if self.view_mode == "Mese":
            self._rebuild_grid()
        else:
            self._load_appointments()

    def _today(self):
        self.current_date = date.today()
        self._update_date_label()
        if self.view_mode == "Mese":
            self._rebuild_grid()
        else:
            self._load_appointments()

    def _on_month_app_click(self, app_date):
        """Passa alla vista giorno per la data selezionata"""
        self.current_date = app_date
        self.view_mode = "Giorno"
        self.view_selector.set("Giorno")
        self._update_date_label()
        self._rebuild_grid()

    def _update_date_label(self):
        # Formatta la data e la scrive nel Label
        if self.view_mode == "Mese":
            text = self.current_date.strftime("%B %Y").title()
        elif self.view_mode == "Settimana":
            start = self.current_date - timedelta(days=self.current_date.weekday())
            end = start + timedelta(days=6)
            text = f"Settimana {start.strftime('%d %b')} - {end.strftime('%d %b %Y')}".title()
        else:
            text = self.current_date.strftime("%A %d %B %Y").title()

        self.date_label.configure(text=text)


    
    def _on_add_new(self):
        """Apre il form per un nuovo appuntamento"""
        dialog = AppointmentFormDialog(self, initial_date=self.current_date)
        self.wait_window(dialog)
        if dialog.result:
            self._load_appointments()

            # Se il risultato è un dizionario (messaggio), mostra il Toast
            if isinstance(dialog.result, dict):
                self.notification = ToastNotification(
                    self,
                    message=dialog.result["message"],
                    color_key=dialog.result["type"]
                )

    def _on_slot_click(self, event, staff, time_str):
        """Gestisce il click sugli slot del calendario"""
        dialog = AppointmentFormDialog(
            self,
            initial_date=self.current_date,
            initial_staff=staff,
            initial_time=time_str
        )
        self.wait_window(dialog)

        if dialog.result:
            self._load_appointments()

            # Se il risultato è un dizionario (messaggio), mostra il Toast
            if isinstance(dialog.result, dict):
                self.notification = ToastNotification(
                    self,
                    message=dialog.result["message"],
                    color_key=dialog.result["type"]
                )

    def _on_appointment_click(self, appointment):
        """Gestisce il click su una card appuntamento esistente (Modifica)"""
        dialog = AppointmentFormDialog(
            self,
            appointment=appointment
        )
        self.wait_window(dialog)
        if dialog.result:
            self._load_appointments()

            # Se il risultato è un dizionario (messaggio), mostra il Toast
            if isinstance(dialog.result, dict):
                self.notification = ToastNotification(
                    self,
                    message=dialog.result["message"],
                    color_key=dialog.result["type"]
                )

    def _draw_monthly_view(self):
        """Disegna la griglia del mese"""
        headers = ["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"]

        # Configura 7 colonne uguali per i giorni del mese
        for i in range(7):
            self.grid_container.grid_columnconfigure(i, weight=1, uniform="mese")

        # Header giorni
        for i, day in enumerate(headers):
            ctk.CTkLabel(self.grid_container, text=day, font=get_font("button")).grid(row=0, column=i, pady=10)

        # Calcola la struttura del mese corrente
        year, month = self.current_date.year, self.current_date.month
        cal = calendar.monthcalendar(year, month)

        # Disegna le settimane
        for r, week in enumerate(cal):
            for c, day in enumerate(week):
                if day == 0: continue # Giorno di un altro mese

                # Crea la casellina del giorno
                day_frame = ctk.CTkFrame(
                    self.grid_container,
                    fg_color=COLORS["bg_card"],
                    corner_radius=4,
                    height=80,
                    border_width=1,
                    border_color=COLORS["border"],
                )
                day_frame.grid(row=r+1, column=c, sticky="nsew", padx=2, pady=2)

                # Numero del giorno
                lbl_numero = ctk.CTkLabel(day_frame, text=str(day), font=get_font("small_bold"))
                lbl_numero.pack(anchor="nw", padx=5, pady=2)

                # Effetto Hover sulla cella
                def on_enter_cell(e, f=day_frame): f.configure(border_width=2, border_color=COLORS["accent"])
                def on_leave_cell(e, f=day_frame): f.configure(border_width=1, border_color=COLORS["border"])
                
                day_frame.bind("<Enter>", on_enter_cell)
                day_frame.bind("<Leave>", on_leave_cell)
                lbl_numero.bind("<Enter>", on_enter_cell)
                lbl_numero.bind("<Leave>", on_leave_cell)

                # Salva lo slot e usa la data completa come chiave
                data_slot = date(year, month, day)
                self.slots[data_slot] = day_frame
        
        # Carica i dati
        self._load_appointments()
    
    def _on_view_change(self, value):
        self.view_mode = value
        
        # Aggiorna subito la label e i tasti navigazione
        self._update_date_label()
        
        # Aggiorna colori testo selettore
        self._update_selector_text_colors()

        # Ricostruisce la griglia che a sua volta ricarica tutti i dati da sola
        self._rebuild_grid()

        # Ricostruisce la griglia che a sua volta ricarica tutti i dati da sola
        self._rebuild_grid()

    def _update_selector_text_colors(self):
        """Aggiorna manualmente i colori del testo per distinguere la vista selezionata."""
        try:
            curr = self.view_selector.get()
            for name, btn in self.view_selector._buttons_dict.items():
                if name == curr:
                    btn.configure(text_color=COLORS["text_on_accent"])
                else:
                    btn.configure(text_color=COLORS["text_primary"])
        except:
            pass