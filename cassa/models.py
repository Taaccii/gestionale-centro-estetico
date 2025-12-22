from django.db import models
from django.db.models import Sum, Count
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth
from datetime import date, timedelta
from appuntamenti.models import Appuntamento


class TransazioneManager(models.Manager):
    """
    Manager personalizzato per query statistiche sulle transazioni.
    """
    
    def incassi_giorno(self, data=None):
        """
        Calcola incasso totale di un giorno specifico.
        Se data non specificata, usa oggi.
        """
        if data is None:
            data = date.today()

        risultato = self.filter(
            data_ora_pagamento__date=data
        ).aggregate(
            totale=Sum('importo_totale'), # Somma tutti gli importi
            numero_transazioni=Count('id') # Conta quante righe
        )

        return{
            'data': data,
            'totale': risultato['totale'] or 0, # Se non ci sono transazioni, Sum() restituisce None, non 0
            'numero_transazioni': risultato['numero_transazioni'] or 0
        }

    def incassi_settimana(self, data_riferimento=None):
        """
        Calcola incasso totale della settimana contenente data_riferimento.
        """
        if data_riferimento is None:
            data_riferimento = date.today()
        
        # Trova lunedi e domenica della settimana
        # weekday() restituisce: 0=Lunedì, 1=Martedì, ..., 6=Domenica
        lunedi = data_riferimento - timedelta(days=data_riferimento.weekday())
        domenica = lunedi + timedelta(days=6)

        risultato = self.filter(
            data_ora_pagamento__date__gte=lunedi,
            data_ora_pagamento__date__lte=domenica
        ).aggregate(
            totale=Sum('importo_totale'),
            numero_transazioni=Count('id')
        )

        return {
            'da': lunedi,
            'a': domenica,
            'totale': risultato['totale'] or 0,
            'numero_transazioni': risultato['numero_transazioni'] or 0
        }

    def incassi_mese(self, anno=None, mese=None):
        """
        Calcola incasso totale di un mese specifico.
        """
        if anno is None:
            anno = date.today().year
        if mese is None:
            mese = date.today().month
        
        risultato = self.filter(
            data_ora_pagamento__year=anno,
            data_ora_pagamento__month=mese
        ).aggregate(
            totale=Sum('importo_totale'),
            numero_transazioni=Count('id')
        )

        return {
            'anno': anno,
            'mese': mese,
            'totale': risultato['totale'] or 0,
            'numero_transazioni': risultato['numero_transazioni'] or 0
        }


    def incassi_per_metodo(self, data_inizio=None, data_fine=None, dipendente_id=None):
        """
        Raggruppa incassi per metodo di pagamento con filtri opzionali.
        """
        # self.all() = tutte le transazioni
        # Non esegue ancora la query. Solo quando accedi ai dati.
        qs = self.all() # (qs)QuerySet - è una "domanda" al database che può essere modificata.

        if data_inizio:
            qs = qs.filter(data_ora_pagamento__date__gte=data_inizio)
        if data_fine:
            qs = qs.filter(data_ora_pagamento__date__lte=data_fine)
        if dipendente_id:
            qs = qs.filter(appuntamento__dipendente_id=dipendente_id)

        # values('metodo_pagamento'): Raggruppa i risultati per metodo di pagamento.
        return qs.values('metodo_pagamento').annotate(
            totale=Sum('importo_totale'),
            numero=Count('id')
        ).order_by('-totale') # '-totale' decrescente (dal più grande al più piccolo).


    def incassi_giorno_per_metodo(self, data=None, metodo=None, escludi=None):
        """
        Raggruppa incassi del giorno per metodo di pagamento.
        """

        if data is None:
            data = date.today()

        # Query base (filtra per data)
        qs = self.filter(data_ora_pagamento__date=data)

        # Se metodo specificato, aggiungi filtro
        if metodo:
            qs = qs.filter(metodo_pagamento=metodo)

        # Se escludi specificato (lista di metodi da escludere)
        if escludi:
            qs = qs.exclude(metodo_pagamento__in=escludi)
        # Aggregate
        risultato = qs.aggregate(
            totale=Sum('importo_totale'),
            numero_transazioni=Count('id')
        )

        # Gestisce il None in caso di 0 nel totale
        return {
            'data': data,
            'metodo': metodo,
            'totale': risultato['totale'] or 0,
            'numero_transazioni': risultato['numero_transazioni'] or 0
        }

    def incassi_per_periodo(self, data_inizio, data_fine, dipendente_id=None):
        """
        Calcola incasso totale in un intervallo di date.
        """
        qs = self.filter(
            data_ora_pagamento__date__range=(data_inizio, data_fine)
        )
        if dipendente_id:
            qs = qs.filter(appuntamento__dipendente_id=dipendente_id)
            
        risultato = qs.aggregate(
            totale=Sum('importo_totale'),
            numero_transazioni=Count('id')
        )
        return {
            'totale': risultato['totale'] or 0,
            'numero_transazioni': risultato['numero_transazioni'] or 0
        }

    def incassi_per_staff(self, data_inizio=None, data_fine=None):
        """
        Raggruppa incassi per membro dello staff in un periodo.
        """
        qs = self.all()
        if data_inizio:
            qs = qs.filter(data_ora_pagamento__date__gte=data_inizio)
        if data_fine:
            qs = qs.filter(data_ora_pagamento__date__lte=data_fine)
            
        return qs.values(
            'appuntamento__dipendente__nome', 
            'appuntamento__dipendente__cognome'
        ).annotate(
            totale=Sum('importo_totale'),
            numero=Count('id')
        ).order_by('-totale')

class Transazione(models.Model):
    """
    Registra i pagamenti per gli appuntamenti completati.
    Ogni appuntamento può avere una sola transazione.
    """
    # SOSTITUISCE il manager di default
    objects = TransazioneManager()

    # Metodi di pagamento disponibili
    METODO_CHOICES = [
        ('contanti', 'Contanti'),
        ('carta', 'Carta'),
        ('satispay', 'Satispay'),
        ('bonifico', 'Bonifico Bancario')
    ]

    # Relazione 1 a 1 con Appuntamento, OneToOneField → Relazione uno-a-uno (UNA sola transazione per UN appuntamento)
    appuntamento = models.OneToOneField(
        Appuntamento,
        on_delete=models.PROTECT,
        related_name='transazione',
        null=True, # Aggiunto per poter inserire transazioni manuali senza appuntament
        blank=True # Aggiunto per il form
    )

    # Dettaglio pagamento
    data_ora_pagamento = models.DateTimeField(auto_now_add=True)
    importo_totale = models.DecimalField(max_digits=10, decimal_places=2)
    sconto_applicato = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Sconto in Euro"
    )

    metodo_pagamento = models.CharField(
        max_length=20,
        choices=METODO_CHOICES,
        default='contanti'
    )
    note= models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Transazioni"
        ordering = ['-data_ora_pagamento']

    def __str__(self):
        return f"€{self.importo_totale} - {self.appuntamento.cliente} - {self.data_ora_pagamento.strftime('%d/%m/%Y')}"



    # @property
    # Non occupa spazio nel database
    # Sempre aggiornato (calcolato dinamicamente)
    # Non può andare "fuori sync" con i dati originali
    @property
    def importo_netto(self):
        """Calcola l'importo dopo lo sconto"""
        return self.importo_totale - self.sconto_applicato



