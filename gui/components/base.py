"""
Componenti riutilizzabili per le schermate del gestionale.

"""

import customtkinter as ctk 
from gui.theme import COLORS, SIZES , get_font


class ScreenHeader(ctk.CTkFrame):
    """
    Header standard per tutte le schermate.
    Include titolo con icona e pulsante opzionale.
    Layout: Titolo a sinistra, Pulsante a destra, Ricerca opzionale al centro.
    """

    def __init__(self, parent, title, icon, button_text=None, button_command=None, search_callback=None, search_placeholder="Cerca..."):
        super().__init__(parent, fg_color="transparent")
        
        # --- TITOLO (Sinistra) ---
        self.title_label = ctk.CTkLabel(
            self,
            text=f"{icon} {title}",
            font=get_font("title"),
            text_color=COLORS["text_primary"],
            anchor="w",
            pady=2
        )
        self.title_label.pack(side="left", padx=(2, 0), pady=5)

        # --- RICERCA (Centro) ---
        if search_callback:
            self.search_entry = ctk.CTkEntry(
                self,
                placeholder_text=search_placeholder,
                placeholder_text_color="#AAAAAA", # Grigio più chiaro per visibilità
                width=400, # Ancora più largo e leggibile
                height=38,
                corner_radius=19,
                fg_color=COLORS["bg_card"],
                border_color=COLORS["border"],
                font=get_font("body")
            )
            self.search_entry.place(relx=0.5, rely=0.5, anchor="center")
            
            # Binding attivo per ricerca istantanea (evita StringVar per stabilità placeholder)
            self.search_entry.bind("<KeyRelease>", lambda e: search_callback(self.search_entry.get()))

        # --- PULSANTE (Destra) ---
        if button_text and button_command:
            self.action_btn = ctk.CTkButton(
                self,
                text=button_text,
                font=get_font("button"),
                fg_color=COLORS["accent"],
                hover_color=COLORS["accent_hover"],
                text_color=COLORS["text_on_accent"],
                width=180,
                height=35,
                corner_radius=SIZES["corner_radius"],
                command=button_command
            )
            self.action_btn.pack(side="right")

        # Container per layout avanzati (Calendar)
        self.left_container = ctk.CTkFrame(self, fg_color="transparent")
        self.center_container = ctk.CTkFrame(self, fg_color="transparent")
        self.right_container = ctk.CTkFrame(self, fg_color="transparent")


class DataCard(ctk.CTkFrame):
    """
    Card standard per visualizzare dati.
    Include un frame content interno per il contenuto.
    """

    def __init__(self, parent):
        super().__init__(
            parent,
            fg_color=COLORS["bg_card"],
            corner_radius=SIZES["corner_radius"]
        )

        # Frame interno per il contenuto
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill="x", padx=15, pady=12) # Aumentato per card leggermente più grandi

    def add_title(self, text):
        """Aggiunge un titolo alla card."""
        label = ctk.CTkLabel(
            self.content,
            text=text,
            font=get_font("heading"),
            text_color=COLORS["text_primary"],
            anchor="w",
            pady=3        # Padding minimo interno per proteggere dal clipping
        )
        label.pack(anchor="w", fill="x", pady=(0, 4)) # Spaziatura tra titolo e dettagli
        return label

    def add_detail(self, text, color=None):
        """Aggiunge una riga di dettaglio alla card"""
        label = ctk.CTkLabel(
            self.content,
            text=text,
            font=get_font("body"),
            text_color=color or COLORS["text_secondary"],
            anchor="w",
            pady=2        # Padding minimo interno per proteggere dal clipping
        )
        label.pack(anchor="w", fill="x", pady=0)
        return label

    def add_detail_row(self, left_text, right_text, left_color=None, right_color=None):
        """Aggiunge una riga con testo a sinistra e testo a destra (Stato) sulla stessa riga."""
        row = ctk.CTkFrame(self.content, fg_color="transparent")
        row.pack(fill="x", pady=(2, 0)) # Piccola spaziatura superiore
        
        left_label = ctk.CTkLabel(
            row, text=left_text, font=get_font("body"),
            text_color=left_color or COLORS["text_secondary"],
            anchor="w", pady=2
        )
        left_label.pack(side="left")
        
        right_label = ctk.CTkLabel(
            row, text=right_text, font=get_font("small"),
            text_color=right_color or COLORS["success"],
            anchor="e", pady=2
        )
        right_label.pack(side="right", padx=(0, 15)) # Distanza moderata dal bordo
        return left_label, right_label

    def add_status(self, text, is_active=True):
        """Aggiunge un indicatore di stato alla card (allineato a destra)"""
        color = COLORS["success"] if is_active else COLORS["error"]
        label = ctk.CTkLabel(
            self.content,
            text=text,
            font=get_font("small"),
            text_color=color,
            anchor="e",   # Allineato a DESTRA
            pady=2
        )
        label.pack(anchor="e", fill="x", pady=(5, 0))
        return label

