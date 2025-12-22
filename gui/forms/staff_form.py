from gui.forms.base_form import BaseFormDialog

import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from anagrafica.models import Dipendente

class StaffFormDialog(BaseFormDialog):
    def __init__(self, parent, staff=None):
        self.staff = staff
        title = "Modifica Dipendente" if staff else "Nuovo Dipendente"
        super().__init__(parent, title)

        self.add_field("nome", "Nome:", default_value=staff.nome if staff else "")
        self.add_field("cognome", "Cognome:", default_value=staff.cognome if staff else "")
        self.add_field("ruolo", "Ruolo:", default_value=staff.ruolo if staff else "")
        self.add_field("telefono", "Telefono:", default_value=staff.telefono if staff else "")
        self.add_field("email", "Email:", default_value=staff.email if staff else "")

        self.update_height()
    
    def _on_save(self):
        self._collect_data()
        if self.staff:
            # Aggiornamento
            for attr, value in self.result.items():
                setattr(self.staff, attr, value)
            self.staff.save()
        else:
            # Creazione
            Dipendente.objects.create(**self.result)
        self.destroy()