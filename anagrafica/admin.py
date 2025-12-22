from django.contrib import admin
from .models import Cliente, Dipendente

# @admin.register(Cliente) → Registra il modello nell'admin con questa configurazione
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    # list_display: Colonne visibili nella lista. Invece di vedere solo "Rossi Mario", vedi una tabella completa.
    list_display = ['cognome', 'nome', 'telefono', 'email', 'data_iscrizione']
    #  Aggiunge una barra di ricerca. Puoi cercare per nome, cognome, telefono, email.
    search_fields = ['cognome', 'nome', 'telefono', 'email']
    # Aggiunge filtri laterali. Es: filtra tutti i clienti iscritti nel 2024.
    list_filter = ['data_iscrizione']

@admin.register(Dipendente)
class DipendenteAdmin(admin.ModelAdmin):
    list_display = ['cognome', 'nome', 'ruolo', 'telefono', 'data_assunzione']
    search_fields = ['cognome', 'nome', 'ruolo']
    list_filter = ['ruolo', 'data_assunzione']
    
    