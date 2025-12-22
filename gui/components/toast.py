import customtkinter as ctk
from gui.theme import COLORS, get_font

class ToastNotification(ctk.CTkFrame):
    """
    Notifica Toast implementata come Frame interno.
    Si sovrappone al contenuto usando .place(), evitando problemi di finestre OS.
    """
    def __init__(self, parent, message, color_key="success", duration=2500):
        # Inizializza il Frame
        super().__init__(
            parent,
            fg_color=COLORS.get(color_key, COLORS["accent"]),
            corner_radius=20,
            border_width=0
        )

        # Label del messaggio
        self.label = ctk.CTkLabel(
            self,
            text=message,
            font=get_font("body"),
            text_color="#FFFFFF", # Bianco fisso per contrasto su colori accesi (Verde/Rosso)
            padx=20,
            pady=10
        )
        self.label.pack()

        # Posizionamento: In alto al centro del parent (relativo)
        # relx=0.5 (centro orizzontale), rely=0.05 (5% dall'alto)
        self.place(relx=0.5, rely=0.05, anchor="n")
        
        # Porta in primo piano sopra gli altri widget del frame
        self.lift()

        # Auto-distruzione
        self.after(duration, self._destroy_toast)

    def _destroy_toast(self):
        try:
            self.destroy()
        except:
            pass
