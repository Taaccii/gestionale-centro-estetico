"""
Form Dialog Base - Componente riutilizzabile per popup di input.
"""
import customtkinter as ctk 
from gui.theme import COLORS, SIZES, get_font

class BaseFormDialog(ctk.CTkToplevel):
    """
    PopUp modale per form di input.
    Classe base riutilizzabile per creare form di inserimento dati.
    """

    def __init__(self, parent, title):
        super().__init__(parent)

        self.title(title)
        self.geometry("450x400")
        # Centra la finestra sullo schermo
        self.update_idletasks()  # Aggiorna le dimensioni
        width = self.winfo_width()
        height = self.winfo_height()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.geometry(f"+{x}+{y}")
        self.configure(fg_color=COLORS["bg_dark"])

        # Rende la finestra modale bloccando la finestra principale
        self.transient(parent) # Associa al parent
        self.grab_set() # Blocca interazione con altre finestre

        # Variabile per salvare il risultato
        self.result = None
        self.fields = {}

        # Frame principale per i campi
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=(20, 10))

        # Frame per i pulsanti
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(fill="x", padx=20, pady=(0, 20))

        # Pulsante Annulla
        btn_cancel = ctk.CTkButton(
            self.button_frame,
            text="Annulla",
            fg_color=COLORS["btn_ghost"],
            hover_color=COLORS["bg_card"],
            text_color=COLORS["text_secondary"],
            command=self._on_cancel
        )
        btn_cancel.pack(side="left")

        # Pulsante Salva
        btn_save = ctk.CTkButton(
            self.button_frame,
            text="Salva",
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            text_color=COLORS["bg_dark"],
            command=self._on_save
        )
        btn_save.pack(side="right")

    
    def update_height(self):
        """
        Ridimensiona automaticamente la finestra misurando il contenuto reale.
        """
        # Forza un aggiornamento calcoli grafici senza scrivere
        self.update_idletasks()

        # Misura quanto sono alti i due frame principali
        content_h = self.content_frame.winfo_reqheight()
        button_h = self.button_frame.winfo_reqheight()

        # Aggiunge un po' di padding extra
        new_height = content_h + button_h + 90 

        # Imposta la geometria mantenendo la larghezza fissa 450
        self.geometry(f"450x{new_height}")

    def add_field(self, name, label_text, default_value=None):
        """
        Aggiunge un campo di input al form.
    
            Args:
            name: chiave per identificare il campo (es. 'nome')
            label_text: testo della label (es. 'Nome:')
        """
        # Label
        label = ctk.CTkLabel(
            self.content_frame,
            text=label_text,
            font=get_font("body"),
            text_color=COLORS["text_primary"]
        )
        label.pack(anchor="w", pady=(10, 2))

        # Campo input
        entry = ctk.CTkEntry(
            self.content_frame,
            font=get_font("body"),
            fg_color=COLORS["bg_card"],
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"]
        )
        entry.pack(fill="x", pady=(0, 5))

        if default_value:
            entry.insert(0, str(default_value))
            
        # Salva il riferimento
        self.fields[name] = entry

    def add_dropdown(self, name, label_text, options, add_command=None):
        """
        Aggiunge un menu a tendina con ricerca autocomplete integrata
    
            Args:
            name: nome del campo
            label_text: etichetta visualizzata
            options: lista di stringhe con le opzioni
        """
        # Label
        label = ctk.CTkLabel(
            self.content_frame,
            text=label_text,
            font=get_font("body"),
            text_color=COLORS["text_primary"]
        )
        label.pack(anchor="w", pady=(10,2))
        
        if add_command:
            container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
            container.pack(fill="x", pady=(0, 5))
            parent_widget = container # La combo andrà qui dentro
        else:
            parent_widget = self.content_frame # La combo va direttamente nel form

            # Dropdown (ComboBox)
        combo = ctk.CTkComboBox(
            parent_widget,
            values=options, # Lista
            font=get_font("body"),
            fg_color=COLORS["bg_card"],
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            #state="readonly" # Impedisce di scrivere testo a caso
        )

        # Logica di autocomplete
        # Imposta vuoto all'inizio
        combo.set("")

        if options:
            def filter_options(event):
                # Se premi tasti speciali (frecce, invio) non filtrare
                if event.keysym in ["Up", "Down", "Return", "Tab"]:
                    return
                typed = combo.get()

                # Se cancelli tutto nella ricerca, rimette tutte le opzioni
                if typed == "":
                    combo.configure(values=options)
                    return

                # Filtra Case-sensitive
                filtered = [item for item in options if typed.lower() in item .lower()]

                # Aggiorna la lista
                if filtered:
                    combo.configure(values=filtered)
                else:
                    # Se non trova nulla, lascia vuoto o mostra tutto
                    combo.configure(values=["Nessun risultato"])

                # Fora l'apertura del menu per mostrare i risultati
                try:
                    combo._dropdown_menu.tk_popup(
                        combo._entry.winfo_rootx(),
                        combo._entry.winfo_rooty() + combo._entry.winfo_height(),
                        0
                    )
                    
                    # Rimette il focus sulla scrittura con ritardo per forzarlo
                    combo._entry.after(100, combo._entry.focus_set)
                except: pass

            # Collega la tastiera ("KeyRelease" scatta dopo aver premuto un tasto)
            combo._entry.bind("<KeyRelease>", filter_options)


        # Posizionamento
        if add_command:
            # Combo a sinistra che si allarga
            combo.pack(side="left", fill="x", expand=True, padx=(0, 5))

            # Bottone "+" a destra
            btn_add = ctk.CTkButton(
                parent_widget,
                text="+",
                width=30,
                fg_color=COLORS["accent"],
                hover_color=COLORS['accent_hover'],
                command=add_command
            )
            btn_add.pack(side="right")
        else:
            combo.pack(fill="x", pady=(0, 5))

        self.fields[name] = combo

        
    def _on_cancel(self):
        self.result = None
        self.destroy()

    def _collect_data(self):
        """Raccoglie i dati"""
        self.result = {nome: entry.get() for nome, entry in self.fields.items()}

    def _on_save(self):
        self._collect_data()
        self.destroy()

    