import os
import json
from datetime import datetime, timedelta
from django.conf import settings

# Il file dove vengono salvati i dati della sessione (nascosto col punto davanti)
SESSION_FILE = os.path.join(settings.BASE_DIR, '.session.json')

def save_session(user_id, duration="short"):
    """Salva l'ID utente e la scadenza in un file JSON."""

    # Mappa per la durata in giorni
    durata = {
        "short": 1, # Default se non spunta nulla
        "month": 30, # Ricordami 1 mese
        "forever": 3650 # "Per sempre" (10 anni)
    }

    # Prende i giorni dal dizionario o 1 se non trova nulla
    days = durata.get(duration, 1)
    expiration = datetime.now() + timedelta(days=days)

    # Prepara il pacchetto dati
    data = {
        "user_id": user_id,
        "expiration": expiration.strftime("%Y-%m-%d %H:%M:%S")
    }

    try:
        with open(SESSION_FILE, 'w') as f:
            json.dump(data, f)
        return True
    except Exception as e:
        print(f"Errore salvataggio sessione: {e}")


def load_session():
    """Ritorna user_id se la sessione è valida altrimenti None"""
    if not os.path.exists(SESSION_FILE):
        return None
    try:
        with open(SESSION_FILE, 'r') as f:
            data = json.load(f)

        # Controlla la scadenza
        exp = datetime.strptime(data["expiration"], "%Y-%m-%d %H:%M:%S")
        if datetime.now() < exp:
            return data["user_id"]

    except Exception:
        pass # Il file è rotto e si ignora

    return None

def clear_session():
    """Cancella il file sessione (Logout)."""
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)