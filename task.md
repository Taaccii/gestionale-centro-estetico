# 📋 Task: Input Forms Implementation

### Step 1: Base e Navigazione
- [x] Creare `gui/screens/calendar.py`
- [x] Control Bar (Next/Prev Day)
- [x] Staff Header (Colonne Dipendenti)

### Step 2: Griglia Oraria
- [x] Container Scrollabile
- [x] Generazione righe 8:00 - 20:00
- [x] Slot vuoti cliccabili

### Step 3: Appuntamenti
- [x] Fetch appuntamenti dal DB
- [x] Rendering Card Appuntamento
- [x] Posizionamento nella griglia corretta
- [x] Migliorare contrasto testo Card (Bianco su Rosa è poco leggibile)

### Step 4: Creazione Appuntamento
- [x] Abilitare pulsante "+ Nuovo Appuntamento"
- [x] Creare `gui/forms/appointment_form.py`
- [x] Gestione selezione Cliente/Servizio/Dipendente
- [x] Salvataggio `Appuntamento` e `DettaglioAppuntamento`

### Step 5: Refactoring Tema (Light/Dark Mode)
- [x] Definire Palette Light Mode (Modern SaaS Style)
- [x] Convertire `theme.py` per usare tuple `(light, dark)`
- [x] Aggiungere switch tema nella Dashboard

### Step 6: Gestione Appuntamenti (Modifica/Cancellazione)
- [x] Click su card appuntamento apre dettaglio
- [x] Adattare `AppointmentFormDialog` per modalità "Modifica"
- [x] Popolare form con dati esistenti
- [x] Logica di salvataggio (Update vs Create)
- [x] Pulsante "Elimina Appuntamento"
- [x] Toast Notification System (Success/Error/Warning)
- [x] Validazione Input Form Appuntamento
- [x] Gestione Omonimie Clienti (Smart Labels)
- [x] UI Polish: Autocomplete Dropdown (Searchable)

### Step 7: Sistema Utenti (Login & Sicurezza)
- [x] Creazione View Login (`gui/screens/login.py`)
- [x] Integrazione Autenticazione Django (`auth.login`)
- [x] Protezione Schermate (Redirect se non loggato)
- [x] Logout funzionalità
- [x] Persistent Login (Remember Me) [`core/utils/session.py`]

### Step 8: Backup & Maintenance
- [x] Script di Backup Database (JSON) [`core/utils/backup.py`]
- [x] UI Impostazioni per gestione Backup [`gui/screens/settings.py`]
- [x] Restore Functionality con conferma di sicurezza
- [x] Styling Bottoni e Feedback Utente

### Step 9: Funzionalità Mancanti (Gap Analysis)
- [x] **Multi-Servizio**: Selezione multipla servizi.
    - [x] UI: Container scrollabile per servizi
    - [x] UI: Pulsante "Aggiungi Servizio" (+) (Chip System implemented)
    - [x] Logic: Salvataggio multiplo in `DettaglioAppuntamento`
    - [x] Logic: Calcolo dinamico durata/prezzo (tramite `app.aggiorna_data_fine`)
- [ ] **Viste Calendario**: Settimanale e Mensile.
- [ ] Storico Appuntamenti per Cliente (Click su Cliente)
- [ ] Controllo Sovrapposizioni Appuntamenti (Collision Check)
- [ ] Ricerca Avanzata Clienti (Barra di ricerca)
- [ ] Popup Avvio (Riepilogo Giornaliero)

---

## Completed
- [x] Cash Screen
- [x] Centralizzazione Icone
- [x] Form Cliente
- [x] Form Servizio
- [x] Form Dipendente
- [x] Form Transazione
