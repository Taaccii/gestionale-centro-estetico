from django.db import models

class Servizio(models.Model):
    nome = models.CharField(max_length=100)
    descrizione = models.TextField(blank=True)
    durata_minuti = models.PositiveIntegerField(help_text="Durata standard del servizio in minuti")
    prezzo = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Prezzo standard in Euro"
    )
    # Vero/Falso. Invece di cancellare un servizio, lo "disattiva". Così lo storico appuntamenti resta intatto.
    attivo = models.BooleanField(
        default=True,
        help_text="Se False, il servizio non sarà prenotabile"
    )

    class Meta:
        verbose_name_plural = "Servizi"
        ordering = ['nome']
        
    def __str__(self):
        return f"{self.nome} - {self.durata_minuti}min - €{self.prezzo}"

