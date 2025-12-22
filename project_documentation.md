# 📘 Gestionale Centro Estetico - Project Documentation

> **Status:** Phase 10 (Consolidamento & QA) - Finalized  
> **Last Update:** 19/12/2024  
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

## 📦 4. Distribuzione e Manutenzione (CI/CD)

Il progetto utilizza **GitHub Actions** per la creazione automatica degli eseguibili per Windows e MacOS.

### Recupero degli Eseguibili
1. Accedi al repository su GitHub.
2. Vai nella scheda **Actions**.
3. Seleziona l'ultima build completata con successo (segno di spunta verde ✅).
4. In fondo alla pagina, nella sezione **Artifacts**, scarica il pacchetto desiderato:
   - `Gestionale-Windows-Portable`: Un unico file `.exe` per Windows.
   - `Gestionale-Mac-App`: Pacchetto `.app` per MacOS.

### Manutenzione Futura
Ogni volta che viene effettuato un `git push` sul ramo `main`, i server di GitHub rigenerano automaticamente gli eseguibili aggiornati.

### Esecuzione in fase di Sviluppo
```bash
source venv/bin/activate
python -m gui.app
```
