import random
from datetime import datetime, time, timedelta
from django.utils import timezone
from django.db import transaction
from anagrafica.models import Cliente, Dipendente
from servizi.models import Servizio
from appuntamenti.models import Appuntamento, DettaglioAppuntamento
from cassa.models import Transazione

def populate_demo_data_if_empty():
    """
    Popola il database con dati demo di qualità se non ci sono appuntamenti.
    """
    if Appuntamento.objects.exists():
        return

    with transaction.atomic():
        print("[DEMO] Inizio generazione dati demo professionali a runtime...")
        
        nomi_servizi = [
            ("Pulizia Viso Profonda", 45.00, 60), 
            ("Manicure Semipermanente", 25.00, 45),
            ("Massaggio Relax Corpo", 55.00, 60), 
            ("Pedicure Curativo", 35.00, 60),
            ("Epilazione Laser Viso", 50.00, 30), 
            ("Trattamento Fango fango drenante", 65.00, 90),
            ("Pressoterapia", 35.00, 45), 
            ("Massaggio Viso Kobido", 40.00, 45)
        ]
        servizi = []
        for nome, prezzo, durata in nomi_servizi:
            s, _ = Servizio.objects.get_or_create(nome=nome, defaults={'prezzo': prezzo, 'durata_minuti': durata})
            servizi.append(s)

        nomi_staff = [("Laura", "Bianchi"), ("Marco", "Rossi"), ("Giulia", "Verdi")]
        staff_objs = []
        for nome, cognome in nomi_staff:
            d, _ = Dipendente.objects.get_or_create(
                nome=nome, 
                cognome=cognome, 
                defaults={'ruolo': "Estetica", 'telefono': "3330000000"}
            )
            staff_objs.append(d)

        laura = staff_objs[0]

        nomi_clienti = [("Anna", "Rossi"), ("Giuseppe", "Verdi"), ("Elena", "Bianchi"), ("Luca", "Neri")]
        clienti_objs = []
        for nome, cognome in nomi_clienti:
            c, _ = Cliente.objects.get_or_create(
                nome=nome, 
                cognome=cognome, 
                defaults={'telefono': "3331234567"}
            )
            clienti_objs.append(c)

        oggi = timezone.now().date()
        
        inizio_a = timezone.make_aware(datetime.combine(oggi, time(9, 30)))
        app_fatto = Appuntamento.objects.create(
            cliente=clienti_objs[0],
            dipendente=laura,
            data_ora_inizio=inizio_a,
            data_ora_fine=inizio_a + timedelta(minutes=servizi[2].durata_minuti),
            stato='completato',
            note='Cliente abituale, massaggio corpo.'
        )
        DettaglioAppuntamento.objects.create(
            appuntamento=app_fatto, servizio=servizi[2], prezzo_finale=servizi[2].prezzo, durata_effettiva=servizi[2].durata_minuti
        )

        Transazione.objects.create(
            appuntamento=app_fatto, 
            importo_totale=app_fatto.prezzo_totale, 
            metodo_pagamento='contanti', 
            data_ora_pagamento=app_fatto.data_ora_fine
        )

        inizio_b = timezone.make_aware(datetime.combine(oggi, time(11, 30)))
        app_in_corso = Appuntamento.objects.create(
            cliente=clienti_objs[1],
            dipendente=laura,
            data_ora_inizio=inizio_b,
            data_ora_fine=inizio_b + timedelta(minutes=servizi[0].durata_minuti),
            stato='in corso',
            note='Trattamento viso iniziato'
        )
        DettaglioAppuntamento.objects.create(
            appuntamento=app_in_corso, servizio=servizi[0], prezzo_finale=servizi[0].prezzo, durata_effettiva=servizi[0].durata_minuti
        )

        marco = staff_objs[1]
        inizio_e = timezone.make_aware(datetime.combine(oggi, time(12, 0)))
        app_marco = Appuntamento.objects.create(
            cliente=clienti_objs[3],
            dipendente=marco,
            data_ora_inizio=inizio_e,
            data_ora_fine=inizio_e + timedelta(minutes=servizi[4].durata_minuti),
            stato='in corso',
            note='Massaggio iniziato'
        )
        DettaglioAppuntamento.objects.create(
            appuntamento=app_marco, servizio=servizi[4], prezzo_finale=servizi[4].prezzo, durata_effettiva=servizi[4].durata_minuti
        )

        inizio_c = timezone.make_aware(datetime.combine(oggi, time(15, 0)))
        app_prenotato = Appuntamento.objects.create(
            cliente=clienti_objs[2],
            dipendente=laura,
            data_ora_inizio=inizio_c,
            data_ora_fine=inizio_c + timedelta(minutes=servizi[1].durata_minuti),
            stato='prenotato',
            note='Prenotazione telefonica'
        )
        DettaglioAppuntamento.objects.create(
            appuntamento=app_prenotato, servizio=servizi[1], prezzo_finale=servizi[1].prezzo, durata_effettiva=servizi[1].durata_minuti
        )

        domani = oggi + timedelta(days=1)
        if domani.weekday() == 6:
            domani += timedelta(days=1)
        
        inizio_d = timezone.make_aware(datetime.combine(domani, time(10, 30)))
        app_domani = Appuntamento.objects.create(
            cliente=clienti_objs[3],
            dipendente=laura,
            data_ora_inizio=inizio_d,
            data_ora_fine=inizio_d + timedelta(minutes=servizi[3].durata_minuti),
            stato='prenotato'
        )
        DettaglioAppuntamento.objects.create(
            appuntamento=app_domani, servizio=servizi[3], prezzo_finale=servizi[3].prezzo, durata_effettiva=servizi[3].durata_minuti
        )

        print(f"[DEMO] Generazione completata con successo: {Appuntamento.objects.count()} appuntamenti.")