class ScrollableList(ctk.CTkScrollableFrame):
    """
    Lista scrollabile standard.
    Usata come container per le card.
    """

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
    
    def clear(self):
        """Rimuove tutti i widget dalla lista."""
        for widget in self.winfo_children():
            widget.destroy()

    def show_empty_message(self, message):
        """Mostra un messaggio quando la lista è vuota"""
        label = ctk.CTkLabel(
            self,
            text=message,
            font=get_font("body"),
            text_color=COLORS["text_secondary"]
        )
        label.pack(pady=50)

class SearchFilter(ctk.CTkFrame):
    """
    Componente di ricerca con input e icona.
    """

    def __init__(self, parent, placeholder="Cerca...", callback=None):
        super().__init__(parent, fg_color="transparent")
        self.callback = callback

        # Entry di ricerca
        self.entry = ctk.CTkEntry(
            self,
            placeholder_text=placeholder,
            font=get_font("body"),
            height=35,
            width=300,
            corner_radius=SIZES["corner_radius"]
        )
        self.entry.pack(side="left", padx=(0, 10))
        
        # Binding per ricerca istantanea (opzionale) o su invio
        self.entry.bind("<KeyRelease>", self._on_change)

    def _on_change(self, event=None):
        """Chiamato al rilascio di ogni tasto"""
        if self.callback:
            self.callback(self.entry.get())

    def get(self):
        """Restituisce il valore attuale"""
        return self.entry.get()

    def clear(self):
        """Pulisce la barra di ricerca"""
        self.entry.delete(0, 'end')


class BaseScreen(ctk.CTkFrame):
    """
    Classe base per tutte le schermate.
    Fornisce struttura comune: header + ricerca + lista.
    """

    def __init__(self, parent, title, icon, button_text=None, search_placeholder=None):
        super().__init__(parent, fg_color=COLORS["bg_dark"])

        self.title = title
        self.icon = icon
        self.button_text = button_text
        self.search_placeholder = search_placeholder
        self.search_query = ""
        self._search_timer = None # Timer per debouncing ricerca

        self._create_layout()
        self._load_data()

    def _create_layout(self):
        """Crea il layout base della schermata con ricerca integrata nell'header."""

        # Header con ricerca integrata
        self.header = ScreenHeader(
            self,
            title=self.title,
            icon=self.icon,
            button_text=self.button_text,
            button_command=self._on_add_new,
            search_callback=self._on_search_change,
            # Se non c'è placeholder, usiamo uno standard per il look pulito
            search_placeholder=self.search_placeholder or "Cerca..."
        )
        self.header.pack(fill="x", padx=30, pady=(30, 20))

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

        # Lista scrollabile
        self.list_container = ScrollableList(self)
        self.list_container.pack(fill="both", expand=True, padx=30, pady=(0, 5))

    def _on_search_change(self, query):
        """Gestisce il cambiamento della query con debouncing per evitare sfarfallio."""
        self.search_query = query
        
        # Annulla il timer precedente se l'utente sta ancora scrivendo
        if self._search_timer:
            self.after_cancel(self._search_timer)
            
        # Avvia un nuovo timer: carica i dati solo dopo 200ms di inattività
        self._search_timer = self.after(200, self._load_data)

    def _load_data(self):
        """Override questo metodo per caricare i dati."""
        pass

    def _on_add_new(self):
        """Override questo metodo per gestire il click su Nuovo."""
        print(f"Nuovo {self.title} - TODO: implementare")


