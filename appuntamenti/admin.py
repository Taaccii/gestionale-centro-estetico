from django.contrib import admin
from .models import Appuntamento, DettaglioAppuntamento

# Inline permette di vedere/aggiungere i dettagli DENTRO la pagina dell'appuntamento 
class DettaglioInline(admin.TabularInline):
    model = DettaglioAppuntamento
    extra = 1 # Mostra una riga vuota per aggiungere nuovi dettagli

@admin.register(Appuntamento)
class AppuntamentoAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'dipendente', 'data_ora_inizio', 'stato']
    # cliente__cognome: Sintassi per cercare in campi di tabelle collegate (ForeignKey)
    search_fields = ['cliente__nome', 'cliente__cognome', 'dipendente__cognome'] 
    list_filter = ['stato', 'dipendente', 'data_ora_inizio']
    date_hierarchy = 'data_ora_inizio' # Navigazione per date
    inlines = [DettaglioInline] # Mostra i dettagli dentro l'appuntamento

@admin.register(DettaglioAppuntamento)
class DettaglioAppuntamentoAdmin(admin.ModelAdmin):
    list_display = ['appuntamento', 'servizio', 'prezzo_finale', 'durata_effettiva']
    
        
