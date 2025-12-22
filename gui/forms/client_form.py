"""Form inserimento Cliente"""

from gui.forms.base_form import BaseFormDialog
from tkinter import messagebox
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from anagrafica.models import Cliente

class ClientFormDialog(BaseFormDialog):
    
    def __init__(self, parent):
        super().__init__(parent, "Nuovo Cliente")

        self.add_field("nome", "Nome:")
        self.add_field("cognome", "Cognome:")
        self.add_field("telefono", "Telefono:")
        self.add_field("email", "Email:")
        self.add_field("note", "Note:")
        
        self.update_height()

    def _on_save(self):
        self._collect_data()

        # Recuperiamo nome e cognome
        nome = self.result.get("nome", "").strip().title()
        cognome = self.result.get("cognome", "").strip().title()

        # Aggiorna i dati puliti nel result
        self.result['nome'] = nome
        self.result['cognome'] = cognome

        # Controllo duplicati
        duplicati = Cliente.objects.filter(nome=nome, cognome=cognome)

        if duplicati.exists():
            msg = f"Esiste già un cliente '{nome} {cognome}'.\nVuoi procedere comunque?\n(Consiglio: Aggiungi un dettaglio nelle note)"
            conferma = messagebox.askyesno("Cliente Esistente", msg)
            if not conferma:
                return # Interrompi e non salvare nulla

        # Salvataggio e Return ID
        nuovo_cliente = Cliente.objects.create(**self.result)
        self.result['id'] = nuovo_cliente.id

        self.destroy()