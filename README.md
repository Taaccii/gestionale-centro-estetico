# 💅 Gestionale Centro Estetico

> Sistema gestionale completo per centri estetici sviluppato in Python con Django e CustomTkinter.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-6.0-092E20?style=for-the-badge&logo=django&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-5.2-FF6B6B?style=for-the-badge)
![License](https://img.shields.io/badge/License-Proprietary-red?style=for-the-badge)

![Demo](./docs/gif-preview-gestionale.gif)

---

## ✨ Funzionalità Principali

### 📅 Gestione Appuntamenti
- Calendario interattivo con viste **Giorno**, **Settimana** e **Mese**
- Prenotazione rapida con selezione orario e operatore
- Gestione stati: Prenotato, In Corso, Completato, Annullato
- **Prevenzione automatica sovrapposizioni** orari
- Calcolo automatico durata totale in base ai servizi

### 👥 Anagrafica Completa
- Gestione **Clienti** con storico appuntamenti e note personali
- Gestione **Dipendenti/Operatori** con ruoli e specializzazioni
- Ricerca avanzata e filtri rapidi

### 💆 Catalogo Servizi
- Definizione servizi con durata standard e prezzo
- Associazione multipla servizi per appuntamento

### 💰 Gestione Cassa
- Registrazione transazioni per ogni appuntamento
- Supporto metodi di pagamento: Contanti, Carta, Satispay, Bonifico
- Report incassi con filtri per periodo e metodo

### 🔔 Sistema Notifiche
- Promemoria automatici via Email/SMS (simulati)
- Log completo degli invii con timestamp

### ⚙️ Impostazioni
- **Tema chiaro/scuro** con design Apple-style
- Sistema di **Backup & Restore** del database
- Login persistente con sessione salvata

---

## 🛠️ Stack Tecnologico

| Componente | Tecnologia |
|------------|-----------|
| **Backend/ORM** | Django 6.0 |
| **Frontend GUI** | CustomTkinter |
| **Database** | SQLite3 |
| **Linguaggio** | Python 3.11+ |
| **Build** | PyInstaller |
| **CI/CD** | GitHub Actions |
| **Release** | GitHub Releases (automated) |

---

## 🏗️ Architettura del Progetto

```
gestionale_centro_estetico/
├── anagrafica/          # Modelli Cliente e Dipendente
├── appuntamenti/        # Logica appuntamenti e notifiche
├── servizi/             # Catalogo servizi
├── cassa/               # Gestione transazioni
├── core/                # Configurazione Django
├── gui/                 # Interfaccia grafica
│   ├── app.py           # Main window e routing
│   ├── theme.py         # Sistema colori e font
│   ├── components/      # Componenti UI riutilizzabili
│   ├── forms/           # Dialog e form modali
│   └── screens/         # Schermate principali
├── assets/              # Risorse grafiche
├── main.py              # Entry point
└── requirements.txt     # Dipendenze Python
```

---

## 🚀 Installazione

### Prerequisiti
- Python 3.11 o superiore
- pip (gestore pacchetti Python)
- admin e admin come username e password

### 🔐 Demo Access
- **Username:** admin
- **Password:** admin

> Un pulsante **"Accedi come Guest"** è disponibile nella schermata di login per accesso immediato.

### Setup

```bash
# Clona il repository
git clone https://github.com/tuousername/gestionale-centro-estetico.git
cd gestionale-centro-estetico

# Crea e attiva l'ambiente virtuale
python -m venv venv
source venv/bin/activate  # Linux/macOS
# oppure: venv\Scripts\activate  # Windows

# Installa le dipendenze
pip install -r requirements.txt

# Applica le migrazioni del database
python manage.py migrate

# Crea un utente admin (opzionale)
python manage.py createsuperuser

# Avvia l'applicazione
python main.py

```

---

## 📦 Build Eseguibile

Il progetto include una pipeline CI/CD per generare automaticamente eseguibili standalone:

```bash
# Build manuale con PyInstaller
pip install pyinstaller
pyinstaller --onefile --windowed main.py
```

Gli eseguibili vengono compilati e pubblicati automaticamente su **GitHub Releases** ad ogni push su main.

---

## 🎨 Design System

L'interfaccia segue le linee guida Apple Human Interface con:

- 🌙 **Dark Mode** nativa con palette Rosa/Antracite
- ✨ **Micro-animazioni** per feedback visivo
- 📱 **Layout responsivo** con sidebar collassabile
- 🔤 **Tipografia** consistente con gerarchia chiara

---

## 📋 Roadmap

- [x] CRUD completo per tutte le entità
- [x] Calendario multi-vista
- [x] Sistema di backup
- [x] Build automatizzata
- [x] Release automatizzate con GitHub Actions
- [x] Accesso Guest per demo
- [ ] Integrazione reale Email/SMS
- [ ] Esportazione report PDF
- [ ] Dashboard analytics avanzate


---

## 📄 Licenza

**Tutti i diritti riservati.** Questo software è disponibile solo per visualizzazione e valutazione (colloqui, portfolio). Non è consentito copiare, modificare, distribuire o utilizzare commercialmente.

Vedi `LICENSE` per i dettagli completi.

---

## 👨‍💻 Autore

**Taaccii**

- 📧 Email: taccidev@gmail.com
- 💼 LinkedIn: [alessandro-barletta-dev](https://linkedin.com/in/alessandro-barletta-dev)
- 🐙 GitHub: [@Taaccii](https://github.com/Taaccii)

---

> *Sviluppato con il ❤️ per dimostrare competenze in Python, Django e sviluppo desktop.*
