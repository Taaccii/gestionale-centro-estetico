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
            ("Trattamento Fango Drenante", 65.00, 90),
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
        marco = staff_objs[1]

        # 3. Clienti
        nomi_clienti = [
            ("Anna", "Rossi"), ("Giuseppe", "Verdi"), 
            ("Elena", "Bianchi"), ("Luca", "Neri"),
            ("Marta", "Ricci"), ("Sara", "Galli")
        ]
        clienti_objs = []
        for nome, cognome in nomi_clienti:
            c, _ = Cliente.objects.get_or_create(
                nome=nome, 
                cognome=cognome, 
                defaults={'telefono': "3331234567"}
            )
            clienti_objs.append(c)

        # 4. Appuntamenti
        oggi = timezone.now().date()
        ieri = oggi - timedelta(days=1)
        domani = oggi + timedelta(days=1)
        if domani.weekday() == 6: # Salta domenica
            domani += timedelta(days=1)
        if ieri.weekday() == 6: # Salta domenica (se fosse oggi lunedì)
            ieri -= timedelta(days=1)

        # --- IERI (Passati) ---
        # 1. Completato Ieri Mattina
        inizio_ieri_1 = timezone.make_aware(datetime.combine(ieri, time(10, 0)))
        app_ieri_1 = Appuntamento.objects.create(
            cliente=clienti_objs[4], # Marta Ricci
            dipendente=laura,
            data_ora_inizio=inizio_ieri_1,
            data_ora_fine=inizio_ieri_1 + timedelta(minutes=60),
            stato='completato',
            note='Trattamento viso ieri'
        )
        DettaglioAppuntamento.objects.create(
            appuntamento=app_ieri_1, servizio=servizi[0], prezzo_finale=servizi[0].prezzo, durata_effettiva=servizi[0].durata_minuti
        )
        Transazione.objects.create(
            appuntamento=app_ieri_1, importo_totale=app_ieri_1.prezzo_totale, metodo_pagamento='contanti', data_ora_pagamento=app_ieri_1.data_ora_fine
        )

        # --- OGGI (Presente) ---
        # 1. OGGI Completato (Mattina presto)
        inizio_a = timezone.make_aware(datetime.combine(oggi, time(8, 30)))
        app_fatto = Appuntamento.objects.create(
            cliente=clienti_objs[0],
            dipendente=laura,
            data_ora_inizio=inizio_a,
            data_ora_fine=inizio_a + timedelta(minutes=60),
            stato='completato',
            note='Fatto stamattina'
        )
        DettaglioAppuntamento.objects.create(
            appuntamento=app_fatto, servizio=servizi[2], prezzo_finale=servizi[2].prezzo, durata_effettiva=servizi[2].durata_minuti
        )
        Transazione.objects.create(
            appuntamento=app_fatto, importo_totale=app_fatto.prezzo_totale, metodo_pagamento='contanti', data_ora_pagamento=app_fatto.data_ora_fine
        )

        inizio_b = timezone.make_aware(datetime.combine(oggi, time(11, 0)))
        app_in_corso = Appuntamento.objects.create(
            cliente=clienti_objs[1],
            dipendente=laura,
            data_ora_inizio=inizio_b,
            data_ora_fine=inizio_b + timedelta(minutes=45),
            stato='in_corso',
            note='In cabina'
        )
        DettaglioAppuntamento.objects.create(
            appuntamento=app_in_corso, servizio=servizi[1], prezzo_finale=servizi[1].prezzo, durata_effettiva=servizi[1].durata_minuti
        )

        inizio_e = timezone.make_aware(datetime.combine(oggi, time(12, 0)))
        app_marco = Appuntamento.objects.create(
            cliente=clienti_objs[5],
            dipendente=marco,
            data_ora_inizio=inizio_e,
            data_ora_fine=inizio_e + timedelta(minutes=60),
            stato='in_corso',
            note='Massaggio'
        )
        DettaglioAppuntamento.objects.create(
            appuntamento=app_marco, servizio=servizi[2], prezzo_finale=servizi[2].prezzo, durata_effettiva=servizi[2].durata_minuti
        )

        inizio_c = timezone.make_aware(datetime.combine(oggi, time(15, 30)))
        app_prenotato = Appuntamento.objects.create(
            cliente=clienti_objs[2],
            dipendente=laura,
            data_ora_inizio=inizio_c,
            data_ora_fine=inizio_c + timedelta(minutes=60),
            stato='prenotato',
            note='Prenotato per pomeriggio'
        )
        DettaglioAppuntamento.objects.create(
            appuntamento=app_prenotato, servizio=servizi[3], prezzo_finale=servizi[3].prezzo, durata_effettiva=servizi[3].durata_minuti
        )

        # --- DOMANI (Futuro) ---
        inizio_d = timezone.make_aware(datetime.combine(domani, time(10, 0)))
        app_domani = Appuntamento.objects.create(
            cliente=clienti_objs[3],
            dipendente=laura,
            data_ora_inizio=inizio_d,
            data_ora_fine=inizio_d + timedelta(minutes=60),
            stato='prenotato'
        )
        DettaglioAppuntamento.objects.create(
            appuntamento=app_domani, servizio=servizi[0], prezzo_finale=servizi[0].prezzo, durata_effettiva=servizi[0].durata_minuti
        )

        print(f"[DEMO] Generazione completata con successo: {Appuntamento.objects.count()} appuntamenti.")
