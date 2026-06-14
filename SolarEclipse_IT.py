#!/usr/bin/env python3
"""
Solar Eclipse Automation Script - Versione Configurabile v3.0
"""

import os
import sys
import time
import re
import json
import winsound
import subprocess
from datetime import datetime, timedelta, time as datetime_time

# Moduli opzionali per telemetria avanzata
try:
    import psutil
    HAS_TELEMETRY = True
except ImportError:
    HAS_TELEMETRY = False

try:
    import ephem 
    HAS_ASTRONOMY = True
except ImportError:
    HAS_ASTRONOMY = False

# ==============================================================================
# 0. CARICAMENTO CONFIGURAZIONE
# ==============================================================================

CONFIG_FILE = "config_SolarEclipse_IT.json"

def carica_configurazione():
    """Carica la configurazione dal file JSON"""
    if not os.path.exists(CONFIG_FILE):
        print(f"❌ ERRORE: File di configurazione {CONFIG_FILE} non trovato!")
        print("   Assicurati che il file sia nella stessa cartella dello script")
        sys.exit(1)
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"✅ Configurazione caricata da {CONFIG_FILE}")
        return config
    except json.JSONDecodeError as e:
        print(f"❌ ERRORE: File JSON non valido - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ ERRORE: Impossibile caricare configurazione - {e}")
        sys.exit(1)

# Carica configurazione all'avvio
CONFIG = carica_configurazione()

# Estrai variabili globali dalla configurazione
SIM_MODE = CONFIG["hardware"]["sim_mode"]
DEBUG_MODE = CONFIG["hardware"]["debug_mode"]
MARCA_CAMERA = CONFIG["hardware"]["marca_camera"]
CMD_PATH = CONFIG["hardware"]["cmd_path"]
GUI_PATH = CONFIG["hardware"]["gui_path"]

# Timing eclisse
def stringa_a_time(time_str):
    """Converte stringa HH:MM:SS in oggetto time"""
    h, m, s = map(int, time_str.split(':'))
    return datetime_time(h, m, s)

def avvia_digicamcontrol():
    """Avvia digiCamControl se non è in esecuzione"""
    if SIM_MODE:
        return True
    
    # Verifica se digiCamControl è già in esecuzione
    try:
        risultato = subprocess.run(['tasklist', '/FI', 'imagename eq CameraControl.exe'], 
                                 capture_output=True, text=True)
        if 'CameraControl.exe' in risultato.stdout:
            log_messaggio("✅ digiCamControl già in esecuzione")
            return True
    except:
        pass
    
    # Avvia digiCamControl
    try:
        log_messaggio("🚀 Avvio digiCamControl...")
        subprocess.Popen([GUI_PATH], shell=True)
        time.sleep(5)  # Attendi l'avvio
        log_messaggio("✅ digiCamControl avviato")
        return True
    except Exception as e:
        log_messaggio(f"❌ Errore avvio digiCamControl: {e}", "ERROR")
        return False
    
P1_INIZIO = stringa_a_time(CONFIG["timing_eclisse"]["p1_inizio"])
TOTALITA_INIZIO = stringa_a_time(CONFIG["timing_eclisse"]["totalita_inizio"])
TOTALITA_FINE = stringa_a_time(CONFIG["timing_eclisse"]["totalita_fine"])
P4_FINE = stringa_a_time(CONFIG["timing_eclisse"]["p4_fine"])

# Tempi di scatto
TEMPI_PROTUBERANZE = CONFIG["tempi_scatto"]["protuberanze"]
TEMPI_CORONA = CONFIG["tempi_scatto"]["corona"]
TEMPI_BURST = CONFIG["tempi_scatto"]["burst"]
TEMPI_HDR = TEMPI_PROTUBERANZE + TEMPI_CORONA
TEMPI_CORONA_INTERNA = TEMPI_CORONA[:6]  # Primi 6 tempi per corona interna
TEMPI_CORONA_ESTERNA = TEMPI_CORONA[6:]  # Restanti per corona esterna
RAFAGA_SCATTI = CONFIG["tempi_scatto"]["raffica_scatti"]

# Intervalli
INTERVALLO_INGRESSO = CONFIG["intervalli"]["ingresso_parziale_sec"]
INTERVALLO_USCITA = CONFIG["intervalli"]["uscita_parziale_sec"]
WATCHDOG_INTERVAL = CONFIG["intervalli"]["watchdog_interval_sec"]

