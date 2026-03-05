"""
Finestra principale dell'applicazione
"""
import os
import sys
from pathlib import Path

# --- FIX PER PYINSTALLER / CORE SETTINGS ---
# Questo blocco deve stare PRIMA di ogni altro import del progetto
if getattr(sys, 'frozen', False):
    # Se siamo dentro un eseguibile, aggiungiamo la cartella corrente al percorso di ricerca
    bundle_dir = Path(sys._MEIPASS)
    if str(bundle_dir) not in sys.path:
        sys.path.insert(0, str(bundle_dir))

# Diciamo a Django dove si trova esattamente il file delle impostazioni
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# IMPORTANTE: Forziamo l'import delle impostazioni per PyInstaller
import core.settings 
import django
django.setup()

# --- SAFETY NET: Assicura che l'utente admin esista sempre ---
# Utile sia in sviluppo che nella versione portable, garantisce
# che le credenziali admin/admin funzionino sempre.
def _ensure_admin_user():
    try:
        from django.contrib.auth.models import User
        admin = User.objects.filter(username='admin').first()
        if admin is None:
            # Crea l'utente admin se non esiste
            User.objects.create_superuser('admin', 'admin@example.com', 'admin')
        elif not admin.check_password('admin'):
            # Resetta la password se è stata cambiata/corrotta
            admin.set_password('admin')
            admin.save()
    except Exception as e:
        print(f"[WARN] Impossibile verificare utente admin: {e}")

_ensure_admin_user()

# --- DEMO DATA: Popola il database al primo avvio se vuoto ---
try:
    from core.utils.demo_manager import populate_demo_data_if_empty
    populate_demo_data_if_empty()
except Exception as e:
    print(f"[WARN] Impossibile generare dati demo: {e}")

from gui.components.toast import ToastNotification
import customtkinter as ctk
from gui.theme import COLORS, SIZES, ICONS, APPEARANCE_MODE, get_font
from gui.screens.dashboard import DashboardScreen
from gui.screens.services import ServicesScreen
from gui.screens.staff import StaffScreen
from gui.screens.clients import ClientsScreen
from gui.screens.reports import ReportsScreen
from gui.screens.cash import CashScreen
from gui.screens.notifications import NotificationsScreen
from gui.screens.calendar import CalendarScreen
from gui.screens.appointments import AppointmentsScreen
from gui.screens.login import LoginScreen
from gui.screens.settings import SettingsScreen
from django.contrib.auth.models import User
from core.utils.session import save_session, load_session, clear_session

# Configurazione CostumTkinter
ctk.set_appearance_mode(APPEARANCE_MODE)
ctk.set_default_color_theme("dark-blue")

