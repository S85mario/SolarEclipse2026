import os
import sys
import time
import re
import winsound
import subprocess
from datetime import datetime, timedelta, time as datetime_time

# Moduli opzionali per la Roadmap avanzata (Telemetry & GPS)
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
# 1. SETUP HARDWARE & ISOLATED EXPOSURE LADDERS
# ==============================================================================

CAMERA_BRAND = "CANON"  # Seleziona il brand: "CANON", "NIKON", o "SONY"

# ------------------------------------------------------------------------------
# INTERVALLI DI ESPOSIZIONE MODIFICABILI
# ------------------------------------------------------------------------------

# 1. LIVELLO PROTUBERANZE (Plasma / Cromosfera)
SHUTTER_SPEEDS_PROMINENCES = [
    "1/8000", "1/4000", "1/2000", "1/1000", "1/500"
]

# 2. LIVELLO CORONA SOLARE (Corona Interna ed Esterna)
SHUTTER_SPEEDS_CORONA = [
    "1/250", "1/125", "1/60", "1/30", "1/15", "1/8", "1/4", "0.5", "1"
]

# 3. TEMPI DEDICATI AI BURST CRITICI C2 E C3 (Anello di Diamante / Grani di Baily)
SHUTTER_SPEEDS_BURST = ["1/8000", "1/4000", "1/2000", "1/1000"]

# Unione sequenziale istantanea delle liste prima dell'avvio del ciclo
SHUTTER_SPEEDS_HDR = SHUTTER_SPEEDS_PROMINENCES + SHUTTER_SPEEDS_CORONA
# ==============================================================================

# ==============================================================================
# 2. COORDINATES & ECLIPSE TIMING (PARSING DMS NATIVO)
# ==============================================================================

def dms_to_decimal(dms_string):
    """Converte automaticamente una stringa DMS (Gradi, Minuti, Secondi) in decimale"""
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

USE_GPS_CALCULATION = False  

# --- COORDINATE LIVE (Cabo Ortegal / Cariño, Galizia) ---
LATITUDE_DMS  = r"""43°44'08.77"N"""
LONGITUDE_DMS = r"""7°55'20.04"W"""
ALTITUDE      = 100  

LATITUDE  = dms_to_decimal(LATITUDE_DMS)
LONGITUDE = dms_to_decimal(LONGITUDE_DMS)

# --- ORARI MANUALI DI FALLBACK PER LA GALIZIA (12 Agosto 2026) ---
P1_START       = datetime_time(19, 30, 0)   
TOTALITY_START = datetime_time(20, 27, 10)  
TOTALITY_END   = datetime_time(20, 28, 50)  
P3_END         = datetime_time(21, 12, 0)   

def calculate_gps_contacts():
    print(f"[GEOTARGET] Coordinate caricate: {LATITUDE_DMS} , {LONGITUDE_DMS}")
    print(f"[GEOTARGET] Validazione interna: Lat {LATITUDE:.6f} | Lon {LONGITUDE:.6f}")
    if not USE_GPS_CALCULATION or not HAS_ASTRONOMY:
        log_message("[TIMING] Configurazione oraria manuale caricata con successo.")

# ==============================================================================
# 3. GLOBAL CONFIGURATION & SYSTEM PATHS
# ==============================================================================

GUI_PATH = r"C:\Program Files (x86)\digiCamControl\CameraControl.exe"
CMD_PATH = r"C:\Program Files (x86)\digiCamControl\CameraControlRemoteCmd.exe"
LOG_FILE = "eclipse_log.txt"

# --- MODALITÀ SIMULAZIONE ---
SIM_MODE = False        
SIM_SPEED_UP = 1.0      

# Cadenza di scatto per le fasi parziali (in secondi)
INTERVAL_INGRESS = 1080  
INTERVAL_EGRESS  = 690   

# Audio di navigazione
AUDIO_1_MIN        = r"C:\Eclipse\Audio\one_minute_left.wav"
AUDIO_TOGLI_FILTRO = r"C:\Eclipse\Audio\remove_filter.wav"
AUDIO_20_SEC       = r"C:\Eclipse\Audio\20_seconds_left.wav"
AUDIO_METTI_FILTRO = r"C:\Eclipse\Audio\replace_filter.wav"

