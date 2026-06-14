📖 Solar Eclipse Automation System - User Manual
🌟 Overview

Professional automation system for photographing total solar eclipses. Designed to handle complex HDR sequences with hot-resume support, hardware telemetry, and simulation mode.
📋 System Requirements
Minimum Hardware

    Windows 10/11 PC (low-power laptops work too)

    4GB RAM

    500MB free disk space

    USB 2.0 or higher port

Recommended Hardware

    SSD for fast log writing

    Backup battery for PC

    CPU temperature monitoring (with psutil)

Supported Cameras

    CANON (tested with EOS series)

    NIKON (theoretical support via digiCamControl)

    SONY (theoretical support)

Required Software

    Windows 10/11

    digiCamControl (free) - Download here

    Python 3.8+

Optional Python Libraries
bash

# For advanced telemetry
pip install psutil

# For GPS astronomical calculations
pip install ephem

# No libraries are mandatory - the script works without them!

🚀 Quick Installation
1. Standard Installation
bash

# Clone or download the repository
git clone https://github.com/S85mario/Solar-Eclipse-Automation.git
cd solar-eclipse-automation

# (Optional) Install additional libraries
pip install psutil ephem

# Verify files are present:
# - SolarEclipse_IT.py
# - config_eclipse.json

2. Initial Configuration

    Install digiCamControl from digicamcontrol.com

    Connect camera via USB

    Launch digiCamControl and verify connection

    Set camera to MANUAL mode (M)

3. Quick Test
bash

# Enable simulation mode in JSON file
"sim_mode": true

# Run the script
python SolarEclipse_IT.py

# Verify logs are generated correctly

⚙️ Detailed Configuration
config_eclipse.json File Structure
<<<<<<< HEAD
json  https://github.com/S85mario/Solar-Eclipse-Automation/blob/main/config_SolarEclipse_IT.json


=======
json https://github.com/S85mario/Solar-Eclipse-Automation/blob/main/config_SolarEclipse_IT.json


📝 Advanced Configuration Guide
Geographic Coordinates - DMS Format
json

// Valid examples:
"latitudine_dms": "45°27'52.5\"N"    // Degrees, minutes, seconds
"longitudine_dms": "12°15'30.0\"E"
"latitudine_dms": "-45.4642"          // Decimal degrees (alternative)

Shutter Speed Formats Supported
json

"1/8000"    // Fraction of a second
"1/500"     
"0.5"       // Half second
"2"         // Two seconds

Customizing Eclipse Phases
json

{
  "nome": "OUTER CORONA",              // Name shown in logs
  "tempo_riferimento": "totalita_inizio", // p1_inizio, totalita_inizio, totalita_fine
  "durata_sec": 45,                    // Phase duration in seconds
  "lista_tempi": "corona_esterna",     // hdr, burst, corona_interna, corona_esterna
  "usa_raffica": false                 // true = multiple shots per exposure
}

>>>>>>> c148c98478660985878be7ffdb85203d80b46520
Simulation vs Debug Mode
Mode	Use Case	Effects
sim_mode: true	Feature testing	No real camera commands
debug_mode: true	Diagnostics	Extremely detailed logs
Both false	Production	Real operation, minimal logs

🎮 Basic Usage
Running the Script
bash

python SolarEclipse_IT.py

Execution Flow

    Load configuration - Verify JSON file

    Interactive checklist - Confirm hardware preparation

    Connection test - Verify camera communication

    Auto wait - Timer until eclipse starts

    Acquisition - Automatic phase sequence

    Completion - Save logs and notification

Generated Outputs
text

project_folder/
├── eclissi_log.txt      # Complete execution log
├── eclissi_stato.json   # State for recovery (if interrupted)
├── watchdog_last.txt    # Last watchdog reset timestamp
└── config_eclipse.json  # Your configuration

🛟 Recovery from Interruption (Hot-Resume)

The script automatically saves state after each shot. In case of:

    System crash

    Accidental shutdown

    Manual interruption (Ctrl+C)

Recovery procedure:

    Restart PC/camera

    Run the script normally

    System will automatically resume from the interrupted phase

    ⚠️ Important: Do not delete eclissi_stato.json to maintain resume capability.

