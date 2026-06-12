import time
import subprocess
from datetime import datetime, time as datetime_time, timedelta

# ==============================================================================
# CONFIGURAZIONI PARAMETRI ECLISSI & HARDWARE
# ==============================================================================
# Percorso dell'eseguibile di digiCamControl
CMD_PATH = r"C:\Program Files (x86)\digiCamControl\CameraControlRemoteCmd.exe"

# --- CONFIGURAZIONE ORARI REALI (Eclissi 12 Agosto 2026 - Nord Spagna) ---
P1_START       = datetime_time(19, 30, 0)   # Inizio parzialità (C1)
TOTALITY_START = datetime_time(20, 27, 0)   # Inizio totalità (C2)
TOTALITY_END   = datetime_time(20, 28, 45)  # Fine totalità (C3)
P3_END         = datetime_time(21, 15, 0)   # Limite osservabilità / Tramonto (C4)

# --- INTERVALLI SCATTI FASI PARZIALI (in secondi) ---
INTERVAL_INGRESS = 1080  # 18 minuti per distribuire 5 scatti equidistanti in ingresso
INTERVAL_EGRESS  = 690   # 11.5 minuti per distribuire 5 scatti equidistanti in uscita

# --- CONFIGURAZIONE LISTE ESPOSIZIONI ---
# Bracketing Corona Solare (Fase Totale)
TOTALITY_EXPOSURES = [
    "1/8000", "1/6400", "1/5000", "1/4000", "1/2000", "1/1000", "1/500", 
    "1/250", "1/125", "1/80", "1/30", "1/20", "1/10", "1/2", "1", "2", "4"
]

# Tempi di sicurezza per l'Anello di Diamante (C2 Burst)
DIAMOND_EXPOSURES = ["1/8000", "1/4000", "1/2000"]

# --- MODALITÀ DI ESECUZIONE ---
SIMULATION_MODE = True  # Imposta su False sul campo reale
SIM_SPEED_UP    = 60.0  # Fattore di accelerazione del tempo in simulazione (es. 60x)

# ==============================================================================
# MOTORE DI SIMULAZIONE DI TEMPO (SimClock)
# ==============================================================================
class SimClock:
    def __init__(self, start_time, speed_up=1.0, active=False):
        self.active = active
        self.speed_up = speed_up
        self.real_start = time.time()
        self.sim_start_dt = datetime.combine(datetime.today(), start_time) - timedelta(minutes=2)

    def now(self):
        if not self.active:
            return datetime.now()
        elapsed_real = time.time() - self.real_start
        elapsed_sim = elapsed_real * self.speed_up
        return self.sim_start_dt + timedelta(seconds=elapsed_sim)

    def sleep(self, seconds, critical=False):
        if not self.active or critical:
            time.sleep(seconds)
        else:
            time.sleep(seconds / self.speed_up)

# Inizializzazione del clock di sistema
clock = SimClock(P1_START, speed_up=SIM_SPEED_UP, active=SIM_MODE)

# ==============================================================================
# FUNZIONI INTERFACCIA MACCHINA FOTOGRAFICA (digiCamControl)
# ==============================================================================
def set_shutter_speed(speed):
    """Invia il comando USB per variare il tempo di scatto."""
    if SIMULATION_MODE:
        return
    try:
        subprocess.run([CMD_PATH, "/c", "set", "shutterkeyword", speed], capture_output=True)
    except Exception as e:
        print(f"\n[ERRORE USB] Impossibile impostare shutter: {e}")

def capture_image(filename):
    """Invia il comando USB per far scattare la reflex."""
    now_str = clock.now().strftime('%H:%M:%S')
    print(f"[{now_str}] [SCATTO] -> {filename}")
    if SIMULATION_MODE:
        return
    try:
        subprocess.run([CMD_PATH, "/c", "capture", filename], capture_output=True)
    except Exception as e:
        print(f"\n[ERRORE USB] Scatto fallito per {filename}: {e}")

def play_sound_alert(alert_type):
    """Genera un segnale acustico di sistema differenziato in base all'evento."""
    import winsound
    if alert_type == "pre_totality":
        winsound.Beep(880, 1000) # Nota LA acuta per 1 secondo
    elif alert_type == "start_totality":
        winsound.Beep(1200, 500); winsound.Beep(1200, 500) # Doppio Beep aggressivo (Filtro via!)
    elif alert_type == "pre_end_totality":
        winsound.Beep(440, 300); winsound.Beep(440, 300) # Pre-avviso rimessa filtro
    elif alert_type == "end_totality":
        winsound.Beep(2000, 1500) # Beep lungo e penetrante (Filtro dentro subito!)

