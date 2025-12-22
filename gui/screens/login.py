import customtkinter as ctk 
from gui.theme import COLORS, get_font, ICONS
from gui.components.toast import ToastNotification
from django.contrib.auth import authenticate

class LoginScreen(ctk.CTkFrame):
    def __init__(self, parent, login_callback):
        # Inizializza il Frame
        super().__init__(parent, fg_color=COLORS["bg_dark"])
        self.login_callback = login_callback
        self.is_password_visible=False

        # Card centrale
        self.card = ctk.CTkFrame(
            self,
            width=400, 
            height=450, # Altezza fissa necessaria con pack_propagate(False)
            fg_color=COLORS["bg_card"],
            corner_radius=15,
            border_width=1,
            border_color=COLORS["border"]
        )
        self.card.pack_propagate(False) # Impedisce al contenuto di rimpicciolire la card
        # Centra la card allo schermo
        self.card.place(relx=0.5, rely=0.5, anchor="center")

        # Titolo
        self.label_title = ctk.CTkLabel(
            self.card,
            text=ICONS['accesso'],
            font=get_font("heading"),
            text_color=COLORS["text_primary"]
        )
        self.label_title.pack(pady=(40, 30))

        # Campi di testo

        # Username
        self.entry_user = ctk.CTkEntry(
            self.card,
            placeholder_text="Username",
            width=260,       
            height=45,
            font=get_font("body")
        )
        self.entry_user.pack(pady=(0, 15))


        # Password
        self.pwd_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.pwd_frame.pack(pady=(0, 30))

        # Spacer a sinistra invisibile per bilanciare il bottone occhio a destra
        # Calcolo: Button (30) + Padding (5) = 35
        spacer = ctk.CTkLabel(self.pwd_frame, text="", width=35)
        spacer.pack(side="left")

        self.entry_psw = ctk.CTkEntry(
            self.pwd_frame,
            placeholder_text="Password",
            show="*",
            width=260,
            height=45,
            font=get_font("body")
        )
        self.entry_psw.pack(side="left")

        # Bottone mostra password
        self.btn_show_psw = ctk.CTkButton(
            self.pwd_frame,
            text="👁️",
            width=30, # Ridotto per eleganza
            height=45,
            fg_color="transparent",
            text_color=COLORS["text_primary"],
            hover_color=COLORS["bg_dark"],
            command=self._toggle_password
        )
        self.btn_show_psw.pack(side="right", padx=(5, 0))

        # Checkbox Ricordami
        self.chk_remember = ctk.CTkCheckBox(
            self.card,
            text="Rimani Connesso",
            font=get_font("body"),
            fg_color=COLORS["success"],
            hover_color=COLORS["success_hover"],
            text_color=COLORS["text_primary"], # Leggermente più scuro del secondary
            command=self._on_remember_click
        )
        self.chk_remember.pack(pady=(0, 10))

        # Frame nascosto per le opzioni che appare se spunti la casella
        self.frame_options = ctk.CTkFrame(self.card, fg_color="transparent")
        
        # Menu dentro il frame
        self.remember_var = ctk.StringVar(value="30 Giorni")
        self.combo_options = ctk.CTkSegmentedButton(
            self.frame_options,
            values=["30 Giorni", "Per Sempre"],
            variable=self.remember_var,
            selected_color=COLORS["success"],
            selected_hover_color=COLORS["success_hover"],
            text_color=COLORS["text_primary"],
        )
        self.combo_options.pack()

        # Bottone Login
        self.btn_login = ctk.CTkButton(
            self.card,
            text="ACCEDI",
            width=250,
            height=40,
            font=get_font("button"),
            text_color=COLORS["bg_dark"],
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            command=self._attempt_login
        )
        self.btn_login.pack(pady=(0, 40))

        # Attiva tasto invio per confermare accesso
        self.entry_psw.bind("<Return>", lambda e: self._attempt_login())

    def _toggle_password(self):
        self.is_password_visible = not self.is_password_visible # Inverte
        
        if self.is_password_visible:
            self.entry_psw.configure(show="")
            self.btn_show_psw.configure(text="❌")
            self.btn_show_psw.configure(text_color=COLORS["accent"]) # Acceso
        else:
            self.entry_psw.configure(show="*")
            self.btn_show_psw.configure(text="👁️")
            self.btn_show_psw.configure(text_color=COLORS["text_primary"]) # Spento
    
    def _attempt_login(self):
        """Prova a loggarsi con Djando"""
        username = self.entry_user.get()
        password = self.entry_psw.get()

        # Validazione base
        if not username or not password:
            ToastNotification(self, "Inserisci tutti i dati!", color_key="warning")
            return

        # Controlla esistenza utente con Django
        user = authenticate(username=username, password=password)

        if user is not None:
            # Calcolo durata
            duration = "short"
            if self.chk_remember.get() == 1:
                val = self.remember_var.get()
                duration = "forever" if val == "Per Sempre" else "month"
            self.login_callback(user, duration)
        else:
            ToastNotification(self, "Credenziali Errate", color_key="error")
            self.entry_psw.delete(0, 'end') # pulisce il campo password


    def _on_remember_click(self):
        if self.chk_remember.get() == 1:
            # before=self.btn_login lo piazza SOPRA il bottone
            self.frame_options.pack(before=self.btn_login, pady=(0, 20))
        else:
            self.frame_options.pack_forget()