# SolarEclipse2026
Automate DSLR/Mirrorless cameras for the 2026 Total Solar Eclipse via digiCamControl. Features smart C2 diamond ring burst &amp; continuous HDR corona bracketing.


# Solar Eclipse 2026 Automation Script

An advanced Python automation script designed to orchestrate DSLR/Mirrorless camera operations during the **Total Solar Eclipse on August 12, 2026, in Northern Spain**. 

Utilizing the `digiCamControl` CLI interface (`CameraControlRemoteCmd.exe`), this script completely automates tethered shooting across all critical eclipse phases. It eliminates human error and hardware communication latency, allowing photographers to focus entirely on the experience.

## Key Features

* **Dual-Phase Partial Tracking:** Independent interval configurations for Ingress (C1 -> C2) and Egress (C3 -> C4) to perfectly handle atmospheric extinction as the Sun approaches the horizon.
* **Smart Diamond Ring Burst (C2):** Minimizes USB command overhead by locking the shutter speed and firing a rapid 4-shot sequence per exposure level, maximizing the chances of capturing Baily's Beads and the perfect diamond flash.
* **Continuous Corona Bracketing:** Seamless, high-dynamic-range (HDR) looping sequence covering up to 17 exposure values ($1/8000s$ to $4s$) during the brief totality window.
* **Integrated Simulation Engine (`SimClock`):** Built-in time acceleration clock allows you to thoroughly test and review your entire sequence timeline within seconds at home before hitting the field.
* **Acoustic Warning System:** Uses system-level audio cues to alert you precisely when to remove and reinstall the physical solar ND filter.

---

## Architecture & Logic Flow

1. **Pre-Eclipse Phase:** Monitors the clock until Contact 1 (C1).
2. **Partial Ingress Phase:** Fires a set number of shots spaced out evenly (e.g., every 18 minutes).
3. **The C2 Window (-12s to +3s from Totality):** Triggers audio alert to remove the solar filter, changes shutter speed to fast safety margins, and shoots rapid 4-photo cycles.
4. **Totality Core (C2 +3s to C3):** Loops through the deep bracketing stack continuously. Triggers a safety warning 20 seconds before C3.
5. **Contact 3 (C3):** Sounds a critical alarm to slide the solar filter back on, resets exposure to standard baselines.
6. **Partial Egress Phase:** Fires symmetrically timed shots down to the horizon/C4 limit.

---

## Installation & Prerequisites

1. **Operating System:** Windows (Required for digiCamControl).
2. **Tethering Software:** Download and install [digiCamControl](http://digicamcontrol.com/). Ensure `CameraControlRemoteCmd.exe` is located in your system path or explicitly configured in the script.
3. **Python:** Python 3.6+ installed.
4. **Camera Setup:** * Connect your camera via USB.
   * Turn off all auto-focus (switch lens to **MF** and lock focus on infinity).
   * Set the camera body to **Manual Mode (M)**.
   * Ensure image saving is set to **RAW** (or RAW+JPEG).

---

## Configuration

Open the script file and update the parameters in the top section:

```python
# Path to digiCamControl remote CLI tool
CMD_PATH = r"C:\Program Files (x86)\digiCamControl\CameraControlRemoteCmd.exe"

# Real local contact timings based on your specific coordination site 
P1_START       = datetime_time(19, 30, 0)
TOTALITY_START = datetime_time(20, 27, 0)
TOTALITY_END   = datetime_time(20, 28, 45)
P3_END         = datetime_time(21, 15, 0)

# Interval spacing in seconds
INTERVAL_INGRESS = 1080  # 18 minutes split for 5 shots
INTERVAL_EGRESS  = 690   # 11.5 minutes split for 5 shots