def calculate_exposure_wait(speed_str):
    """Calcola i secondi fisici necessari per l'esposizione della posa."""
    if "/" in speed_str:
        num, denom = speed_str.split("/")
        return float(num) / float(denom)
    return float(speed_str)

# ==============================================================================
# AUTOMAZIONE CENTRALE DELL'ECLISSI
# ==============================================================================
def run_eclipse_automation():
    # Registri temporali degli ultimi scatti eseguiti
    last_partial_shot_sim_ts = 0
    
    # Interruttori di Sicurezza (Flags di stato)
    pre_totality_executed = False  
    pre_end_totality_executed = False 
    totality_executed = False
    filter_remove_warned = False
    diamond_burst_c2_executed = False

    # Calcolo dinamico e automatico delle finestre temporali critiche
    PRE_TOTALITY_TIME     = (datetime.combine(datetime.today(), TOTALITY_START) - timedelta(minutes=1)).time()
    WARN_REMOVE_FILTER    = (datetime.combine(datetime.today(), TOTALITY_START) - timedelta(seconds=12)).time() 
    START_DIAMOND_BURST   = (datetime.combine(datetime.today(), TOTALITY_START) - timedelta(seconds=8)).time()  
    START_CORONA_BRACKET  = (datetime.combine(datetime.today(), TOTALITY_START) + timedelta(seconds=3)).time()  
    PRE_END_TOTALITY_TIME = (datetime.combine(datetime.today(), TOTALITY_END) - timedelta(seconds=20)).time()
    
    print("=" * 70)
    print(f" LOGISTICA AUTOMAZIONE ECLISSI 2026 - MODALITÀ SIMULAZIONE: {SIMULATION_MODE}")
    print("=" * 70)
    print(f" Finestra Diamante C2:  Da {START_DIAMOND_BURST.strftime('%H:%M:%S')} a {START_CORONA_BRACKET.strftime('%H:%M:%S')}")
    print(f" Bracketing Corona:    Da {START_CORONA_BRACKET.strftime('%H:%M:%S')} a {TOTALITY_END.strftime('%H:%M:%S')}")
    print("-" * 70)

    while True:
        now_dt = clock.now()
        now_time = now_dt.time()
        current_sim_ts = now_dt.timestamp()
        
        if SIMULATION_MODE:
            print(f" Ora Simulata: {now_dt.strftime('%H:%M:%S')} | Stato: Monitoraggio loop", end="\r")

        # ----------------------------------------------------------------------
        # 1. ATTESA INIZIALE (Prima del contatto C1)
        # ----------------------------------------------------------------------
        if now_time < P1_START:
            clock.sleep(0.5)
            continue
            
        # ----------------------------------------------------------------------
        # 2. FASE PARZIALE IN INGRESSO (C1 -> Finestra Diamante)
        # ----------------------------------------------------------------------
        elif P1_START <= now_time < START_DIAMOND_BURST:
            
            # Controllo pre-allarme standard vocale (-1 minuto alla totalità)
            if now_time >= PRE_TOTALITY_TIME and not pre_totality_executed:
                print(f"\n\n[!!!] ALLARME: -1 MINUTO ALLA TOTALITÀ! Prepararsi.")
                play_sound_alert("pre_totality")
                pre_totality_executed = True 
            
            # Avviso acustico immediato rimozione filtro solare (-12 secondi a C2)
            if now_time >= WARN_REMOVE_FILTER and not filter_remove_warned:
                print(f"\n\n[!!!] AZIONE: TOGLIERE IL FILTRO SOLARE ORA! [!!!]")
                play_sound_alert("start_totality")
                filter_remove_warned = True

            # Gestione scatti intervallati (Utilizza INTERVAL_INGRESS = 1080s)
            if current_sim_ts - last_partial_shot_sim_ts >= INTERVAL_INGRESS:
                capture_image("Parziale_Ingresso")
                last_partial_shot_sim_ts = current_sim_ts
                
        # ----------------------------------------------------------------------
        # 3. FASE ANELLO DI DIAMANTE IN INGRESSO (C2 Burst - 4 Scatti x Esposizione)
        # ----------------------------------------------------------------------
        elif START_DIAMOND_BURST <= now_time < START_CORONA_BRACKET and not diamond_burst_c2_executed:
            print(f"\n\n[>>>] ENTRATA FASE DIAMANTE (C2). Esecuzione raffiche veloci...")
            
            for speed in DIAMOND_EXPOSURES:
                set_shutter_speed(speed)
                clock.sleep(0.05, critical=True)  # Latenza hardware minima ricezione comando
                
                # Esegue la quadruplicazione dello scatto sullo stesso tempo stabilizzato
                for shot_num in range(1, 5):
                    capture_image(f"C2_Diamond_{speed.replace('/', '_')}_shot{shot_num}")
                    clock.sleep(0.15, critical=True) # Svuotamento buffer macchina veloce
            
            if now_time >= START_CORONA_BRACKET:
                diamond_burst_c2_executed = True

        # ----------------------------------------------------------------------
        # 4. FASE TOTALE: BRACKETING PROFONDO DELLA CORONA SOLARE
        # ----------------------------------------------------------------------
        elif START_CORONA_BRACKET <= now_time <= TOTALITY_END and not totality_executed:
            print(f"\n\n[!!!] FASE TOTALE: AVVIO BRACKETING CORONA PROFONDA ({now_time.strftime('%H:%M:%S')})")
            
            sim_seconds_left = (datetime.combine(datetime.today(), TOTALITY_END) - clock.now()).total_seconds()
            real_seconds_left = sim_seconds_left / SIM_SPEED_UP if SIMULATION_MODE else sim_seconds_left
            real_end_time = time.time() + real_seconds_left
            
            # Ciclo continuo a oltranza fino all'ultimo secondo della totalità
            while time.time() <= real_end_time:
                for speed in TOTALITY_EXPOSURES:
                    if time.time() > real_end_time: 
                        break
                    
                    # Controllo integrato del pre-allarme di fine totalità (-20 secondi a C3)
                    sim_now = clock.now().time()
                    if sim_now >= PRE_END_TOTALITY_TIME and not pre_end_totality_executed:
                        print(f"\n\n[!!!] AVVISO SAFETY: -20 SECONDI ALLA FINE DELLA TOTALITÀ!")
                        play_sound_alert("pre_end_totality")
                        pre_end_totality_executed = True
                    
                    # Esecuzione scatto bracketing
                    set_shutter_speed(speed)
                    clock.sleep(0.1, critical=True)
                    capture_image(f"Totalita_Corona_{speed.replace('/', '_')}")
                    
                    # Calcolo dinamico dei tempi di scrittura del sensore per evitare blocchi specchio
                    exp_time = calculate_exposure_wait(speed)
                    buffer_time = 2.5 if exp_time >= 1.0 else 1.4
                    wait_time = exp_time + (buffer_time if not SIMULATION_MODE else buffer_time / 2)
                    clock.sleep(wait_time, critical=True) 
            
            # Chiusura della finestra totale (Contatto C3)
            print(f"\n\n[!] FINE TOTALITÀ ({clock.now().strftime('%H:%M:%S')}). RIMONTARE FILTRO SOLARE IMMEDIATAMENTE!")
            play_sound_alert("end_totality")
            set_shutter_speed("1/1000") # Reset di sicurezza del tempo per la parzialità
            totality_executed = True
            # Allinea il timer parziale all'orario attuale per ripartire pulito in uscita
            last_partial_shot_sim_ts = clock.now().timestamp()
                
        # ----------------------------------------------------------------------
        # 5. FASE PARZIALE IN USCITA (C3 -> C4 / Tramonto)
        # ----------------------------------------------------------------------
        elif TOTALITY_END < now_time <= P3_END:
            # Gestione scatti intervallati corti (Utilizza INTERVAL_EGRESS = 690s)
            if current_sim_ts - last_partial_shot_sim_ts >= INTERVAL_EGRESS:
                capture_image("Parziale_Uscita")
                last_partial_shot_sim_ts = current_sim_ts
                
        # ----------------------------------------------------------------------
        # 6. FINE DELL'EVENTO
        # ----------------------------------------------------------------------
        else:
            print(f"\n\n[+] Automazione completata con successo alle ore {now_time.strftime('%H:%M:%S')}.")
            break
            
        clock.sleep(0.1)

if __name__ == "__main__":
    run_eclipse_automation()
