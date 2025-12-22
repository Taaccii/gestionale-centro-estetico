"""
Dialog per visualizzare lo storico e i dettagli di un cliente.
"""
import customtkinter as ctk
from gui.theme import COLORS, SIZES, get_font, ICONS
from datetime import datetime

class ClientDetailsDialog(ctk.CTkToplevel):
    """
    Finestra popup per mostrare lo storico appuntamenti di un cliente.
    """

    def __init__(self, parent, cliente):
        super().__init__(parent)
        self.cliente = cliente

        self.title(f"Storico Cliente: {cliente.nome} {cliente.cognome}")
        self.geometry("600x700")
        
        # Centra la finestra
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 600) // 2
        y = (self.winfo_screenheight() - 700) // 2
        self.geometry(f"+{x}+{y}")
        
        self.configure(fg_color=COLORS["bg_dark"])
        self.transient(parent)
        self.grab_set()

        self._create_widgets()

    def _create_widgets(self):
        # Header Info Cliente
        header = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=SIZES["corner_radius"])
        header.pack(fill="x", padx=20, pady=20)

        # Nome e Cognome
        ctk.CTkLabel(
            header, 
            text=f"{self.cliente.nome} {self.cliente.cognome}", 
            font=get_font("title"),
            text_color=COLORS["text_primary"]
        ).pack(anchor="w", padx=20, pady=(15, 5))

        # Dettagli Contatto (Telefono, Email)
        contact_info = f"{ICONS['phone']} {self.cliente.telefono or 'N/D'}  •  {ICONS['email']} {self.cliente.email or 'N/D'}"
        ctk.CTkLabel(
            header, 
            text=contact_info, 
            font=get_font("body"),
            text_color=COLORS["text_secondary"]
        ).pack(anchor="w", padx=20, pady=(0, 5))

        # Data Iscrizione
        registration_info = f"{ICONS['calendar']} Cliente dal: {self.cliente.data_iscrizione.strftime('%d/%m/%Y')}"
        ctk.CTkLabel(
            header, 
            text=registration_info, 
            font=get_font("body"),
            text_color=COLORS["text_secondary"]
        ).pack(anchor="w", padx=20, pady=(0, 15))

        # Note se presenti
        if self.cliente.note:
            note_frame = ctk.CTkFrame(header, fg_color=COLORS["bg_dark"], corner_radius=5)
            note_frame.pack(fill="x", padx=20, pady=(0, 15))
            ctk.CTkLabel(
                note_frame, 
                text=f"{ICONS['notes']} Note: {self.cliente.note}", 
                font=get_font("small"),
                text_color=COLORS["warning"],
                wraplength=500,
                justify="left"
            ).pack(padx=10, pady=8)

        # Tabs o Sezioni per Appuntamenti
        self.tabview = ctk.CTkTabview(
            self, 
            fg_color="transparent", 
            segmented_button_fg_color=COLORS["bg_card"],
            segmented_button_selected_color=COLORS["accent"],
            segmented_button_selected_hover_color=COLORS["accent_hover"],
            segmented_button_unselected_hover_color=COLORS["bg_dark"],
            command=self._update_tab_text_colors
        )
        self.tabview.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.tabview.add("Futuri")
        self.tabview.add("Storico")

        self._load_appointments("Futuri", self.cliente.get_appuntamenti_futuri())
        self._load_appointments("Storico", self.cliente.get_appuntamenti_passati())

        # Primo aggiornamento colori testo (dopo che le tab sono state aggiunte)
        self.after(100, self._update_tab_text_colors)

    def _update_tab_text_colors(self):
        """Aggiorna manualmente i colori del testo per distinguere la tab selezionata."""
        try:
            curr = self.tabview.get()
            for name, btn in self.tabview._segmented_button._buttons_dict.items():
                if name == curr:
                    btn.configure(text_color=COLORS["text_on_accent"])
                else:
                    btn.configure(text_color=COLORS["text_primary"])
        except:
            pass

    def _load_appointments(self, tab_name, appuntamenti):
        container = ctk.CTkScrollableFrame(self.tabview.tab(tab_name), fg_color="transparent")
        container.pack(fill="both", expand=True)

        if not appuntamenti.exists():
            ctk.CTkLabel(
                container, 
                text="Nessun appuntamento trovato.", 
                font=get_font("body"),
                text_color=COLORS["text_secondary"]
            ).pack(pady=50)
            return

        for app in appuntamenti:
            self._create_appointment_row(container, app)

    def _create_appointment_row(self, container, app):
        row = ctk.CTkFrame(container, fg_color=COLORS["bg_card"], corner_radius=10)
        row.pack(fill="x", pady=8, padx=5)

        # Data e Ora
        data_str = app.data_ora_inizio.strftime("%d/%m/%Y %H:%M")
        
        # Colonna Sx: Data e Servizi
        content_frame = ctk.CTkFrame(row, fg_color="transparent")
        content_frame.pack(side="left", fill="both", expand=True, padx=25, pady=18)

        ctk.CTkLabel(
            content_frame, 
            text=data_str, 
            font=get_font("button"),
            text_color=COLORS["accent"]
        ).pack(anchor="w")

        # Servizi
        servizi = ", ".join([d.servizio.nome for d in app.dettagli.all()])
        ctk.CTkLabel(
            content_frame, 
            text=servizi, 
            font=get_font("body"),
            text_color=COLORS["text_primary"],
            wraplength=350,
            justify="left"
        ).pack(anchor="w")

        # Info Staff
        ctk.CTkLabel(
            content_frame, 
            text=f"{ICONS['staff']} {app.dipendente.nome}", 
            font=get_font("small"),
            text_color=COLORS["text_secondary"]
        ).pack(anchor="w")

        # Colonna dx: Stato e Prezzo
        info_frame = ctk.CTkFrame(row, fg_color="transparent")
        info_frame.pack(side="right", padx=25, pady=18)

        # Colore stato
        stato_colors = {
            'completato': COLORS["success"],
            'annullato': COLORS["error"],
            'prenotato': COLORS["accent"],
            'in_corso': COLORS["warning"]
        }
        color = stato_colors.get(app.stato, COLORS["text_secondary"])

        ctk.CTkLabel(
            info_frame, 
            text=app.get_stato_display(), 
            font=get_font("small"),
            text_color=color
        ).pack(anchor="e")
        if app.stato == 'annullato' and app.motivo_annullamento:
            ctk.CTkLabel(
                info_frame,
                text=f"Motivo: {app.motivo_annullamento}",
                font=get_font("small"),
                text_color=COLORS["error"],
                wraplength=100
            ).pack(pady=(5, 0), anchor="e")

        ctk.CTkLabel(
            info_frame, 
            text=f"€ {app.prezzo_totale:.2f}", 
            font=get_font("heading"),
            text_color=COLORS["text_primary"]
        ).pack(anchor="e")
