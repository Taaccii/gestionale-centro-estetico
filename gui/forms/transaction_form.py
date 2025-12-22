"""Form inserimento Transazione"""

from gui.forms.base_form import BaseFormDialog

import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from cassa.models import Transazione

class TransactionFormDialog(BaseFormDialog):

    def __init__(self, parent):
        super().__init__(parent, "Nuova Transazione")

        # Campi importo e sconto
        self.add_field("importo_totale", "Importo (€):")
        self.add_field("sconto_applicato", "Sconto (€):")

        # Menu tendina per il metodo pagamento (DropDown)
        # Estrae le chiavi [0] per i metodi pagamento, creando un menu a tendina dinamico
        metodi = [choice[1] for choice in Transazione.METODO_CHOICES]
        self.add_dropdown("metodo_pagamento", "Metodo:", metodi)

        # Campo note
        self.add_field("note", "Note:")

        self.update_height()
        
    def _on_save(self):
        self._collect_data()

        # Validazione Importo (se vuoto, esce senza fare nulla)
        if not self.result.get("importo_totale"):
            return

        # Gestione in caso di sconto vuoto (Il DB vuole un decimal e non una stringa vuota)
        if not self.result.get("sconto_applicato"):
            self.result["sconto_applicato"] = 0

        # Gestione Metodo (Da "Contanti" a "contanti" per il DB). Mettiamo tutto in minuscolo
        if self.result.get("metodo_pagamento"):
            self.result["metodo_pagamento"] = self.result["metodo_pagamento"].lower()

        Transazione.objects.create(**self.result)  # Spacchettiamo il dizionario 
        self.destroy()
        