# ==============================================================================
# 4. HARDWARE SUBPROCESS & TELEMETRY ENGINE
# ==============================================================================

def check_system_telemetry():
    """Monitora lo stato di carica del PC portatile"""
    if HAS_TELEMETRY:
        battery = psutil.sensors_battery()
        if battery and not battery.power_plugged and battery.percent < 20:
            log_message(f"ATTENZIONE: BATTERIA PORTATILE AL {battery.percent}% - NON IN CARICA!", level="WARN")
            winsound.Beep(2000, 1000)


def set_shutter_speed(shutter_speed, max_retries=3):
    """Invia il comando di cambio tempo con loop di recupero"""
    if SIM_MODE:
        return True
        
    for attempt in range(1, max_retries + 1):
        try:
            result = subprocess.run([CMD_PATH, "/c", "set", "shutterspeed", shutter_speed], capture_output=True, text=True)
            if "error" not in result.stdout.lower() and result.returncode == 0:
                time.sleep(0.15)  
                return True
        except Exception as e:
            log_message(f"Errore USB al tentativo {attempt}: {e}", level="WARN")
        time.sleep(0.2)
        
    log_message(f"CRITICAL HARDWARE DROP: Cambio tempo fallito ({shutter_speed})!", level="ERROR")
    for _ in range(5): winsound.Beep(1500, 300)
    return False


def capture_image(log_label, max_retries=3):
    """Invia il comando di scatto nativo puro alla macchina"""
    if SIM_MODE:
        log_message(f"[SIM] Scatto eseguito: {log_label}")
        return True
        
    for attempt in range(1, max_retries + 1):
        try:
            result = subprocess.run([CMD_PATH, "/c", "capture"], capture_output=True, text=True)
            if "error" not in result.stdout.lower() and result.returncode == 0:
                return True
        except Exception as e:
            log_message(f"Errore di scatto al tentativo {attempt}: {e}", level="WARN")
        time.sleep(0.2)
        
    log_message(f"CRITICAL CAMERA CRASH: Scatto fallito per {log_label}!", level="ERROR")
    return False

# ==============================================================================
# SYSTEM UTILITIES (CLOCK, AUDIO, PREFLIGHT)
# ==============================================================================

def log_message(message, level="INFO"):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    formatted_msg = f"[{timestamp}] [{level}] {message}"
    sys.stdout.write("\r" + " " * 80 + "\r")
    sys.stdout.flush()
    print(formatted_msg)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f: f.write(formatted_msg + "\n")
    except Exception as e: print(f"[LOG ERROR] {e}")

class SimClock:
    def __init__(self, start_time_obj, speed_up=1.0, active=False):
        self.active = active
        self.speed_up = speed_up
        self.real_start = time.time()
        anchor_dt = datetime.combine(datetime.now().date(), start_time_obj)
        self.sim_start_dt = anchor_dt - timedelta(minutes=1)
        
    def get_now(self):
        if not self.active: return datetime.now()
        elapsed_sim = (time.time() - self.real_start) * self.speed_up
        return self.sim_start_dt + timedelta(seconds=elapsed_sim)

