📖 Solar Eclipse Automation System - Manuale Utente
🌟 Panoramica

Sistema di automazione professionale per l'acquisizione fotografica di eclissi solari totali. Progettato per gestire sequenze HDR complesse, con supporto hot-resume, telemetria hardware e modalità simulazione.
📋 Requisiti di Sistema
Hardware Minimo

    PC Windows 10/11 (anche laptop a basso consumo)

    4GB RAM

    500MB spazio libero su disco

    Porta USB 2.0 o superiore

Hardware Consigliato

    SSD per scrittura rapida dei log

    Batteria di backup per il PC

    Monitoraggio temperatura CPU (con psutil)

Camere Supportate

    CANON (testata con EOS series)

    NIKON (supporto teorico tramite digiCamControl)

    SONY (supporto teorico)

Software Richiesto

    Windows 10/11

    digiCamControl (gratuito) - Scarica qui

    Python 3.8+

Librerie Python Opzionali
bash

# Per telemetria avanzata
pip install psutil

# Per calcoli astronomici GPS
pip install ephem

# Nessuna libreria è obbligatoria - lo script funziona anche senza!

🚀 Installazione Rapida
1. Installazione Standard
bash

# Clona o scarica il repository
git clone https://github.com/S85mario/Solar-Eclipse-Automation.git
cd solar-eclipse-automation

# (Opzionale) Installa librerie aggiuntive
pip install psutil ephem

# Verifica che i file siano presenti:
# - SolarEclipse_IT.py
# - config_eclipse.json

2. Configurazione Iniziale

    Installa digiCamControl da digicamcontrol.com

    Collega la camera via USB

    Avvia digiCamControl e verifica la connessione

    Configura la camera in modalità MANUALE (M)

3. Test Rapido
bash

# Abilita modalità simulazione nel file JSON
"sim_mode": true

# Esegui lo script
python SolarEclipse_IT.py

# Verifica che i log vengano generati correttamente

⚙️ Configurazione Dettagliata
Struttura del File config_eclipse.json
json  https://github.com/S85mario/Solar-Eclipse-Automation/blob/main/config_SolarEclipse_IT.json


Modalità Debug vs Simulazione
Modalità	Uso	Effetti
sim_mode: true	Test funzionalità	Nessun comando reale alla camera
debug_mode: true	Diagnostica	Log estremamente dettagliati
Entrambe false	Produzione	Operazione reale, log minimi

🎮 Utilizzo Base

Avvio dello Script
bash

python SolarEclipse_IT.py

Flusso di Esecuzione

    Caricamento configurazione - Verifica file JSON

    Checklist interattiva - Conferma preparazione hardware

    Test connessione - Verifica comunicazione con camera

    Attesa automatica - Timer fino all'inizio eclisse

    Acquisizione - Sequenza automatica delle fasi

    Completamento - Salvataggio log e notifica

Output Generati
text

cartella_progetto/
├── eclissi_log.txt      # Log completo dell'esecuzione
├── eclissi_stato.json   # Stato per recupero (se interrotto)
├── watchdog_last.txt    # Timestamp ultimo reset watchdog
└── config_eclipse.json  # La tua configurazione

🛟 Recupero da Interruzione (Hot-Resume)

Lo script salva automaticamente lo stato dopo ogni scatto. In caso di:

    Crash del sistema

    Spegnimento accidentale

    Interruzione manuale (Ctrl+C)

Procedura di recupero:

    Riavvia il PC/camera

    Rilancia lo script normalmente

    Il sistema riprenderà automaticamente dalla fase interrotta

    ⚠️ Importante: Non cancellare il file eclissi_stato.json per mantenere la possibilità di resume.

📊 Interpretazione dei Log
Livelli Log
Livello	Significato	Azione Richiesta
[INFO]	Operazione normale	Solo informativo
[WARN]	Anomalia recuperabile	Monitorare
[ERROR]	Errore grave	Verifica configurazione
[DEBUG]	Dettaglio tecnico	Solo se debug_mode=true
Esempi Log
text

[19:15:23] [INFO] 🚀 MOTORE ECLISSE ATTIVO
[19:15:23] [INFO] 📷 MODALITA' REALE
[19:27:10] [INFO] 🎯 Ora TOTALITA' raggiunta!
[19:27:11] [INFO] 📸 TOTALITA'_CORONA_INTERNA_1/500_shot1
[19:27:12] [WARN] ⚠️ BATTERIA AL 18% - NON IN CARICA!