class App(ctk.CTk):
    """
    Finestra principale del gestionale.
    """

    def __init__(self):
        super().__init__()

        # Configurazione finestra
        self.title("Centro Estetico - Gestionale")
        self.geometry("1400x800")
        # Centra la finestra sullo schermo
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.geometry(f"+{x}+{y}")
        self.minsize(1200, 700)

        # Dizionario per nascondere schermi e fare caching
        self._screens = {}

        # Colore sfondo
        self.configure(fg_color=COLORS["bg_dark"])

        # Stato utente
        self.current_user = None

        # Controllo sessione per Avvio schermata login
        user_id = load_session()
        if user_id:
            try:
                # Se c'è un ID valido recupera l'utente ed entra diretto
                self.current_user = User.objects.get(pk=user_id)
                self._create_layout()
                ToastNotification(self, f"Bentornato {self.current_user.username}!", color_key="success")
            except User.DoesNotExist:
                self._show_login()
        else:
            self._show_login()

    def _show_login(self):
        """Pulisce tutto e mostra il login"""

        # Distrugge eventuali widget presenti e resetta la cache degli schermi
        self._screens = {}
        for widget in self.winfo_children():
            widget.destroy()

        login_screen = LoginScreen(self, login_callback=self.login)
        login_screen.pack(fill="both", expand=True) 

    def login(self, user, duration="short"):
        """Chiamato quando il login ha successo"""
        self.current_user = user

        save_session(user.id, duration)
        # Pulisce la schermata di login e resetta la cache degli schermi
        self._screens = {}
        for widget in self.winfo_children():
            widget.destroy()

        # Costruisce la vera interfaccia
        self._create_layout()


    def _create_layout(self):
        """Crea il layout con sidebar e area contenuto."""

        # Sidebar sinistra
        self.sidebar = ctk.CTkFrame(
            self,
            width=SIZES["sidebar_width"],
            corner_radius=0,
            fg_color=COLORS["bg_sidebar"]
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False) # Mantiene larghezza fissa
        
        # Area contenuto principale
        self.content_area = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=COLORS["bg_dark"]
        )
        self.content_area.pack(side="right", fill="both", expand=True)

        # Crea elemeni sidebar
        self._create_sidebar()

        # Mostra dashboard di default
        self._show_dashboard()

    def _create_sidebar(self):
        """Crea i pulsanti di navigazione nella sidebar."""

        # Logo/Titolo
        logo_label = ctk.CTkLabel(
            self.sidebar,
            text="✨ Centro Estetico",
            font=get_font("heading"),
            text_color=COLORS["accent"]
        )
        logo_label.pack(pady=(30,40), padx=20)

        # Voci del menu
        menu_items = [
            ("dashboard", "Dashboard"),
            ("calendar", "Calendario"),
            ("clients", "Clienti"),
            ("staff", "Staff"),
            ("services", "Servizi"),
            ("cash", "Cassa"),
            ("reports", "Report"),
            ("notifications", "Notifiche"),
            ("history", "Storico App."),
            ("settings", "Impostazioni"),

            
        ]

        for icon_key, label in menu_items:
            self._create_menu_button(icon_key,label)

        # Spacer: elemento invisibile che "occupa spazio" per spingere altri elementi in posizione.
        spacer = ctk.CTkLabel(self.sidebar, text="") # Label vuota che si ESPANDE e non consuma risorse
        spacer.pack(expand=True)

        # Switch Tema
        self.theme_switch = ctk.CTkSwitch(
            self.sidebar,
            text="Tema Scuro",
            command=self._toggle_theme,
            onvalue="Dark",
            offvalue="Light",
            font=get_font("body"),
            progress_color=COLORS["accent"]
        )
        self.theme_switch.pack(pady=(0, 20), padx=20, anchor="w")
        self.theme_switch.select() # Default Dark

        # Logout in fondo
        self._create_menu_button("logout", "Esci", is_logout=True)

    def _create_menu_button(self, icon_key, label, is_logout=False):
        """Crea un pulsante del menu."""
        btn = ctk.CTkButton(
            self.sidebar,
            text=f"{ICONS[icon_key]} {label}",
            font=get_font("button"),
            fg_color="transparent",
            hover_color=COLORS["sidebar_hover"],
            text_color=COLORS["text_secondary"] if not is_logout else COLORS["error"],
            anchor="w",
            height=45,
            corner_radius=SIZES["corner_radius"],
            command=lambda k=icon_key: self._on_menu_click(k)
        )
        btn.pack(fill="x", padx=15, pady=5)

    def _on_menu_click(self, menu_key):
        """Gestisce il click su una voce del menu."""
        
        # Nasconde lo schermo precedente se esiste invece di distruggerlo
        for widget in self.content_area.winfo_children():
            widget.pack_forget() # Lo nasconde e lo tiene in memoria (caching)
        
        # Mostra la schermata corrispondente (creandola se non esiste o recuperandola dalla cache)
        if menu_key == "dashboard":
            self._show_dashboard()
        elif menu_key == "calendar":
            self._show_calendar()
        elif menu_key == "services":
            self._show_services()
        elif menu_key == "clients":
            self._show_clients()
        elif menu_key == "staff":
            self._show_staff()
        elif menu_key == "reports":
            self._show_reports()
        elif menu_key == "history":
            self._show_appointments()
        elif menu_key == "cash":
            self._show_cash()
        elif menu_key == "settings":
            self._show_settings()
        elif menu_key == "notifications":
            self._show_notifications()
        elif menu_key == "logout":
            clear_session()
            self.current_user = None
            self._show_login()
    
    def _show_services(self):
        """Mostra la schermata Servizi"""
        if "services" not in self._screens:
            self._screens["services"] = ServicesScreen(self.content_area)
        screen = self._screens["services"]
        screen.pack(fill="both", expand=True)
        if hasattr(screen, '_load_data'):
            screen._load_data()
    
    def _show_clients(self):
        """Mostra la schermata Clienti"""
        if "clients" not in self._screens:
            self._screens["clients"] = ClientsScreen(self.content_area)
        screen = self._screens["clients"]
        screen.pack(fill="both", expand=True)
        if hasattr(screen, '_load_data'):
            screen._load_data()

    def _show_reports(self):
        """Mostra la schermata Reports"""
        if "reports" not in self._screens:
            self._screens["reports"] = ReportsScreen(self.content_area)
        screen = self._screens["reports"]
        screen.pack(fill="both", expand=True)
        if hasattr(screen, '_load_data'):
            screen._load_data()
    
    def _show_cash(self):
        """Mostra la schermata Cassa"""
        if "cash" not in self._screens:
            self._screens["cash"] = CashScreen(self.content_area)
        screen = self._screens["cash"]
        screen.pack(fill="both", expand=True)
        if hasattr(screen, '_load_data'):
            screen._load_data()

    def _show_staff(self):
        """Mostra la schermata Staff."""
        if "staff" not in self._screens:
            self._screens["staff"] = StaffScreen(self.content_area)
        screen = self._screens["staff"]
        screen.pack(fill="both", expand=True)
        if hasattr(screen, '_load_data'):
            screen._load_data()

    def _show_dashboard(self):
        """Mostra la Dashboard"""
        if "dashboard" not in self._screens:
            self._screens["dashboard"] = DashboardScreen(self.content_area)
        screen = self._screens["dashboard"]
        screen.pack(fill="both", expand=True)
        if hasattr(screen, '_load_data'):
            screen._load_data()
    
    def _show_calendar(self):
        """Mostra il Calendario"""
        if "calendar" not in self._screens:
            self._screens["calendar"] = CalendarScreen(self.content_area)
        screen = self._screens["calendar"]
        screen.pack(fill="both", expand=True)
        # Il calendario usa _load_appointments invece di _load_data
        if hasattr(screen, '_load_appointments'):
            screen._load_appointments()

    def _show_settings(self):
        """Mostra le Impostazioni"""
        if "settings" not in self._screens:
            self._screens["settings"] = SettingsScreen(self.content_area)
        screen = self._screens["settings"]
        screen.pack(fill="both", expand=True)
        # Impostazioni potrebbe non aver bisogno di refresh, ma per sicurezza:
        if hasattr(screen, '_load_data'):
            screen._load_data()

    def _show_appointments(self):
        """Mostra lo storico appuntamenti"""
        if "appointments" not in self._screens:
            self._screens["appointments"] = AppointmentsScreen(self.content_area)
        screen = self._screens["appointments"]
        screen.pack(fill="both", expand=True)
        if hasattr(screen, '_load_data'):
            screen._load_data()

    def _show_notifications(self):
        """Mostra la schermata Centro Notifiche"""
        if "notifications" not in self._screens:
            self._screens["notifications"] = NotificationsScreen(self.content_area)
        screen = self._screens["notifications"]
        screen.pack(fill="both", expand=True)
        if hasattr(screen, '_load_data'):
            screen._load_data()

    def _toggle_theme(self):
        """Cambia il tema dell'applicazione."""
        mode = self.theme_switch.get()
        ctk.set_appearance_mode(mode)
        
        # Aggiorna il testo dello switch
        new_text = "Tema Scuro" if mode == "Dark" else "Tema Chiaro"
        self.theme_switch.configure(text=new_text)
        
if __name__ == "__main__":
    app = App()
    app.mainloop()