def play_alert(file_path):
    if SIM_MODE: log_message(f"[SIM - AUDIO] Riproduzione: {os.path.basename(file_path)}"); return
    try: winsound.PlaySound(file_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
    except Exception as e: log_message(f"Riproduzione audio fallita: {e}", level="ERROR")

def start_digicamcontrol():
    if SIM_MODE: return
    log_message(f"Inizializzazione backend per {CAMERA_BRAND}...")
    if os.path.exists(GUI_PATH):
        try: subprocess.Popen([GUI_PATH]); time.sleep(5)
        except Exception as e: log_message(f"Impossibile avviare digiCamControl: {e}", level="ERROR")

def run_preflight_checklist():
    print("\n" + "!" * 75)
    print("      MANDATORY HARDWARE CONNECTION SEQUENCE (ANTI-FREEZE PROTOCOL)")
    print("!" * 75)
    print(f"  CONFIGURAZIONE ATTIVA: Brand={CAMERA_BRAND}")
    print(f"  Totale stop pianificati nella parentesi core: {len(SHUTTER_SPEEDS_HDR)} (Raffica da 3 scatti ciascuno)")
    print("  1. ACCENDI CAMERA -> 2. CONNETTI CAVO USB AL PC -> 3. AVVIA LO SCRIPT")
    print("!" * 75)
    input("\n[Premi INVIO per testare la connessione hardware e passare alla Checklist]")
    
    if not SIM_MODE:
        if not set_shutter_speed("1/2000"):
            print("\n[ATTENZIONE] Il comando di test è stato rifiutato dall'interfaccia USB.")
            if input("Forzare l'avvio dello stesso? (y/n): ").lower() != 'y': sys.exit(1)
            
    checklist = [
        "Filtro Solare montato saldamente sull'obiettivo?",
        "Messa a fuoco impostata su MANUALE (MF) e bloccata con nastro adesivo?",
        "Selettore fisico della fotocamera impostato su Manuale ('M')?",
        "ISO e Diaframma impostati manualmente? (Lo script NON li modificherà!)",
        "Fotocamera configurata per salvare i file ESCLUSIVAMENTE sulla scheda SD interna?"
    ]
    print("\n" + "=" * 70 + "\n                 VALIDAZIONE DI SICUREZZA PRE-VOLO\n" + "=" * 70)
    for i, item in enumerate(checklist, 1):
        input(f"  [{i}/{len(checklist)}] {item} [INVIO] ")

# ==============================================================================
# 5. CORE AUTOMATION WITH HOT-RESUME LOGIC
# ==============================================================================

def run_eclipse_automation():
    today = datetime.now().date()
    dt_c1 = datetime.combine(today, P1_START)
    dt_c2 = datetime.combine(today, TOTALITY_START)
    dt_c3 = datetime.combine(today, TOTALITY_END)
    dt_c4 = datetime.combine(today, P3_END)
    
    clock = SimClock(P1_START, speed_up=SIM_SPEED_UP, active=SIM_MODE)
    log_message("MOTORE ECLISSI ATTIVO [RAFFICA DA 3 SCATTI PER STOP]")
    
    last_ingress_shot = dt_c1
    last_egress_shot = None
    ingress_captured_count = 0
    egress_captured_count = 0
    
    alert_1m_done = False
    alert_12s_done = False
    alert_20s_done = False
    alert_c3_done = False
    c2_burst_done = False
    c3_burst_done = False
    
    hdr_index = 0
    hdr_shot_count = 0
    hdr_sequence_done = False
    
    last_slow_tick = 0
    first_loop_validation = True

    while True:
        now = clock.get_now()
        timestamp_str = now.strftime('%H:%M:%S')
        time.sleep(0.05 if SIM_MODE else 0.1)
        
        if first_loop_validation:
            first_loop_validation = False
            if now >= dt_c4:
                log_message("Script avviato dopo C4. Fine.", level="WARN")
                break
            elif dt_c3 <= now < dt_c4:
                log_message("HOT-RESUME: Sincronizzazione attiva su fase Egress.", level="WARN")
                alert_1m_done = alert_12s_done = alert_20s_done = alert_c3_done = c2_burst_done = c3_burst_done = hdr_sequence_done = True
                last_egress_shot = now
            elif dt_c2 <= now < dt_c3:
                log_message("HOT-RESUME: Sincronizzazione attiva all'interno della TOTALITÀ!", level="WARN")
                alert_1m_done = alert_12s_done = c2_burst_done = True
            elif dt_c1 <= now < dt_c2:
                log_message("HOT-RESUME: Sincronizzazione attiva su fase Ingress.", level="WARN")
                last_ingress_shot = now

        current_epoch = time.time()
        if current_epoch - last_slow_tick >= 1.0:
            last_slow_tick = current_epoch
            check_system_telemetry()
            
            if now < dt_c1:
                sys.stdout.write(f"\r[{timestamp_str}] Attesa contatto C1: -{str(dt_c1 - now).split('.')[0]} ")
            elif now < dt_c2 and not c2_burst_done:
                sys.stdout.write(f"\r[{timestamp_str}] Ingress | Tempo al C2: -{str(dt_c2 - now).split('.')[0]} ")
            elif now < dt_c3 and not c3_burst_done:
                sys.stdout.write(f"\r[{timestamp_str}] TOTALITÀ | Stop attivo: {hdr_index + 1}/{len(SHUTTER_SPEEDS_HDR)} (Scatto {hdr_shot_count + 1}/3) | Fine in: -{str(dt_c3 - now).split('.')[0]} ")
            elif now < dt_c4:
                sys.stdout.write(f"\r[{timestamp_str}] Egress | Fine eclissi (C4) in: -{str(dt_c4 - now).split('.')[0]} ")
            sys.stdout.flush()

        if now < dt_c1:
            continue
            
        # --- FASE 2: INGRESSO (PARZIALE) ---
        elif dt_c1 <= now < dt_c2:
            time_to_c2 = (dt_c2 - now).total_seconds()
            if time_to_c2 <= 60:
                if time_to_c2 <= 60 and not alert_1m_done:
                    log_message("T-60s al C2: Avviso vocale 1 min."); play_alert(AUDIO_1_MIN); alert_1m_done = True
                if time_to_c2 <= 12 and not alert_12s_done:
                    log_message("T-12s: RIMUOVERE FILTRO SOLARE!"); play_alert(AUDIO_TOGLI_FILTRO); alert_12s_done = True
                if time_to_c2 <= 4 and not c2_burst_done:
                    log_message("BURST C2 (Anello di Diamante Ingress)")
                    for speed in SHUTTER_SPEEDS_BURST:
                        if set_shutter_speed(speed):
                            for _ in range(5): capture_image("C2_Burst")
                    c2_burst_done = True
            else:
                if (now - last_ingress_shot).total_seconds() >= INTERVAL_INGRESS or ingress_captured_count == 0:
                    log_message(f"Scatto Ingress Parziale #{ingress_captured_count + 1}")
                    capture_image("Partial_Ingress")
                    last_ingress_shot = now; ingress_captured_count += 1
                    
        # --- FASE 3: TOTALITÀ CORE ---
        elif dt_c2 <= now < dt_c3:
            time_to_c3 = (dt_c3 - now).total_seconds()
            if time_to_c3 <= 20 and not alert_20s_done:
                log_message("T-20s al C3: Fine imminente totalità!"); play_alert(AUDIO_20_SEC); alert_20s_done = True
            if time_to_c3 <= 2 and not c3_burst_done:
                log_message("BURST C3 (Anello di Diamante Egress)")
                for speed in SHUTTER_SPEEDS_BURST:
                    if set_shutter_speed(speed):
                        for _ in range(5): capture_image("C3_Burst")
                c3_burst_done = True
            
            # Sequenza Bracketing Ultra-Semplificata (Raffica da 3 scatti)
            if time_to_c3 > 2 and not hdr_sequence_done:
                current_shutter = SHUTTER_SPEEDS_HDR[hdr_index]
                
                if hdr_shot_count == 0: 
                    set_shutter_speed(current_shutter)
                
                capture_image("Totality_HDR_Stop")
                hdr_shot_count += 1
                
                # --- LOGICA AGGIORNATA: RAFFICA DI 3 SCATTI PER OGNI STOP ---
                if hdr_shot_count >= 3:  
                    hdr_shot_count = 0
                    hdr_index += 1      
                    if hdr_index >= len(SHUTTER_SPEEDS_HDR):
                        log_message("SEQUENZA HDR COMPLETATA. In stand-by fino al burst C3.")
                        hdr_sequence_done = True
                
        # --- FASE 4: USCITA (PARZIALE) ---
        elif dt_c3 <= now <= dt_c4:
            if not alert_c3_done:
                log_message("C3 Superato: RIPOSIZIONARE IL FILTRO SOLARE IMMEDIATAMENTE!"); play_alert(AUDIO_METTI_FILTRO); alert_c3_done = True
                last_egress_shot = now
            if (now - last_egress_shot).total_seconds() >= INTERVAL_EGRESS or egress_captured_count == 0:
                log_message(f"Scatto Egress Parziale #{egress_captured_count + 1}")
                capture_image("Partial_Egress")
                last_egress_shot = now; egress_captured_count += 1
        else:
            log_message("Contatto C4 superato. Automazione completata."); break

if __name__ == "__main__":
    calculate_gps_contacts()
    start_digicamcontrol()
    run_preflight_checklist()
    run_eclipse_automation()