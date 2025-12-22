from gui.forms.base_form import BaseFormDialog
from gui.forms.client_form import ClientFormDialog
from anagrafica.models import Cliente, Dipendente
from servizi.models import Servizio
import customtkinter as ctk
from datetime import datetime, date
from django.utils import timezone
from appuntamenti.models import Appuntamento, DettaglioAppuntamento
from gui.theme import COLORS, get_font, ICONS
from gui.components.toast import ToastNotification
from tkinter import messagebox
from django.core.exceptions import ValidationError

class AppointmentFormDialog(BaseFormDialog):

    def _build_clienti_map(self):
        """Costruisce la mappa {Nome Visualizzato: Oggetto Cliente} gestendo gli omonimi"""
        clienti = Cliente.objects.all()
        mappa = {}

        # Conta quante volte appare ogni combinazione "Nome Cognome"
        counts = {}
        for c in clienti:
            full_name = f"{c.nome} {c.cognome}"
            counts[full_name] = counts.get(full_name, 0) +1

        # Costruisce etichette
        for c in clienti:
            full_name = f"{c.nome} {c.cognome}"

            # Se è unico = Solo nome e cognome
            if counts[full_name] == 1:
                label = full_name
            else:
                # Se è duplicato = Nome + Note o ID
                dettaglio = c.note if c.note else f"ID {c.id}"
                label = f"{full_name} ({dettaglio})"

            mappa[label] = c

        return mappa

    def __init__(self, parent, initial_date=None, initial_staff=None, initial_time=None, appointment=None):

        # Cambio del titolo dinamico
        title = "Modifica Appuntamento" if appointment else "Nuovo Appuntamento"
        super().__init__(parent, title=title)

        self.appointment = appointment

        # Caricamento Dati e Creazione Mappe (ID Mapping)
        self.clienti_map = self._build_clienti_map()
        self.servizi_map = {f"{s.nome} ({s.durata_minuti}m) € {s.prezzo}": s for s in Servizio.objects.all()}
        self.staff_map = {f"{d.nome} {d.cognome}": d for d in Dipendente.objects.all()}

        # Creazione Campi (usando le chiavi delle mappe)
        self.add_dropdown("cliente", "Cliente", list(self.clienti_map.keys()), add_command=self._open_add_client)

        # Selettore Master per aggiungere servizi
        self.add_dropdown("selector_service", "Aggiungi Servizio", list(self.servizi_map.keys()))
        
        # Configura la combo per agire subito quando selezioni
        self.fields['selector_service'].configure(command=self._add_chip)
        self.fields['selector_service'].set("Seleziona perr aggiungere...")

        # Area dopo compaiono i "Chip" (Tag)
        
        ctk.CTkLabel(self.content_frame, text="Servizi Selezionati:", font=get_font("body"),
        text_color=COLORS["text_secondary"]).pack(anchor="w", pady=(5, 0))

        self.chips_container = ctk.CTkFrame(self.content_frame, fg_color=COLORS["bg_card"], height=100)
        self.chips_container.pack(fill="x", pady=5)

        # Lista dati veri (i nomi dei servizi scelti)
        self.selected_services = []

        self.add_dropdown("dipendente", "Dipendente", list(self.staff_map.keys()))

        # Campo data e ora (Pre-compilata)
        default_date = initial_date.strftime("%d/%m/%Y") if initial_date else date.today().strftime("%d/%m/%Y")
        self.add_field("data", "Data (GG/MM/AAAA)", default_value=default_date)

        # Dropdown con orari di 30 minuti
        orari = []
        for h in range(8, 20):
            orari.append(f"{h:02d}:00")
            orari.append(f"{h:02d}:30")
        
        self.add_dropdown("ora", "Ora Inizio", orari)

        # Stato (Sempre visibile)
        stati = [choice[1] for choice in Appuntamento.STATO_CHOICES]
        self.add_dropdown("stato", "Stato Appuntamento", stati)
        self.fields['stato'].set("Prenotato")

        if appointment:
            # Mostra campo motivo se annullato
            if appointment.stato == 'annullato':
                self.add_field("motivo_annullamento", "Motivo Annullamento", default_value=appointment.motivo_annullamento or "")

        # Note
        self.add_field("note", "Note (Opzionale)")

        # Logica Pre-Compilazione
        if appointment:
            # Trova Cliente (Cerca nella mappa chi ha lo stesso ID)
            target_id = appointment.cliente.id
            for label, cliente in self.clienti_map.items():
                if cliente.id == target_id:
                    self.fields['cliente'].set(label)
                    break
           
            # Trova Dipendente
            for key, obj in self.staff_map.items():
                if obj.id == appointment.dipendente.id:
                    self.fields['dipendente'].set(key)
                    break
                    
            # Carica TUTTI i servizi usando la mappa per trovare i nomi esatti
            for dettaglio in appointment.dettagli.all():
                target_id = dettaglio.servizio.id
                
                # Cerca nella mappa quale "etichetta" corrisponde a questo ID
                for label, obj in self.servizi_map.items():
                    if obj.id == target_id:
                        self._add_chip(label)
                        break

            if appointment.note:
                self.fields['note'].delete(0, 'end')
                self.fields['note'].insert(0, appointment.note)

        else:
            # Fallback se appointment è None
            if initial_staff:
                for nome, obj in self.staff_map.items():
                    if obj.id == initial_staff.id:
                        self.fields['dipendente'].set(nome)
                        break

            if initial_time:
                self.fields['ora'].set(initial_time)

        # Svuota il frame pulsanti della classe base per avere controllo totale
        for widget in self.button_frame.winfo_children():
            widget.destroy()

        # Gruppo Sinistra: Azioni Destruttive/Stato
        if appointment:
            # Tasto Elimina
            self.btn_delete = ctk.CTkButton(
                self.button_frame,
                text="Elimina",
                width=100,
                fg_color=COLORS["error"],
                hover_color="#B00020",
                command=self._on_delete
            )
            self.btn_delete.pack(side="left", padx=(0, 10))

            # Tasto Annulla Appuntamento
            if appointment.stato != 'annullato':
                self.btn_cancel_app = ctk.CTkButton(
                    self.button_frame,
                    text="Annulla App.",
                    width=120,
                    fg_color=COLORS["warning"],
                    hover_color="#CC8800",
                    text_color=COLORS["bg_dark"],
                    command=self._on_cancel_appointment
                )
                self.btn_cancel_app.pack(side="left", expand=True)

        # Gruppo Destra: Azioni Standard
        self.btn_save = ctk.CTkButton(
            self.button_frame,
            text="Salva",
            width=100,
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            text_color=COLORS["bg_dark"],
            command=self._on_save
        )
        self.btn_save.pack(side="right")
        
        # Mappa inversa per gli stati (da Label a Chiave DB)
        self.reverse_stati = {choice[1]: choice[0] for choice in Appuntamento.STATO_CHOICES}
        if appointment:
            current_label = [choice[1] for choice in Appuntamento.STATO_CHOICES if choice[0] == appointment.stato][0]
            self.fields['stato'].set(current_label)

        self.update_height()

    def _on_save(self):
        try:
            # Recupera i dati dal form
            nome_cliente = self.fields['cliente'].get()
            nome_staff = self.fields['dipendente'].get()
            data_str = self.fields['data'].get()
            ora_str = self.fields['ora'].get()

            # 1. Validazione Campi Obbligatori
            if not nome_cliente or not nome_staff or not data_str or not ora_str:
                self.notification = ToastNotification(self, "Compila tutti i campi!", color_key="warning")
                return

            if not self.selected_services:
                self.notification = ToastNotification(self, "Seleziona almeno un servizio!", color_key="warning")
                return

            # 2. Verifica esistenza nei dizionari (evita KeyError)
            if nome_cliente not in self.clienti_map:
                self.notification = ToastNotification(self, "Cliente non valido", color_key="error")
                return
            if nome_staff not in self.staff_map:
                self.notification = ToastNotification(self, "Dipendente non valido", color_key="error")
                return

            cliente = self.clienti_map[nome_cliente]
            dipendente = self.staff_map[nome_staff]

            # 3. Parsing Data
            try:
                data_ora_inizio = datetime.strptime(f"{data_str} {ora_str}", "%d/%m/%Y %H:%M")
            # Data AWARE che conosce il fuso orario
                data_ora_inizio = timezone.make_aware(data_ora_inizio)
            except ValueError:
                self.notification = ToastNotification(self, "Formato Data/Ora errato!", color_key="error")
                return

            # SALVA nel DB
            
            # Crea o aggiorna appuntamento
            if self.appointment:
                app = self.appointment
                app.cliente = cliente
                app.dipendente = dipendente
                app.data_ora_inizio = data_ora_inizio
                app.note = self.fields['note'].get()
                
                # Aggiorna Stato se presente
                if 'stato' in self.fields:
                    app.stato = self.reverse_stati.get(self.fields['stato'].get(), 'prenotato')
                
                if 'motivo_annullamento' in self.fields:
                    app.motivo_annullamento = self.fields['motivo_annullamento'].get()
                
                app.save()

                # Pulisce i vecchi servizi per salvarli da zero
                app.dettagli.all().delete()

            else:
                app = Appuntamento.objects.create(
                    cliente=cliente,
                    dipendente=dipendente,
                    data_ora_inizio=data_ora_inizio,
                    data_ora_fine=data_ora_inizio, # Provvisorio per gestire i dati
                    stato='prenotato',
                    note=self.fields['note'].get()
                )

            # Salva i nuovi servizi
            for nome_servizio_str in self.selected_services:
                servizio = self.servizi_map[nome_servizio_str]

                DettaglioAppuntamento.objects.create(
                    appuntamento=app,
                    servizio=servizio,
                    prezzo_finale=servizio.prezzo,
                    durata_effettiva=servizio.durata_minuti
                )

            # 3) Ricalcola la fine esatta in base alla durata del servizio
            app.aggiorna_data_fine()

            # --- CONTROLLO SOVRAPPOSIZIONI (ALERT) ---
            conflicts = app.get_appuntamenti_sovrapposti()
            if conflicts:
                # Se ci sono conflitti, mostra un alert dettagliato
                msg = f"{ICONS['alert']} SOVRAPPOSIZIONE! {dipendente.nome} è già occupato:\n"
                for c in conflicts:
                    ora_c = c.data_ora_inizio.strftime("%H:%M")
                    msg += f"• {ora_c} con {c.cliente}\n"
                
                # Rollback se era un nuovo appuntamento
                if not self.appointment:
                    app.delete()
                
                self.notification = ToastNotification(self, msg, color_key="error")
                return

            # Se tutto ok, procedi
            msg = "Modifica salvata!" if self.appointment else "Nuovo appuntamento creato!"
            self.result = {"type": "success", "message": msg}
            self.destroy()

        except ValidationError as e:
            # Gestione errori di validazione generici di Django
            error_msg = str(e)
            if hasattr(e, 'message_dict'):
                error_msg = list(e.message_dict.values())[0][0]
            
            if not self.appointment and 'app' in locals():
                app.delete()
                
            self.notification = ToastNotification(self, error_msg, color_key="error")
            return # Interrompe il salvataggio per poter correggere l'errore

        except Exception as e:
            print(f"Errore nel salvataggio: {e}")
            self.notification = ToastNotification(self, f"Errore: {str(e)}", color_key="error")


    def _on_delete(self):
        if not self.appointment:
            return

            # Pop Up di conferma eliminazione
        conferma = messagebox.askyesno(
            "Conferma Eliminazione",
            "Sei sicuro di voler eliminare questo appuntamento?\nL'operazione è irreversibile."
        )

        if conferma:
            self.appointment.delete()
            self.result = {"type": "error", "message": "Appuntamento Eliminato!"}
            self.destroy()

    def _on_cancel_appointment(self):
        """Gestisce l'annullamento rapido dell'appuntamento con richiesta motivo."""
        from tkinter import simpledialog
        
        motivo = simpledialog.askstring(
            "Annullamento Appuntamento", 
            "Inserisci il motivo dell'annullamento:",
            parent=self
        )
        
        if motivo is not None: # Se non ha premuto 'Cancel' nel mini-dialog
            self.appointment.stato = 'annullato'
            self.appointment.motivo_annullamento = motivo
            self.appointment.save()
            
            self.result = {"type": "warning", "message": "Appuntamento Annullato!"}
            self.destroy()

            
    
    def _open_add_client(self):
        dialog = ClientFormDialog(self)
        self.wait_window(dialog)

        if dialog.result:
            # Ricarica tutti i clienti per avere anche quello nuovo e aggiorna la mappa interna
            self.clienti_map = self._build_clienti_map()
            self.fields['cliente'].configure(values=list(self.clienti_map.keys()))

            # trova la chiave giusta per il nuovo ID (Reverse Lookup)
            nuovo_id = dialog.result['id']
            for label, cliente in self.clienti_map.items():
                if cliente.id == nuovo_id:
                    self.fields['cliente'].set(label)
                    break

    def _add_chip(self, selection):
            """Crea un chip visivo per il servizio selezionato"""
            if selection in self.selected_services or selection == "Seleziona per aggiungere...":
                return # Evita duplicati o click a vuoto

            # Aggiunge alla lista logica
            self.selected_services.append(selection)

            # Crea il Chip Visivo (Un frame colorato)
            chip = ctk.CTkFrame(self.chips_container, fg_color=COLORS["accent"], corner_radius=10)
            chip.pack(fill="x", pady=2, padx=5)

            # Label Nome
            ctk.CTkLabel(chip, text=selection, text_color=COLORS["bg_dark"]).pack(side="left", padx=10)

            # Bottone X
            ctk.CTkButton(
                chip, 
                text="✕", 
                width=30, 
                fg_color="transparent", 
                text_color=COLORS["bg_dark"],
                hover_color=COLORS["accent_hover"],
                command=lambda: self._remove_chip(selection, chip)
            ).pack(side="right", padx=5)

            # Reset della tendina
            self.fields['selector_service'].set("Seleziona per aggiungere...")

    
    def _remove_chip(self, selection, chip_widget):
        self.selected_services.remove(selection) # Via dalla lista
        chip_widget.destroy() # Via dalla vista