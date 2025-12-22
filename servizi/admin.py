from django.contrib import admin
from .models import Servizio

@admin.register(Servizio)
class ServizioAdmin(admin.ModelAdmin):
    list_display = ['nome', 'durata_minuti', 'prezzo', 'attivo']
    search_fields = ['nome', 'descrizione']
    list_filter = ['attivo']
    # Permette di cliccare su "attivo" direttamente dalla lista per modificarlo
    list_editable = ['attivo', 'prezzo']