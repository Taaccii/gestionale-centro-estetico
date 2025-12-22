import customtkinter as ctk 
from tkinter import filedialog
from gui.theme import COLORS, ICONS, get_font
from gui.components.base import BaseScreen, DataCard
from gui.components.toast import ToastNotification
from core.utils.backup import create_backup, restore_backup
from tkinter import messagebox

class SettingsScreen(BaseScreen):
    def __init__(self, parent):
        super().__init__(parent, title="Impostazioni", icon=ICONS["settings"], button_text=None)

    def _load_data(self):
        """Disegna le sezioni delle impostazioni con ricerca intelligente."""
        self.list_container.clear()
        query = self.search_query.lower().strip()

        # --- SEZIONE BACKUP & RIPRISTINO ---
        if not query or any(x in query for x in ["back", "up", "salva", "dati", "ripristin"]):
            card = DataCard(self.list_container)
            card.pack(fill="x", pady=10)

            card.add_title(f"{ICONS['backup']} Backup & Ripristino")
            card.add_detail("Salva i tuoi dati al sicuro o ripristina una versione precedente.")

            # Container bottoni
            btn_frame = ctk.CTkFrame(card.content, fg_color="transparent")
            btn_frame.pack(fill="x", pady=(15, 0))

            # Bottoni
            ctk.CTkButton(
                btn_frame, text="Crea Backup Locale",
                fg_color=COLORS["success"], hover_color=COLORS["success_hover"],
                text_color=COLORS["text_on_accent"], width=150,
                command=self._on_backup_local
            ).pack(side="left", padx=(0, 10))

            ctk.CTkButton(
                btn_frame, text="Salva con nome...",
                fg_color=COLORS["accent"], hover_color=COLORS['accent_hover'],
                text_color=COLORS["text_on_accent"], width=150,
                command=self._on_backup_custom
            ).pack(side="left")

            ctk.CTkButton(
                btn_frame, text="Ripristina da file",
                fg_color=COLORS["error"], hover_color="#800000",
                text_color=COLORS["text_on_accent"], width=150,
                command=self._on_restore
            ).pack(side="right")

        # --- SEZIONE INFORMAZIONI SISTEMA ---
        if not query or any(x in query for x in ["info", "versione", "sistema", "centro"]):
            card_info = DataCard(self.list_container)
            card_info.pack(fill="x", pady=10)

            card_info.add_title(f"{ICONS['dashboard']} Informazioni Sistema")
            card_info.add_detail("Gestione Centro Estetico v2.0")
            
            card_info.add_detail_row("Versione Database", "Django + SQLite 3")
            card_info.add_detail_row("Interfaccia Grafica", "CustomTkinter Modern UI")
            card_info.add_detail_row("Licenza", "Proprietà Riservata")

    
    def _on_backup_local(self):
        """Crea backup nella cartella predefinita"""
        try:
            path = create_backup()
            ToastNotification(self, f"Backup creato: {path.split('/')[-1]}", color_key="success")

        except Exception as e:
            ToastNotification(self, f"Errore: {str(e)}", color_key="error")

    def _on_backup_custom(self):
        """Apre finestra di salvataggio"""
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            title="Salva Backup"
        )
        if path:
            try:
                create_backup(custom_path=path)
                ToastNotification(self, "Backup esportato con successo!", color_key="success")
            except Exception as e:
                ToastNotification(self, f"Errore: {str(e)}", color_key="error")
        
    
    def _on_restore(self):
        """Apre finestra per scegliere file da ripristinare"""
        path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")],
            title="Seleziona Backup da ripristinare"
        )
        if path:
            # Check di sicurezza
            confirm = messagebox.askyesno(
                "Conferma Ripristino",
                "ATTENZIONE: Il ripristino cancellerà i dati attuali e caricherà quelli del backup.\n\nSei sicuro di voler procedere?",
                icon="warning"
            )
            
            if confirm:
                try:
                    if restore_backup(path):
                        ToastNotification(self, "Ripristino completato! Riavvia l'app.", color_key="success")
                    else:
                        ToastNotification(self, "File non valido", color_key="error")
                except Exception as e:
                    ToastNotification(self, f"Errore Ripristino: {str(e)}", color_key="error")