# File di sistema
LOG_FILE = CONFIG["file_sistema"]["log_file"]
STATO_FILE = CONFIG["file_sistema"]["stato_file"]
WATCHDOG_FILE = CONFIG["file_sistema"]["watchdog_file"]

# Checklist items
CHECKLIST_ITEMS = CONFIG["checklist_items"]

# Parametri suoni
SUONI = CONFIG["suoni"]

# Parametri camera
TEST_TEMPO = CONFIG["parametri_camera"]["test_tempo"]

# ==============================================================================
# 1. FUNZIONI DI UTILITY E LOGGING
# ==============================================================================

def log_messaggio(messaggio, level="INFO"):
    """Logga messaggio su console e file con timestamp"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    formattato = f"[{timestamp}] [{level}] {messaggio}"
    sys.stdout.write("\r" + " " * 80 + "\r")
    sys.stdout.flush()
    print(formattato)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(formattato + "\n")

def log_debug(messaggio):
    """Logga solo se DEBUG_MODE è attivo"""
    if DEBUG_MODE:
        log_messaggio(f"[DEBUG] {messaggio}")

def emetti_suono(tipo="attenzione"):
    """Emette un suono in base al tipo specificato"""
    try:
        if tipo == "attenzione":
            winsound.Beep(SUONI["attenzione_freq"], SUONI["attenzione_durata"])
        elif tipo == "critico":
            winsound.Beep(SUONI["critico_freq"], SUONI["critico_durata"])
        elif tipo == "completamento":
            for freq, dur in zip(SUONI["completamento_freq"], SUONI["completamento_durata"]):
                winsound.Beep(freq, dur)
    except:
        pass  # Silenzia errori audio

def watchdog_reset():
    """Reset watchdog per evitare freeze totale"""
    try:
        with open(WATCHDOG_FILE, "w") as f:
            f.write(datetime.now().isoformat())
        log_debug("Watchdog resettato")
    except Exception as e:
        log_debug(f"Errore watchdog: {e}")

def salva_stato(fase, indice):
    """Salva lo stato corrente per hot-resume"""
    try:
        stato = {
            'fase': fase,
            'indice': indice,
            'timestamp': datetime.now().isoformat(),
            'ultimo_scatto': datetime.now().strftime('%H:%M:%S')
        }
        with open(STATO_FILE, 'w') as f:
            json.dump(stato, f, indent=2)
        log_debug(f"Stato salvato: {fase} - indice {indice}")
    except Exception as e:
        log_messaggio(f"Errore salvataggio stato: {e}", "WARN")

def carica_stato():
    """Carica lo stato precedente per resume"""
    if os.path.exists(STATO_FILE):
        try:
            with open(STATO_FILE, 'r') as f:
                stato = json.load(f)
            log_messaggio(f"✅ Ripreso da stato: {stato.get('fase', 'inizio')}")
            return stato
        except Exception as e:
            log_messaggio(f"Errore caricamento stato: {e}", "WARN")
    return None

# ==============================================================================
# 2. FUNZIONI HARDWARE E TELEMETRIA
# ==============================================================================

def controlla_telemetria():
    """Monitora batteria portatile per evitare black-out"""
    if HAS_TELEMETRY:
        try:
            batteria = psutil.sensors_battery()
            if batteria:
                if not batteria.power_plugged and batteria.percent < 20:
                    log_messaggio(f"⚠️ BATTERIA AL {batteria.percent}% - NON IN CARICA!", "WARN")
                    emetti_suono("attenzione")
                elif not batteria.power_plugged and batteria.percent < 10:
                    log_messaggio(f"🚨 CRITICO: BATTERIA AL {batteria.percent}%!", "ERROR")
                    emetti_suono("critico")
                
                # Log temperatura CPU
                log_debug(f"CPU: {psutil.cpu_percent()}% | RAM: {psutil.virtual_memory().percent}%")
        except Exception as e:
            log_debug(f"Errore telemetria: {e}")

def converti_tempo_in_secondi(stringa_tempo):
    """Converte stringa tempo (es. '1/2000' o '0.5') in secondi"""
    try:
        if "/" in stringa_tempo:
            num, denom = stringa_tempo.split("/")
            return float(num) / float(denom)
        return float(stringa_tempo)
    except:
        return 0.1

def calc_pausa(tempo_scatto):
    """Calcola pausa basata sul tempo di scatto per evitare sovraccarico buffer"""
    durata = converti_tempo_in_secondi(tempo_scatto)
    if durata < 0.5:
        return 1.0  # Scatto rapido
    elif durata < 5:
        return durata * 1.2  # 20% buffer
    else:
        return durata + 1.0  # +1 secondo per pose lunghe

def imposta_tempo_scatto(tempo, max_tentativi=3):
    """Cambia tempo di scatto con pausa dinamica anti-freeze"""
    if SIM_MODE:
        log_debug(f"[SIM] Imposto tempo: {tempo}")
        return True
        
    for tentativo in range(1, max_tentativi + 1):
        try:
            risultato = subprocess.run([CMD_PATH, "/c", "set", "shutterspeed", tempo], 
                                      capture_output=True, text=True, timeout=5)
            if "error" not in risultato.stdout.lower() and risultato.returncode == 0:
                # LOGICA DEL DELAY DINAMICO
                durata = converti_tempo_in_secondi(tempo)
                if durata >= 0.25:
                    time.sleep(0.15 + durata)  # Attesa stabilizzazione + durata posa
                else:
                    time.sleep(0.15)
                return True
        except subprocess.TimeoutExpired:
            log_messaggio(f"Timeout cambio tempo al tentativo {tentativo}", "WARN")
        except Exception as e:
            log_messaggio(f"Errore USB al tentativo {tentativo}: {e}", "WARN")
        time.sleep(0.2)
        
    log_messaggio(f"❌ CRITICO: Cambio tempo fallito ({tempo})!", "ERROR")
    emetti_suono("critico")
    return False

def scatta_foto(etichetta, max_tentativi=3):
    """Esegue uno scatto con gestione errori"""
    if SIM_MODE:
        log_messaggio(f"[SIM] 📸 Scatto: {etichetta}")
        time.sleep(0.1)
        return True
        
    for tentativo in range(1, max_tentativi + 1):
        try:
            risultato = subprocess.run([CMD_PATH, "/c", "capture"], 
                                      capture_output=True, text=True, timeout=10)
            if "error" not in risultato.stdout.lower() and risultato.returncode == 0:
                return True
        except subprocess.TimeoutExpired:
            log_messaggio(f"Timeout scatto al tentativo {tentativo}", "WARN")
        except Exception as e:
            log_messaggio(f"Errore otturatore al tentativo {tentativo}: {e}", "WARN")
        time.sleep(0.2)
        
    log_messaggio(f"❌ CRITICO: Scatto fallito per {etichetta}!", "ERROR")
    emetti_suono("critico")
    return False

# ==============================================================================
# 3. FUNZIONI DI TEMPORIZZAZIONE
# ==============================================================================

def dms_to_decimal(dms_string):
    """Converte una stringa DMS (Gradi, Primi, Secondi) in decimale"""
    clean_str = dms_string.strip()
    parts = re.findall(r"[-+]?\d*\.\d+|\d+", clean_str)
    direction = clean_str[-1].upper()
    
    if len(parts) >= 3:
        deg, mn, sec = float(parts[0]), float(parts[1]), float(parts[2])
    elif len(parts) == 2:
        deg, mn, sec = float(parts[0]), float(parts[1]), 0.0
    else:
        deg, mn, sec = float(parts[0]), 0.0, 0.0
        
    decimal = deg + (mn / 60.0) + (sec / 3600.0)
    if direction in ['S', 'W', 'O']:
        decimal = -decimal
    return decimal

def calcola_contatti_gps():
    """Calcola o mostra i contatti dell'eclisse"""
    lat_dms = CONFIG["coordinate"]["latitudine_dms"]
    lon_dms = CONFIG["coordinate"]["longitudine_dms"]
    uso_gps = CONFIG["coordinate"]["uso_calcolo_gps"]
    
    print(f"[GEOTARGET] Coordinate caricate: {lat_dms} , {lon_dms}")
    
    if not uso_gps or not HAS_ASTRONOMY:
        log_messaggio("[TIMING] Configurazione oraria manuale caricata correttamente.")
        print(f"\n📅 ORARI ECLISSE ({CONFIG['timing_eclisse']['_data']}):")
        print(f"   P1 (Inizio parziale):   {P1_INIZIO}")
        print(f"   C2 (Inizio totalità):   {TOTALITA_INIZIO}")
        print(f"   C3 (Fine totalità):     {TOTALITA_FINE}")
        print(f"   P4 (Fine parziale):     {P4_FINE}")
        
        # Calcola durata totalità
        durata_min = (TOTALITA_FINE.hour*60+TOTALITA_FINE.minute) - (TOTALITA_INIZIO.hour*60+TOTALITA_INIZIO.minute)
        print(f"   Durata totalità:        ~{durata_min} minuti")
    else:
        # Qui andrebbe il calcolo con ephem
        log_messaggio("Calcolo GPS avanzato non implementato", "WARN")

