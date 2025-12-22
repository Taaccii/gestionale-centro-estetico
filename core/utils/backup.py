import os
import sys
from datetime import datetime
from django.core.management import call_command
from django.conf import settings

# Definisce dove salvare i file (nella cartella "Backup" del progetto)
BACKUP_DIR = os.path.join(settings.BASE_DIR, 'backups')

def create_backup(custom_path=None):
    """Crea un backup e se non dai un percorso ne crea uno con la data di oggi"""

    # Se la cartella non esiste, la crea
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    # Fa scegliere il nome del file
    if custom_path:
        output_file = custom_path
    else:
        # Usa data e ora
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_file = os.path.join(BACKUP_DIR, f"back_up{timestamp}.json")

    with open(output_file, 'w') as f:
        # Chiede a Django di dargli tutti i dati tranne le cose inutili per il backup
        # stdout=f: "Non scriverlo a schermo (console), scrivilo dentro il file f che ho appena aperto".
        # indent=2: "Scrivi ordinato". Crea un JSON leggibile con rientri, non un unico rigo illeggibile.
        call_command('dumpdata', exclude=['sessions', 'contenttypes'], stdout=f, indent=2)
    
    return output_file


def restore_backup(file_path):
    """Legge un file JSON e lo ricarica nel database. Ritorna True se tutto ok"""
    
    if not os.path.exists(file_path):
        return False # Errore

    # Il contrario di 'dumpdata' è 'loaddata'
    call_command('loaddata', file_path)
    return True