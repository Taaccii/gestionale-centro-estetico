from django.db import models

class Cliente(models.Model):
    nome = models.CharField(max_length=100)
    cognome = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    data_nascita = models.DateField(null=True, blank=True)
    note = models.TextField(blank=True) # Per inserire allergie, problemi di pelle, preferenze etc.
    data_iscrizione = models.DateField(auto_now_add=True)

    # Classe interna che configura il comportamento del modello.
    class Meta:
        # Nel pannello Admin di Django. Senza questo, vedrai "Clientes" (Django aggiunge "s" automaticamente)
        verbose_name_plural = "Clienti"
        # Quando fai una query, i risultati saranno sempre ordinati per cognome e poi nome
        ordering = ['cognome', 'nome']

    def __str__(self):
        return f"{self.cognome} {self.nome}"

    def get_appuntamenti_passati(self):
        """Restituisce gli appuntamenti completati o passati dal più recente."""
        from django.utils import timezone
        return self.appuntamenti.filter(
            data_ora_inizio__lt=timezone.now()
        ).order_by('-data_ora_inizio')

    def get_appuntamenti_futuri(self):
        """Restituisce gli appuntamenti prenotati nel futuro."""
        from django.utils import timezone
        return self.appuntamenti.filter(
            data_ora_inizio__gte=timezone.now()
        ).order_by('data_ora_inizio')


class Dipendente(models.Model):
    nome = models.CharField(max_length=100)
    cognome = models.CharField(max_length=100)
    ruolo = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    stipendio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank= True)
    data_assunzione = models.DateField(null=True, blank=True)

    
    class Meta:
        verbose_name_plural = "Dipendenti"
        ordering = ['cognome', 'nome']

    def __str__(self):
        return f"{self.cognome} {self.nome} - {self.ruolo}"


    