def attesa_fino_a(orario_target, nome_fase=""):
    """Attende fino all'orario specificato con feedback visivo"""
    now = datetime.now()
    target = datetime.combine(now.date(), orario_target)
    
    # Se l'orario è già passato, guarda a domani (gestione mezzanotte)
    if now > target:
        target += timedelta(days=1)
    
    wait_sec = (target - now).total_seconds()
    
    if wait_sec <= 0:
        log_messaggio(f"⚠️ Orario {orario_target} già passato per {nome_fase}!", "WARN")
        return
    
    log_messaggio(f"⏳ Attesa {wait_sec/60:.1f} minuti fino a {nome_fase} ({orario_target})")
    
    # Watchdog ogni N secondi
    last_watchdog = time.time()
    while wait_sec > 0:
        sleep_time = min(WATCHDOG_INTERVAL, wait_sec)
        time.sleep(sleep_time)
        wait_sec -= sleep_time
        
        # Reset watchdog periodicamente
        if time.time() - last_watchdog >= WATCHDOG_INTERVAL:
            watchdog_reset()
            last_watchdog = time.time()
            controlla_telemetria()
        
        if wait_sec > 0:
            print(f"\r⏳ Ancora {wait_sec:.0f} sec per {nome_fase}...", end='')
    
    print()  # Newline dopo l'attesa
    log_messaggio(f"🎯 Ora {nome_fase} raggiunta!")

