# 📘 Gestionale Centro Estetico - Project Documentation

> **Status:** Phase 11 (Distribuzione Automatizzata) - Finalized  
> **Last Update:** 22/12/2024  
> **Framework:** Django (Backend) + CustomTkinter (Frontend)

---

## 🎯 1. QA Protocol & Rules

### Contesto del Progetto
- **Stack Tecnologico:** Django + Python + CustomTkinter
- **Tipo:** Gestionale per Centro Estetico (Desktop App)
- **Modalità:** Senior AI Mentor -> Professional Implementation

---

## 📂 2. Project Structure & Progress

### ✅ Completed Phases
1. **Setup Ambiente**: Python 3.x, Virtualenv, Django ORM core.
2. **Database Models (100% Implemented)**:
   - `anagrafica`: `Cliente`, `Dipendente` (Ruoli, Note, Allergy).
   - `servizi`: `Servizio` (Durata standard, Costo).
   - `appuntamenti`: `Appuntamento` (Prenotato, In Corso, Completato, Annullato), `DettaglioAppuntamento`. Aggiunto supporto a `promemoria_inviato` e `motivo_annullamento`.
   - `cassa`: `Transazione` (Contanti, Carta, Satispay, Bonifico).
   - `notifiche`: `LogNotifica` (Registro invii Email/SMS).
3. **Business Logic**:
   - Manager per calcoli Durata Totale e Collisioni (Prevenzione sovrapposizioni).
   - **Session System**: Login persistente via `.session.json` con **auto-reset della cache schermi** (`self._screens = {}`) per prevenire errori di puntamento widget (`TclError`).
   - **Backup System**: Dump/Restore integrale del database.
   - **Notification System**: `NotificationService` con logica di rilevamento dinamico (1-48h dall'inizio appuntamento).
4. **GUI Framework (Apple-style UX)**:
   - `gui/app.py`: Main window con Sidebar e Screen Caching.
   - `gui/theme.py`: Sistema colori Rosa/Antracite Light & Dark.
   - `gui/components/base.py`: Componenti riutilizzabili (`DataCard`, `KPICard`, `SearchFilter`).
   - **Universal Footer**: Firma "Sviluppato col ❤️ da TacciDev" integrata in `BaseScreen` e `CalendarScreen`.

---

## 🖥️ Screen Feature Matrix

| Screen | Status | Key Features |
|--------|--------|--------------|
| **Dashboard** | ✅ Ready | 4 KPI Cards, Lista Appuntamenti Odierni. **Refactored** per derivare da `BaseScreen` (include Footer). |
| **Calendario** | ✅ Ready | Viste Giorno/Settimana/Mese. Filtro Dipendente e **Footer manuale**. |
| **Storico App.** | ✅ Ready | Filtri avanzati per Periodo, Stato e Staff. Statistiche incasso. |
| **Anagrafiche** | ✅ Ready | CRUD Staff e Clienti. **Storico Cliente** dettagliato. |
| **Cassa & Report**| ✅ Ready | Gestione transazioni e analisi incassi per metodo di pagamento. |
| **Settings** | ✅ Ready | Gestione Temi e Backup DB. |
| **Notifiche** | ✅ Ready | Centro controllo promemoria (Email/SMS) con log invio. |

---

## 🚀 3. Key Technical Decisions

### Apple-style Architecture
- **Header Integrato**: Ricerca universale con debouncing centrata in ogni schermata.
- **Filter Toolbar**: Barra dei filtri secondaria nel Calendario per non affollare la navigazione principale.
- **Screen Caching**: Memoria istantanea nel passaggio tra viste per massima fluidità Desktop (con reset automatico al login/logout).
- **Simulated Notifications**: Logica di invio differita (Email/SMS) basata su range temporali dinamici (1-48h).

---

```bash
source venv/bin/activate
python -m gui.app
```

---

## 🏗️ 5. Distribution & CI/CD (GitHub Actions)

Il progetto utilizza un sistema di **Continuous Integration** per generare automaticamente gli eseguibili per Windows e Mac.

### Come ottenere gli eseguibili:
1.  Accedi al repository su **GitHub**.
2.  Vai nella scheda **"Actions"**.
3.  Seleziona l'ultima build completata (con segno di spunta verde ✅).
4.  Scarica i file dalla sezione **"Artifacts"** in fondo alla pagina:
    -   `Gestionale-Windows-Portable`: File `.exe` per Windows.
    -   `Gestionale-Mac-App`: Pacchetto `.app` per macOS.

### Note sulla sicurezza:
-   **Windows**: Al primo avvio, se appare SmartScreen, cliccare su "Ulteriori informazioni" -> "Esegui comunque".
-   **macOS**: Fare "Tasto destro" -> "Apri" la prima volta per ignorare il blocco dello sviluppatore non identificato.
-   **Database**: Il file `db.sqlite3` è incluso nell'eseguibile. Per backup manuali, esportare il file `.json` dalla sezione Settings dell'app.

---

> **Sviluppato col ❤️ da TacciDev**
