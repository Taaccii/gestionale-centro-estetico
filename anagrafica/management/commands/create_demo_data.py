from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from anagrafica.models import Cliente, Dipendente
from servizi.models import Servizio
import random

class Command(BaseCommand):
    help = 'Popola il database con dati dimostrativi base (Clienti, Staff, Servizi)'

    def handle(self, *args, **kwargs):
        self.stdout.write('Inizio generazione dati demo...')

        servizi_demo = [
            {'nome': 'Pulizia Viso Profonda', 'descrizione': 'Trattamento purificante completo', 'durata_minuti': 60, 'prezzo': 55.00},
            {'nome': 'Massaggio Rilassante', 'descrizione': 'Massaggio corpo total relax con oli essenziali', 'durata_minuti': 45, 'prezzo': 45.00},
            {'nome': 'Manicure Semipermanente', 'descrizione': 'Pulizia e applicazione smalto semipermanente', 'durata_minuti': 40, 'prezzo': 35.00},
            {'nome': 'Pedicure Curativo', 'descrizione': 'Trattamento piedi completo', 'durata_minuti': 50, 'prezzo': 40.00},
            {'nome': 'Epilazione Total Body', 'descrizione': 'Ceretta gambe, inguine, ascelle', 'durata_minuti': 60, 'prezzo': 65.00},
        ]

        for s_data in servizi_demo:
            Servizio.objects.get_or_create(nome=s_data['nome'], defaults=s_data)
        
        self.stdout.write(self.style.SUCCESS(f'Creati {Servizio.objects.count()} Servizi demo'))

        staff_demo = [
            {'nome': 'Laura', 'cognome': 'Bianchi', 'ruolo': 'Estetista Senior', 'telefono': '3331234567', 'email': 'laura@centro.it'},
            {'nome': 'Giulia', 'cognome': 'Verdi', 'ruolo': 'Onicotecnica', 'telefono': '3339876543', 'email': 'giulia@centro.it'},
            {'nome': 'Marco', 'cognome': 'Rossi', 'ruolo': 'Massaggiatore', 'telefono': '3381122334', 'email': 'marco@centro.it'}
        ]

        for st_data in staff_demo:
            Dipendente.objects.get_or_create(nome=st_data['nome'], cognome=st_data['cognome'], defaults=st_data)
            
        self.stdout.write(self.style.SUCCESS(f'Creati {Dipendente.objects.count()} Dipendenti demo'))

        clienti_demo = [
            {'nome': 'Chiara', 'cognome': 'Ferraris', 'telefono': '3405566778', 'email': 'chiara.f@email.com', 'note': 'Pelle sensibile, usare prodotti anallergici'},
            {'nome': 'Anna', 'cognome': 'Esposito', 'telefono': '3479988776', 'email': 'anna.e@email.com', 'note': 'Preferisce appuntamenti mattutini'},
            {'nome': 'Marta', 'cognome': 'Ricci', 'telefono': '3491122998', 'email': 'marta.r@email.com', 'note': ''},
            {'nome': 'Sara', 'cognome': 'Romano', 'telefono': '3314455667', 'email': 'sara.ro@email.com', 'note': 'Ritarda spesso 5 minuti'}
        ]

        for c_data in clienti_demo:
            Cliente.objects.get_or_create(nome=c_data['nome'], cognome=c_data['cognome'], defaults=c_data)

        self.stdout.write(self.style.SUCCESS(f'Creati {Cliente.objects.count()} Clienti demo'))
        self.stdout.write(self.style.SUCCESS('Completato! Il database ora contiene dati realistici.'))