# ==============================================================================
# 4. SEQUENZA DI SCATTO PRINCIPALE
# ==============================================================================

def ottieni_lista_tempi(nome_lista):
    """Restituisce la lista dei tempi in base al nome"""
    mappa_liste = {
        "hdr": TEMPI_HDR,
        "burst": TEMPI_BURST,
        "corona_interna": TEMPI_CORONA_INTERNA,
        "corona_esterna": TEMPI_CORONA_ESTERNA,
        "protuberanze": TEMPI_PROTUBERANZE,
        "corona": TEMPI_CORONA
    }
    return mappa_liste.get(nome_lista, TEMPI_HDR)

def esegui_sequenza_scatti(nome_fase, lista_tempi, indice_partenza=0, usa_raffica=True):
    """
    Esegue la sequenza di scatti per una fase
    Returns: Indice dell'ultimo scatto eseguito
    """
    if indice_partenza >= len(lista_tempi):
        log_messaggio(f"Fase {nome_fase} già completata", "INFO")
        return len(lista_tempi) - 1
    
    log_messaggio(f"🎬 INIZIO {nome_fase} - {len(lista_tempi)-indice_partenza} esposizioni rimaste")
    
    for i, tempo in enumerate(lista_tempi[indice_partenza:], indice_partenza):
        # Controlla se l'eclisse è terminata
        if datetime.now().time() > P4_FINE:
            log_messaggio(f"📅 Eclisse terminata, interrompo {nome_fase}")
            return i - 1
        
        # Rafter da N scatti per HDR
        if usa_raffica:
            for scatto in range(RAFAGA_SCATTI):
                etichetta = f"{nome_fase}_{tempo}_shot{scatto+1}"
                if imposta_tempo_scatto(tempo):
                    if scatta_foto(etichetta):
                        log_messaggio(f"📸 {etichetta}")
                        controlla_telemetria()
                    time.sleep(0.3)
        else:
            etichetta = f"{nome_fase}_{tempo}"
            if imposta_tempo_scatto(tempo):
                if scatta_foto(etichetta):
                    log_messaggio(f"📸 {etichetta}")
                    controlla_telemetria()
        
        # Salva stato dopo ogni esposizione
        salva_stato(nome_fase, i + 1)
        
        # Attendi prossimo scatto (se non è l'ultimo)
        if i < len(lista_tempi) - 1:
            pausa = calc_pausa(tempo)
            log_debug(f"Pausa {pausa:.1f}s prima prossimo scatto")
            time.sleep(pausa)
    
    log_messaggio(f"✅ COMPLETATA {nome_fase}")
    return len(lista_tempi) - 1

