import sys
import os
from pathlib import Path

# --- PYINSTALLER PATH FIX ---
if getattr(sys, 'frozen', False):
    # Se siamo dentro un eseguibile, aggiungiamo la cartella del bundle al percorso di ricerca
    bundle_dir = Path(sys._MEIPASS)
    if str(bundle_dir) not in sys.path:
        sys.path.insert(0, str(bundle_dir))
else:
    # In sviluppo, aggiungiamo la root del progetto
    project_root = Path(__file__).resolve().parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

# Imposta il modulo delle impostazioni di Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Importa l'app e avviala
try:
    from gui.app import App
    if __name__ == "__main__":
        app = App()
        app.mainloop()
except Exception as e:
    import traceback
    # In caso di errore fatale all'avvio nel bundle, proviamo a mostrare un messaggio
    print(f"Errore all'avvio: {e}")
    traceback.print_exc()
    input("Premi Invio per chiudere...")