🔧 Risoluzione Problemi
Problema: "digiCamControl non trovato"

Soluzione:

    Verifica che digiCamControl sia installato

    Controlla il percorso in config_eclipse.json

    Percorso tipico: C:\Program Files (x86)\digiCamControl\

Problema: Camera non risponde

Checklist:

    Camera accesa

    USB collegata direttamente (no hub)

    digiCamControl aperto e connesso

    Camera in modalità M (Manuale)

    Batteria camera carica

Problema: Tempi di scatto errati

Verifiche:

    Formato tempi in JSON (es. "1/2000" non "1/2000s")

    Camera supporta i tempi specificati

    Prova con modalità simulazione

Script si blocca durante attesa

Cause possibili:

    Watchdog non resettato correttamente

    Problemi di sistema

Soluzioni:

    Riduci watchdog_interval_sec a 15

    Disabilita debug_mode

    Esegui come amministratore

🧪 Modalità Simulazione - Guida al Test
Configurazione Test Completo
json

{
  "hardware": {
    "sim_mode": true,
    "debug_mode": true
  },
  "intervalli": {
    "ingresso_parziale_sec": 10,    // Ridotto per test
    "uscita_parziale_sec": 10
  }
}

Cosa Verificare in Simulazione

    ✅ Logica delle fasi e transizioni

    ✅ Hot-resume (interrompi con Ctrl+C)

    ✅ Calcolo tempi di attesa

    ✅ Gestione errori

    ✅ Salvataggio stato

Test da Eseguire
bash

# Test 1: Esecuzione completa
python SolarEclipse_IT.py

# Test 2: Interruzione e resume
# Avvia -> Ctrl+C dopo 10 secondi -> Riavvia

# Test 3: Configurazioni diverse
# Modifica tempi_scatto nel JSON -> Riavvia

📈 Ottimizzazione Performance
Per Laptop/Batteria
json

{
  "intervalli": {
    "watchdog_interval_sec": 60     // Riduce controlli frequenti
  },
  "tempi_scatto": {
    "raffica_scatti": 2              // Meno scatti = meno energia
  }
}

Per Prestazioni Massime
json

{
  "intervalli": {
    "watchdog_interval_sec": 10     // Monitoraggio più frequente
  },
  "hardware": {
    "debug_mode": false              // Riduce overhead I/O
  }
}

🎯 Best Practices per l'Evento
Prima dell'Eclisse (1 settimana prima)

    Test completo con simulazione

    Verifica batterie camera (almeno 2 cariche)

    Formatta SD card

    Backup configurazione JSON

    Prova connessione USB prolungata (1 ora+)

Giorno dell'Eclisse (3 ore prima)

    Carica batteria PC al 100%

    Prepara cavi di ricambio

    Test connessione camera

    Verifica orientamento filtro solare

    Blocca messa a fuoco con nastro adesivo

Durante l'Eclisse

    Non toccare PC/camera

    Monitora solo i log (nessuna interazione)

    Se possibile, usa batterie esterne

Dopo l'Eclisse

    Salva backup dei log

    Copia foto su disco esterno

    Non formattare SD fino a doppio backup

❓ FAQ

D: Posso usare WiFi invece di USB?
R: Sconsigliato - Latenza e affidabilità USB sono superiori per eventi critici.

D: Cosa succede se la batteria del PC si scarica?
R: All'avvio successivo, hot-resume riprenderà dall'ultimo scatto salvato.

D: Supporta video durante l'eclisse?
R: No, focus esclusivo su foto HDR. Usa una seconda camera per video.

D: Posso cambiare la sequenza durante l'esecuzione?
R: No - tutte le modifiche richiedono restart. Usa modalità simulazione prima.

D: Quante foto farà in totale?
R: Circa 60-80 a seconda della configurazione (raffica 3x per esposizione).
📞 Supporto e Contributi
Segnalazione Bug

Apri una issue su GitHub con:

    File eclissi_log.txt

    Versione script

    Configurazione JSON

    Passi per riprodurre

Miglioramenti Suggeriti

    Supporto per altre marche camera

    Calcolo automatico timing con ephem

    Interfaccia GUI

    Export metadati EXIF

📄 Licenza

MIT License - Uso libero per scopi non commerciali.
Crediti apprezzati ma non obbligatori.
🙏 Ringraziamenti

    Team digiCamControl per il software di controllo

    Comunità astrofili italiani per i test sul campo

    Contributori open source

Buona eclisse! 🌞🌑📸