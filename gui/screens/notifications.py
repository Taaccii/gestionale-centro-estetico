import customtkinter as ctk
from gui.components.base import BaseScreen, DataCard
from gui.theme import COLORS, SIZES, ICONS, get_font
from appuntamenti.services import NotificationService
from appuntamenti.models import LogNotifica
from django.utils import timezone

class NotificationsScreen(BaseScreen):
    """Schermata per la gestione e visualizzazione delle notifiche inviate."""

    def __init__(self, parent):
        super().__init__(
            parent,
            title="Centro Notifiche",
            icon=ICONS["notifications"],
            button_text="Invia Promemoria Manuali"
        )

    def _create_layout(self):
        """Override del layout per aggiungere la sezione dei log in alto."""
        super()._create_layout()
        
        # Sgancia la lista temporaneamente per inserire i contenuti sopra
        self.list_container.pack_forget()

        # Intestazione informativa (Spostata in alto e ingrandita)
        info_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=SIZES["corner_radius"])
        info_frame.pack(fill="x", padx=30, pady=(0, 20))
        
        info_label = ctk.CTkLabel(
            info_frame,
            text=f"{ICONS['notifications']} Centro di Controllo Promemoria Automatici",
            font=get_font("heading"),
            text_color=COLORS["accent"],
            justify="left"
        )
        info_label.pack(anchor="w", padx=20, pady=(15, 5))

        desc_label = ctk.CTkLabel(
            info_frame,
            text="Il sistema scansiona gli appuntamenti e invia automaticamente Email e SMS 24 ore prima dell'inizio.\nUsa il pulsante in alto a destra per forzare l'invio manuale per i test.",
            font=get_font("body"),
            text_color=COLORS["text_secondary"],
            justify="left"
        )
        desc_label.pack(anchor="w", padx=20, pady=(0, 15))

        # Riaggancia la lista
        self.list_container.pack(fill="both", expand=True, padx=30, pady=(0, 5))

    def _on_add_new(self):
        """Trigger manuale per l'elaborazione dei promemoria."""
        count = NotificationService.process_reminders()
        from gui.components.toast import ToastNotification
        
        if count > 0:
            msg = f"Elaborazione completata: inviati {count * 2} messaggi (Email + SMS)."
            type_msg = "success"
        else:
            msg = "Nessun appuntamento trovato nelle prossime 24 ore che richieda un promemoria."
            type_msg = "warning"
            
        self.notification = ToastNotification(self, message=msg, color_key=type_msg)
        self._load_data()

    def _load_data(self):
        """Carica i log delle notifiche."""
        # Pulisce la lista
        self.list_container.clear()
            
        logs = NotificationService.get_recent_notifications(limit=20)
        
        if not logs:
            self.list_container.show_empty_message("Nessun invio registrato al momento.")
            return

        for log in logs:
            self._create_log_card(log)

    def _create_log_card(self, log):
        """Crea una card per il log della notifica."""
        card = DataCard(self.list_container)
        card.pack(fill="x", pady=5)
        
        tipo_icon = ICONS["email"] if log.tipo == "email" else ICONS["phone"]
        data_invio = log.data_ora_invio.strftime("%d/%m/%Y %H:%M:%S")
        
        # Titolo: Destinatario e Tipo
        card.add_title(f"{tipo_icon} {log.tipo.upper()} a {log.destinatario}")
        
        # Dettaglio 1: Data invio e Appuntamento
        card.add_detail(f"{ICONS['calendar']} Inviato il: {data_invio}  •  {ICONS['staff']} Rif: {log.appuntamento}")
        
        # Dettaglio 2: Messaggio (Troncato se troppo lungo)
        msg_preview = log.messaggio[:80] + "..." if len(log.messaggio) > 80 else log.messaggio
        card.add_detail_row(
            f"{ICONS['notes']} {msg_preview}",
            "INVIATO",
            right_color=COLORS["success"]
        )
