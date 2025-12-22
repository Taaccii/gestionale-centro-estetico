from django.db import models
from anagrafica.models import Cliente, Dipendente
from servizi.models import Servizio
from datetime import timedelta
from django.core.exceptions import ValidationError

# Gestione appuntamenti
class Appuntamento(models.Model):

    # Scelte per lo stato dell'Appuntamento
    STATO_CHOICES = [
        ('prenotato', 'Prenotato'),
        ('in_corso', 'In Corso'),
        ('completato', 'Completato'),
        ('annullato', 'Annullato'),
    ]

    # Relazioni con altre tabelle (Foregn Keys). Una ForeignKey crea un collegamento tra due tabelle.
    cliente = models.ForeignKey(
        Cliente, # Tabella collegata
        on_delete=models.PROTECT, #  Impedisce la cancellazione. Non puoi cancellare un cliente se ha appuntamenti
        related_name='appuntamenti' # Nome per la relazione inversa
    )

    dipendente = models.ForeignKey(
        Dipendente,
        on_delete=models.PROTECT,
        related_name='appuntamenti'
    )

    # Campi data/ora
    data_ora_inizio = models.DateTimeField()
    data_ora_fine = models.DateTimeField()

    # Stato e note
    stato = models.CharField(
        max_length=20,
        choices=STATO_CHOICES,
        default='prenotato'
    )

    promemoria_inviato = models.BooleanField(default=False)
    
    note = models.TextField(blank=True)
    motivo_annullamento = models.TextField(blank=True, null=True)


    # Timestamp automatici
    creato_il = models.DateTimeField(auto_now_add=True)
    modificato_il = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Appuntamenti"
        ordering = ['-data_ora_inizio']  # Dal più recente
    
    def __str__(self):
        return f"{self.cliente} - {self.data_ora_inizio.strftime('%d/%m/%Y %H:%M')}"


    def calcola_durata_totale(self):
        """
        Calcola la durata totale sommando le durate di tutti i servizi.
        Restituisce un timedelta.
        """
        # self.dettagli.all() per ottenere tutti i DettaglioAppuntamento collegati
        durata_minuti = sum(dettaglio.durata_effettiva for dettaglio in self.dettagli.all())
        return timedelta(minutes=durata_minuti)

    def aggiorna_data_fine(self):
        """
        Aggiorna data_ora_fine basandosi sui servizi associati.
        Chiamare dopo aver aggiunto/modificato i dettagli.
        """
        durata = self.calcola_durata_totale()
        # Converte il timedelta in secondi totali e evita di aggiornare la data_fine se non ci sono servizi
        if durata.total_seconds() > 0:
            self.data_ora_fine = self.data_ora_inizio + durata
            self.save()


    @property
    def durata_minuti(self):
        """Restituisce la durata totale in minuti (property calcolata).
        Per sapere quanto dura l'appuntamento COSÌ COM'È salvato nel DB"""
        delta = self.data_ora_fine - self.data_ora_inizio
        return int(delta.total_seconds() / 60)

    @property
    def prezzo_totale(self):
        """Calcola il prezzo totale sommando tutti i servizi."""
        return sum(dettaglio.prezzo_finale for dettaglio in self.dettagli.all())


    def get_appuntamenti_sovrapposti(self):
        """
        Verifica che il dipendente non abbia altri appuntamenti sovrapposti.
        Restituisce la lista degli appuntamenti che si sovrappongono.
        Se la lista è vuota, il dipendente è disponibile.
        """
        sovrapposti = []
        # Trova appuntamenti dello stesso dipendente (escluso questo)
        appuntamenti_dipendente = Appuntamento.objects.filter(
            dipendente=self.dipendente,
            stato__in=['prenotato', 'in_corso'] # Solo attivi
        ).exclude(pk=self.pk) # Esclude l'appuntamento corrente

        for altro in appuntamenti_dipendente:
            # Controllo sovrapposizione: due intervalli si sovrappongono se:
            # il mio inizio < la sua fine AND la mia fine > il suo inizio
            if (self.data_ora_inizio < altro.data_ora_fine and self.data_ora_fine > altro.data_ora_inizio):
                sovrapposti.append(altro)

        return sovrapposti   

    @property
    def dipendente_disponibile(self):
        """Restituisce True se non ci sono sovrapposizioni."""
        return len(self.get_appuntamenti_sovrapposti()) == 0


    def clean(self):
        """
        Metodo di validazione automatico di Django.
        Viene chiamato prima di salvare per verificare che i dati siano validi.
        """
        super().clean() # Chiama la validazione del genitore

        # Verifica prima che data_fine e data_inizio abbiano un valore e poi verifica che data_fine sia dopo data_inizio
        if self.data_ora_fine and self.data_ora_inizio:
            if self.data_ora_fine <= self.data_ora_inizio:
                raise ValidationError({'data_ora_fine': 'La data/ora fine deve essere successiva a quella di inizio.'})
        
        # Verifica disponibilità dipendente (solo se ha già entrambe le date)
        if self.data_ora_inizio and self.data_ora_fine and self.dipendente:
            if not self.dipendente_disponibile:
                conflitti = self.get_appuntamenti_sovrapposti()
                msg = f"Il dipendente {self.dipendente} ha già appuntamenti a questo orario: "
                # str(c) chiama il metodo __str__ di ogni appuntamento
                msg += ", ".join([str(c) for c in conflitti])
                raise ValidationError({'dipendente': msg})



class DettaglioAppuntamento(models.Model):
    """
    Collega un appuntamento ai servizi richiesti.
    Un appuntamento può avere più servizi (es: Manicure + Pedicure).
    """

    appuntamento = models.ForeignKey(
        Appuntamento,
        on_delete=models.CASCADE, # Cancella anche i figli. Se cancelli l'appuntamento, cancella anche i suoi dettagli.
        related_name='dettagli'
    )

    servizio = models.ForeignKey(
        Servizio,
        on_delete=models.PROTECT,
        related_name='dettagli_appuntamento'
    )

    # Prezzo e durata effettivi
    prezzo_finale = models.DecimalField(max_digits=8, decimal_places=2)
    durata_effettiva = models.PositiveIntegerField(help_text="Durata effettiva in minuti")

    class Meta:
        verbose_name_plural = "Dettagli Appuntamenti"

    def __str__(self):
        return f"{self.appuntamento} - {self.servizio.nome}"


class LogNotifica(models.Model):
    """
    Registra l'invio (simulato) di notifiche e promemoria.
    """
    TIPO_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
    ]

    appuntamento = models.ForeignKey(
        Appuntamento,
        on_delete=models.CASCADE,
        related_name='notifiche_log'
    )
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    destinatario = models.CharField(max_length=255)
    messaggio = models.TextField()
    data_ora_invio = models.DateTimeField(auto_now_add=True)
    successo = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Log Notifiche"
        ordering = ['-data_ora_invio']

    def __str__(self):
        return f"{self.tipo.upper()} a {self.destinatario} - {self.data_ora_invio.strftime('%d/%m/%Y %H:%M')}"