class KPICard(ctk.CTkFrame):
    """
    Card per visualizzare un KPI (Key Performance Indicator).
    Usata nella Dashboard e nei Report.
    """

    def __init__(self, parent, title, value, subtitle="", color=None):
        super().__init__(
            parent,
            fg_color=COLORS["bg_card"],
            corner_radius=SIZES["corner_radius"]
        )

        # Contenuto
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(padx=20, pady=20, fill="both", expand=True)

        # Titolo piccolo
        title_label = ctk.CTkLabel(
            content,
            text=title,
            font=get_font("small"),
            text_color=COLORS["text_secondary"]
        )
        title_label.pack(anchor="w")

        # Valore grande
        value_label = ctk.CTkLabel(
            content,
            text=str(value),
            font=get_font("display"),
            text_color=color or COLORS["text_primary"]
        )
        value_label.pack(anchor="w", pady=(5, 0))
        # Sottotitolo
        if subtitle:
            subtitle_label = ctk.CTkLabel(
                content,
                text=subtitle,
                font=get_font("small"),
                text_color=COLORS["text_secondary"]
            )
            subtitle_label.pack(anchor="w")


class DataCard(ctk.CTkFrame):
    """
    Card informativa per liste dettagliate (es. Appuntamenti, Transazioni).
    Supporta più righe di testo e allineamenti DX/SX.
    """

    def __init__(self, parent):
        super().__init__(
            parent,
            fg_color=COLORS["bg_card"],
            corner_radius=SIZES["corner_radius"],
            border_width=2,
            border_color=COLORS["bg_card"]
        )
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(padx=20, pady=25, fill="both", expand=True)
        self._click_command = None
        
        # Effetto Hover
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.content.bind("<Enter>", self._on_enter)
        self.content.bind("<Leave>", self._on_leave)

    def _on_enter(self, event=None):
        """Effetto hover: cambia colore di sfondo e aggiunge bordo."""
        if self._click_command:
            hover_color = "#F5F5F7" if ctk.get_appearance_mode() == "Light" else "#2C2C2E"
            self.configure(fg_color=hover_color, border_color=COLORS["accent"])

    def _on_leave(self, event=None):
        """Ritorna al colore originale."""
        self.configure(fg_color=COLORS["bg_card"], border_color=COLORS["bg_card"])

    def bind_click(self, command):
        """Associa un comando al click sulla card e su tutti i suoi figli."""
        self._click_command = command
        # Bind ricorsivo partendo dalla card stessa
        self._bind_recursive(self, command)

    def _bind_recursive(self, widget, command):
        widget.bind("<Button-1>", lambda e: command())
        # Propaga anche hover ai figli per evidenziare la card principale
        widget.bind("<Enter>", self._on_enter)
        widget.bind("<Leave>", self._on_leave)
        
        for child in widget.winfo_children():
            self._bind_recursive(child, command)

    def _apply_click_to_widget(self, widget):
        if self._click_command:
            widget.bind("<Button-1>", lambda e: self._click_command())
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)

    def add_title(self, text, color=None):
        label = ctk.CTkLabel(
            self.content,
            text=text,
            font=get_font("body_bold"),
            text_color=color or COLORS["text_primary"],
            height=30 # Altezza esplicita contro il clipping
        )
        label.pack(anchor="w", pady=(0, 12)) # Aumentato padding
        self._apply_click_to_widget(label)

    def add_detail(self, text, color=None):
        label = ctk.CTkLabel(
            self.content,
            text=text,
            font=get_font("small"),
            text_color=color or COLORS["text_secondary"],
            height=20 # Altezza minima per descenders
        )
        label.pack(anchor="w", pady=(10, 0))
        self._apply_click_to_widget(label)

    def add_detail_row(self, left_text, right_text, left_color=None, right_color=None):
        row = ctk.CTkFrame(self.content, fg_color="transparent")
        row.pack(fill="x", pady=(12, 0))

        lbl_left = ctk.CTkLabel(
            row,
            text=left_text,
            font=get_font("small"),
            text_color=left_color or COLORS["text_secondary"],
            height=22
        )
        lbl_left.pack(side="left")

        lbl_right = ctk.CTkLabel(
            row,
            text=right_text,
            font=get_font("button"),
            text_color=right_color or COLORS["text_secondary"],
            height=22
        )
        lbl_right.pack(side="right")
        
        self._apply_click_to_widget(row)
        self._apply_click_to_widget(lbl_left)
        self._apply_click_to_widget(lbl_right)