# ==============================================================================
# 5. MOTORE AUTOMAZIONE PRINCIPALE (HOT-RESUME)
# ==============================================================================

def run_automazione():
    """Motore principale di acquisizione con hot-resume"""
    log_messaggio("🚀 MOTORE ECLISSE ATTIVO")
    log_messaggio(f"{'🔧 SIMULATION ACTIVE' if SIM_MODE else '📷 REAL MODE'}")
    
    # Carica eventuale stato precedente
    stato = carica_stato()
    fase_ripresa = stato.get('fase') if stato else None
    indice_ripresa = stato.get('indice', 0) if stato else 0
    
    # Ottieni le fasi dalla configurazione
    fasi_config = CONFIG["fasi_eclisse"]
    fasi = []
    
    for fase in fasi_config:
        # Determina il tempo di riferimento
        tempo_riferimento = fase["tempo_riferimento"]
        if tempo_riferimento == "p1_inizio":
            orario = P1_INIZIO
        elif tempo_riferimento == "totalita_inizio":
            orario = TOTALITA_INIZIO
        elif tempo_riferimento == "totalita_fine":
            orario = TOTALITA_FINE
        else:
            orario = P1_INIZIO
        
        # Ottieni la lista dei tempi
        lista_tempi = ottieni_lista_tempi(fase["lista_tempi"])
        
        fasi.append((
            fase["nome"],
            orario,
            fase["durata_sec"],
            lista_tempi,
            fase["usa_raffica"]
        ))
    
    # Esegui le fasi
    for nome_fase, tempo_inizio, durata_sec, tempi_scatto, usa_raffica in fasi:
        # Se stiamo riprendendo e questa fase è già stata completata, salta
        if fase_ripresa and fase_ripresa != nome_fase:
            nomi_fasi = [f[0] for f in fasi]
            if fase_ripresa in nomi_fasi:
                indice_fase_corrente = nomi_fasi.index(nome_fase)
                indice_fase_ripresa = nomi_fasi.index(fase_ripresa)
                if indice_fase_corrente < indice_fase_ripresa:
                    log_messaggio(f"⏭️ Salto fase già completata: {nome_fase}")
                    continue
        
        # Determina indice di partenza per questa fase
        if fase_ripresa == nome_fase:
            indice_partenza = indice_ripresa
            fase_ripresa = None  # Reset dopo ripresa
            log_messaggio(f"🔄 Riprendo {nome_fase} dall'indice {indice_partenza}")
        else:
            indice_partenza = 0
            # Attendi l'inizio della fase (solo se non siamo in ripresa)
            attesa_fino_a(tempo_inizio, nome_fase)
        
        # Esegui la sequenza di scatti
        ultimo_indice = esegui_sequenza_scatti(nome_fase, tempi_scatto, indice_partenza, usa_raffica)
        
        # Se la fase è stata completata, rimuovi lo stato
        if ultimo_indice >= len(tempi_scatto) - 1:
            if os.path.exists(STATO_FILE):
                os.remove(STATO_FILE)
                log_debug("Stato cancellato - fase completata")
    
    log_messaggio("🎉 ECLISSE COMPLETATA! 🎉")
    emetti_suono("completamento")

# ==============================================================================
# 6. CHECKLIST E TEST PRE-EVENTO
# ==============================================================================

def test_completo():
    """Test completo dell'hardware prima dell'evento"""
    print("\n" + "🔧" * 40)
    print("           TEST COMPLETO HARDWARE")
    print("🔧" * 40)
    
    # Test telemetria
    if HAS_TELEMETRY:
        try:
            batteria = psutil.sensors_battery()
            if batteria:
                stato_carica = "⚡ In carica" if batteria.power_plugged else "🔌 Su batteria"
                print(f"🔋 Batteria: {batteria.percent}% - {stato_carica}")
            print(f"💻 CPU: {psutil.cpu_percent()}% | RAM: {psutil.virtual_memory().percent}%")
        except Exception as e:
            print(f"⚠️ Errore telemetria: {e}")
    else:
        print("⚠️ psutil non installato - telemetria disabilitata")
    
    # Test comandi camera
    if not SIM_MODE:
        print("\n📷 TEST CONNESSIONE CAMERA...")
        if imposta_tempo_scatto(TEST_TEMPO):
            print("   ✅ Impostazione tempo OK")
            success = scatta_foto("TEST_PRE_EVENTO")
            print(f"   {'✅' if success else '❌'} Scatto test")
        else:
            print("   ❌ Errore connessione camera!")
            if input("\nForzare continuazione? (s/n): ").lower() != 's':
                sys.exit(1)
    else:
        print("\n🔧 MODALITA' SIMULAZIONE - Test skip")
    
    print("\n✅ Test completato")

