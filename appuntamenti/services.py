from django.utils import timezone
from datetime import timedelta
from .models import Appuntamento, LogNotifica

class NotificationService:
    """
    Servizio per la gestione e l'invio simulato di notifiche.
    """

    @staticmethod
    def process_reminders():
        """
        Controlla gli appuntamenti nelle prossime 24 ore e invia promemoria.
        Restituisce il numero di notifiche inviate.
        """
        now = timezone.now()
        # Per i test/demo, cerchiamo appuntamenti che iniziano tra 1 e 48 ore da adesso
        start_range = now + timedelta(hours=1)
        end_range = now + timedelta(hours=48)

        appuntamenti = Appuntamento.objects.filter(
            stato='prenotato',
            promemoria_inviato=False,
            data_ora_inizio__range=(start_range, end_range)
        )

        sent_count = 0
        for app in appuntamenti:
            # Simulazione invio Email
            LogNotifica.objects.create(
                appuntamento=app,
                tipo='email',
                destinatario=app.cliente.email or f"{app.cliente.cognome.lower()}@example.com",
                messaggio=f"Gentile {app.cliente.nome}, ti ricordiamo il tuo appuntamento di domani alle {app.data_ora_inizio.strftime('%H:%M')}."
            )

            # Simulazione invio SMS
            LogNotifica.objects.create(
                appuntamento=app,
                tipo='sms',
                destinatario=app.cliente.telefono or "3331234567",
                messaggio=f"Ciao {app.cliente.nome}! Promemoria appuntamento domani ore {app.data_ora_inizio.strftime('%H:%M')} da Gestionale Tacci."
            )

            app.promemoria_inviato = True
            app.save()
            sent_count += 1
        
        return sent_count

    @staticmethod
    def get_recent_notifications(limit=10):
        """Restituisce gli ultimi log di notifica."""
        return LogNotifica.objects.all()[:limit]
