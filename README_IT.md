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
git clone https://github.com/tuo-username/solar-eclipse-automation.git
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
json

{
  "hardware": {
    "marca_camera": "CANON",           // CANON, NIKON, SONY
    "gui_path": "C:\\...\\CameraControl.exe",
    "cmd_path": "C:\\...\\CameraControlRemoteCmd.exe",
    "sim_mode": false,                 // true = test senza camera
    "debug_mode": false                // true = log dettagliati
  },
  
  "coordinate": {
    "latitudine_dms": "43°44'08.77\"N",  // Formato gradi/minuti/secondi
    "longitudine_dms": "7°55'20.04\"W",  // N/S e E/W alla fine
    "uso_calcolo_gps": false            // true = calcolo automatico con ephem
  },
  
  "timing_eclisse": {
    "_data": "12 Agosto 2026",
    "p1_inizio": "19:30:00",           // HH:MM:SS formato 24h
    "totalita_inizio": "20:27:10",     // Inizio fase totale
    "totalita_fine": "20:28:50",       // Fine fase totale
    "p4_fine": "21:12:00"              // Fine eclisse
  },
  
  "tempi_scatto": {
    "protuberanze": ["1/8000", "1/4000", "1/2000", "1/1000"],
    "corona": ["1/500", "1/250", "1/125", "1/60", "1/30", "1/15", "1/8", "1/4", "0.5", "1", "2"],
    "burst": ["1/8000", "1/4000", "1/2000"],
    "raffica_scatti": 3                 // Numero scatti per esposizione
  },
  
  "intervalli": {
    "ingresso_parziale_sec": 1080,      // 18 minuti
    "uscita_parziale_sec": 690,         // 11.5 minuti
    "watchdog_interval_sec": 30         // Check watchdog ogni 30 secondi
  },
  
  "fasi_eclisse": [
    // Definisci qui l'ordine e i tempi delle fasi
  ],
  
  "checklist_items": [
    "Filtro solare montato?",
    "Fuoco su MANUALE (MF) e bloccato...",
    // Aggiungi/modifica voci della checklist
  ],
  
  "parametri_camera": {
    "iso_default": 200,
    "apertura_default": 8,
    "test_tempo": "1/1000"
  }
}

📝 Guida alle Configurazioni Avanzate
Coordinate Geografiche - Formato DMS
json

// Esempi validi:
"latitudine_dms": "45°27'52.5\"N"    // Gradi, minuti, secondi
"longitudine_dms": "12°15'30.0\"E"
"latitudine_dms": "-45.4642"          // Gradi decimali (alternativa)

Tempi di Scatto - Formati Supportati
json

"1/8000"    // Frazioni di secondo
"1/500"     
"0.5"       // Mezzo secondo
"2"         // Due secondi

Personalizzazione Fasi Eclisse
json

{
  "nome": "CORONA ESTERNA",           // Nome visualizzato nei log
  "tempo_riferimento": "totalita_inizio", // p1_inizio, totalita_inizio, totalita_fine
  "durata_sec": 45,                   // Durata della fase in secondi
  "lista_tempi": "corona_esterna",    // hdr, burst, corona_interna, corona_esterna
  "usa_raffica": false                // true = multipli scatti per esposizione
}

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