def run_checklist():
    """Checklist pre-eclisse interattiva"""
    print("\n" + "!" * 75)
    print("      SEQUENZA DI CONNESSIONE HARDWARE (PROTOCOLLO ANTI-FREEZE)")
    print("!" * 75)
    print("  1. ACCENDI CAMERA -> 2. COLLEGA USB -> 3. AVVIA LO SCRIPT")
    print("!" * 75)
    
    if not SIM_MODE:
        input("\n[Premi INVIO per testare la connessione]")
        
        if not imposta_tempo_scatto(TEST_TEMPO):
            print("\n⚠️ Il comando test è stato rifiutato.")
            if input("Forzare inizializzazione? (s/n): ").lower() != 's':
                print("❌ Inizializzazione annullata")
                sys.exit(1)
    
    print("\n📋 CHECKLIST PRE-ECLISSE:")
    for i, item in enumerate(CHECKLIST_ITEMS, 1):
        input(f"  [{i}/{len(CHECKLIST_ITEMS)}] {item} [INVIO] ")
    
    print("\n✅ Checklist completata!")
    
    # Offri test opzionale
    if input("\nEseguire test hardware completo? (s/n): ").lower() == 's':
        test_completo()

# ==============================================================================
# 7. MAIN
# ==============================================================================

def main():
    """Punto di ingresso principale"""
    print("\n" + "☀️" * 40)
    print("      SOLAR ECLIPSE AUTOMATION SCRIPT v3.0")
    print(f"      Data: {CONFIG['timing_eclisse']['_data']}")
    print("☀️" * 40)
    
    # Verifica percorsi se non in simulazione
    if not SIM_MODE:
        if not os.path.exists(CMD_PATH):
            print(f"\n❌ ERRORE: digiCamControl non trovato in:")
            print(f"   {CMD_PATH}")
            print("\n   Verifica il percorso in config_eclipse.json")
            sys.exit(1)
        
        # AVVIA digiCamControl automaticamente
        if not avvia_digicamcontrol():
            print("\n❌ Impossibile avviare digiCamControl")
            print("   Avvialo manualmente e riprova")
            input("\nPremi INVIO dopo aver avviato digiCamControl...")
    
    # Mostra configurazione attiva
    print(f"\n📋 Configurazione attiva:")
    print(f"   Camera: {MARCA_CAMERA}")
    print(f"   Modalità: {'SIMULAZIONE' if SIM_MODE else 'REALE'}")
    print(f"   Debug: {'ON' if DEBUG_MODE else 'OFF'}")
    print(f"   Raffica: {RAFAGA_SCATTI} scatti per esposizione")
    
    # Calcola e mostra timing
    calcola_contatti_gps()
    
    # Esegui checklist
    run_checklist()
    
    # Attesa finale prima dell'inizio
    print("\n" + "⚠️" * 40)
    print("      SCRIPT PRONTO - IN ATTESA DELL'ECLISSE")
    print("      NON SPEGNERE IL COMPUTER O SCOLLEGARE LA CAMERA")
    print("⚠️" * 40)
    
    if not SIM_MODE:
        input("\n[Premi INVIO per avviare il motore principale]")
    else:
        print("\n🔧 MODALITA' SIMULAZIONE - Avvio immediato")
    
    # Avvia automazione
    try:
        run_automazione()
    except KeyboardInterrupt:
        log_messaggio("🚨 SCRIPT INTERROTTO DALL'UTENTE", "WARN")
        print("\n\n⚠️ Script interrotto. Stato salvato per resume.")
        sys.exit(0)
    except Exception as e:
        log_messaggio(f"❌ ERRORE CRITICO: {e}", "ERROR")
        print(f"\n\n❌ Errore fatale: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()