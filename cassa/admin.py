from django.contrib import admin
from .models import Transazione

@admin.register(Transazione)
class TransazioneAdmin(admin.ModelAdmin):
    list_display = ['appuntamento', 'importo_totale', 'sconto_applicato', 'metodo_pagamento', 'data_ora_pagamento']
    search_fields = ['appuntamento__cliente__cognome']
    list_filter = ['metodo_pagamento', 'data_ora_pagamento']
    date_hierarchy = 'data_ora_pagamento'