📊 Log Interpretation
Log Levels
Level	Meaning	Required Action
[INFO]	Normal operation	Informational only
[WARN]	Recoverable anomaly	Monitor
[ERROR]	Serious error	Check configuration
[DEBUG]	Technical detail	Only if debug_mode=true
Log Examples
text

[19:15:23] [INFO] 🚀 ECLIPSE ENGINE ACTIVE
[19:15:23] [INFO] 📷 REAL MODE
[19:27:10] [INFO] 🎯 TOTALITY time reached!
[19:27:11] [INFO] 📸 TOTALITY_INNER_CORONA_1/500_shot1
[19:27:12] [WARN] ⚠️ BATTERY AT 18% - NOT CHARGING!

🔧 Troubleshooting
Issue: "digiCamControl not found"

Solution:

    Verify digiCamControl is installed

    Check path in config_eclipse.json

    Typical path: C:\Program Files (x86)\digiCamControl\

Issue: Camera not responding

Checklist:

    Camera powered on

    USB connected directly (no hub)

    digiCamControl open and connected

    Camera in M (Manual) mode

    Camera battery charged

Issue: Wrong shutter speeds

Verifications:

    Speed format in JSON (e.g., "1/2000" not "1/2000s")

    Camera supports specified speeds

    Try simulation mode

Script freezes during wait

Possible causes:

    Watchdog not reset correctly

    System issues

Solutions:

    Reduce watchdog_interval_sec to 15

    Disable debug_mode

    Run as administrator

🧪 Simulation Mode - Testing Guide
Complete Test Configuration
json

{
  "hardware": {
    "sim_mode": true,
    "debug_mode": true
  },
  "intervalli": {
    "ingresso_parziale_sec": 10,    // Reduced for testing
    "uscita_parziale_sec": 10
  }
}

What to Verify in Simulation

    ✅ Phase logic and transitions

    ✅ Hot-resume (interrupt with Ctrl+C)

    ✅ Wait time calculations

    ✅ Error handling

    ✅ State saving

Tests to Run
bash

# Test 1: Complete execution
python SolarEclipse_IT.py

# Test 2: Interruption and resume
# Start -> Ctrl+C after 10 seconds -> Restart

# Test 3: Different configurations
# Modify tempi_scatto in JSON -> Restart

📈 Performance Optimization
For Laptop/Battery
json

{
  "intervalli": {
    "watchdog_interval_sec": 60     // Reduces frequent checks
  },
  "tempi_scatto": {
    "raffica_scatti": 2              // Fewer shots = less energy
  }
}

For Maximum Performance
json

{
  "intervalli": {
    "watchdog_interval_sec": 10     // More frequent monitoring
  },
  "hardware": {
    "debug_mode": false              // Reduces I/O overhead
  }
}

🎯 Best Practices for the Event
Before Eclipse (1 week prior)

    Full test with simulation

    Verify camera batteries (at least 2 charges)

    Format SD cards

    Backup JSON configuration

    Test prolonged USB connection (1+ hours)

Eclipse Day (3 hours before)

    Charge PC battery to 100%

    Prepare spare cables

    Test camera connection

    Verify solar filter orientation

    Lock focus with tape

During Eclipse

    Do not touch PC/camera

    Monitor logs only (no interaction)

    If possible, use external batteries

After Eclipse

    Backup logs

    Copy photos to external drive

    Don't format SD until double backup complete

❓ FAQ

Q: Can I use WiFi instead of USB?
A: Not recommended - USB latency and reliability are superior for critical events.

Q: What happens if PC battery dies?
A: On restart, hot-resume will continue from the last saved shot.

Q: Does it support video during eclipse?
A: No, focus is exclusively on HDR photos. Use a second camera for video.

Q: Can I change the sequence during execution?
A: No - all changes require restart. Use simulation mode beforehand.

Q: How many photos will it take total?
A: Approximately 60-80 depending on configuration (3x burst per exposure).
📞 Support and Contributions
Bug Reporting

Open a GitHub issue with:

    eclissi_log.txt file

    Script version

    JSON configuration

    Steps to reproduce

Suggested Improvements

    Support for other camera brands

    Automatic timing calculation with ephem

    GUI interface

    EXIF metadata export

📄 License

MIT License - Free use for non-commercial purposes.
Credits appreciated but not required.
🙏 Acknowledgments

    digiCamControl team for control software

    Italian astrophotography community for field testing

    Open source contributors

Happy eclipse! 🌞🌑📸
