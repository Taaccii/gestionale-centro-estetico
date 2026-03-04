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

       
        from appuntamenti.models import Appuntamento, DettaglioAppuntamento
        from cassa.models import Transazione
        
        
        clienti = list(Cliente.objects.all())
        staff = list(Dipendente.objects.all())
        servizi = list(Servizio.objects.all())
        oggi = timezone.now().replace(hour=10, minute=0, second=0, microsecond=0)

        
        app_passato = Appuntamento.objects.create(
            cliente=clienti[0],
            dipendente=staff[0],
            data_ora_inizio=oggi - timedelta(days=1),
            data_ora_fine=oggi - timedelta(days=1) + timedelta(minutes=60),
            stato='completato'
        )
        DettaglioAppuntamento.objects.create(
            appuntamento=app_passato,
            servizio=servizi[0], # Pulizia Viso
            prezzo_finale=servizi[0].prezzo,
            durata_effettiva=servizi[0].durata_minuti
        )
        
        Transazione.objects.create(
            appuntamento=app_passato,
            importo_totale=app_passato.prezzo_totale,
            metodo_pagamento='carta',
        )

        
        app_lungo = Appuntamento.objects.create(
            cliente=clienti[1],
            dipendente=staff[1],
            data_ora_inizio=oggi,
            data_ora_fine=oggi + timedelta(minutes=150),
            stato='completato',
            note='Trattamento SPA completo'
        )
        
        for s in servizi[1:4]: # Relax, Manicure, Pedicure
            DettaglioAppuntamento.objects.create(
                appuntamento=app_lungo,
                servizio=s,
                prezzo_finale=s.prezzo,
                durata_effettiva=s.durata_minuti
            )
        Transazione.objects.create(
            appuntamento=app_lungo,
            importo_totale=app_lungo.prezzo_totale,
            metodo_pagamento='contanti',
        )

        app_in_corso = Appuntamento.objects.create(
            cliente=clienti[3],
            dipendente=staff[0],
            data_ora_inizio=oggi + timedelta(hours=1), 
            data_ora_fine=oggi + timedelta(hours=2),
            stato='in_corso',
            note='Cliente in cabina'
        )
        DettaglioAppuntamento.objects.create(
            appuntamento=app_in_corso,
            servizio=servizi[1], # Massaggio
            prezzo_finale=servizi[1].prezzo,
            durata_effettiva=servizi[1].durata_minuti
        )

        app_dopo = Appuntamento.objects.create(
            cliente=clienti[0],
            dipendente=staff[0],
            data_ora_inizio=oggi + timedelta(hours=5),
            data_ora_fine=oggi + timedelta(hours=6),
            stato='prenotato',
            note='Trattamento di routine'
        )
        DettaglioAppuntamento.objects.create(
            appuntamento=app_dopo,
            servizio=servizi[2], # Manicure
            prezzo_finale=servizi[2].prezzo,
            durata_effettiva=servizi[2].durata_minuti
        )

        # Se domani è domenica (weekday == 6), l'appuntamento futuro si sposta a lunedì
        # perché la vista settimana del calendario mostra solo Lun-Sab.
        domani = oggi + timedelta(days=1, hours=4)
        if domani.weekday() == 6:
            domani += timedelta(days=1)

        app_futuro = Appuntamento.objects.create(
            cliente=clienti[2],
            dipendente=staff[0], 
            data_ora_inizio=domani,
            data_ora_fine=domani + timedelta(hours=1),
            stato='prenotato'
        )
        DettaglioAppuntamento.objects.create(
            appuntamento=app_futuro,
            servizio=servizi[4], # Epilazione
            prezzo_finale=servizi[4].prezzo,
            durata_effettiva=servizi[4].durata_minuti
        )

        self.stdout.write(self.style.SUCCESS(f'Creati {Appuntamento.objects.count()} Appuntamenti demo completi di dettagli e incassi'))
        self.stdout.write(self.style.SUCCESS('Completato! Il database ora contiene dati realistici.'))
