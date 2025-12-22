"""Form inserimento Servizio"""

from gui.forms.base_form import BaseFormDialog

import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from servizi.models import Servizio

class ServiceFormDialog(BaseFormDialog):
    def __init__(self, parent, service=None):
        self.service = service
        title = "Modifica Servizio" if service else "Nuovo Servizio"
        super().__init__(parent, title)

        self.add_field("nome", "Nome Servizio:", default_value=service.nome if service else "")
        self.add_field("durata_minuti", "Durata (minuti):", default_value=str(service.durata_minuti) if service else "")
        self.add_field("prezzo", "Prezzo (€):", default_value=str(service.prezzo) if service else "")
        self.add_field("descrizione", "Descrizione:", default_value=service.descrizione if service else "")

        self.update_height()

    def _on_save(self):
        self._collect_data()
        if self.service:
            # Aggiornamento
            for attr, value in self.result.items():
                setattr(self.service, attr, value)
            self.service.save()
        else:
            # Creazione
            Servizio.objects.create(**self.result)
        self.destroy()