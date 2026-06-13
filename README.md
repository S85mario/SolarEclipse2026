# Universal Total Solar Eclipse Automation Script

A Python automation script developed to manage the entire photographic session during the Total Solar Eclipse on August 12, 2026 (Primary observation site: Galicia, Spain).

The engine interfaces directly with the **digiCamControl** Command Line Utility (`CameraControlRemoteCmd.exe`) to drive the camera body via USB. This eliminates human error and manages critical astronomical contact windows with millisecond-level precision.

---

## ⚡ Key Features & Optimizations

### 1. Zero-Overhead USB Protocol (Maximum Speed)
During the totality core, every single millisecond is vital. The script is stripped of any processing overhead to prevent USB bus bottlenecks and PC CPU spikes:
* It fires the raw hardware `capture` command with no extra arguments.
* **No real-time file transfer:** The camera must be configured to write exclusively to its internal SD card, leveraging the mirrorless camera's native hardware buffer.
* **Zero string manipulation or file renaming** takes place during the core totality loop, mitigating any risk of interface freezing.

### 2. Granular Control & Isolated Exposure Pools
Shutter speed management is split into three independent, clean Python lists at the very top of the script. This allows for instant adjustments without messing with the core loop logic:
* **Prominences:** Ultra-fast shutter speeds dedicated to freezing plasma structures on the solar chromosphere without saturating the red channel.
* **Corona:** A progressive dynamic ramp (ranging from fast to long exposures) to capture the full structural detail of both the inner and outer corona.
* **Burst C2/C3:** High-speed sequences dedicated to capturing Baily's Beads and the Diamond Ring effect right at the contact thresholds.

### 3. Anti-Vibration Redundancy (3-Shot Burst)
For every exposure step defined in the HDR ladder, the script executes a **3-shot consecutive burst** before sending the command to switch the shutter speed (`set shutterspeed`). This provides crucial statistical redundancy against micro-blurring caused by wind gusts or mechanical shutter vibrations.

### 4. Emergency Hot-Resume Protocol
In the event of a system crash, accidental cable disconnection, or an unexpected PC reboot on the field, the engine performs an instantaneous timestamp validation upon startup. The script automatically detects the ongoing phase of the eclipse, skips past events, and resynchronizes the shooting sequence in less than 2 seconds.

### 5. Field Telemetry & Power Monitoring
Native integration with system telemetry libraries keeps track of the laptop's power status. If the battery drops below a critical threshold of 20% while disconnected from the power bank (19V / 3.42A), the script triggers high-frequency audio alerts to warn the operator without interrupting the active capture loop.

---

## ⚙️ Exposure Ladder Configuration

Customizing your HDR bracket is as simple as editing the values inside Section 1 of the script:

```python
# 1. PROMINENCE LEVEL (Plasma / Chromosphere)
SHUTTER_SPEEDS_PROMINENCES = [
    "1/8000", "1/4000", "1/2000", "1/1000", "1/500"
]

# 2. SOLAR CORONA LEVEL (Inner & Outer Corona)
SHUTTER_SPEEDS_CORONA = [
    "1/250", "1/125", "1/60", "1/30", "1/15", "1/8", "1/4", "0.5", "1"
]

# 3. CRITICAL BURST SPEEDS FOR C2 & C3 (Diamond Ring)
SHUTTER_SPEEDS_BURST = ["1/8000", "1/4000", "1/2000", "1/1000"]

📋 Mandatory Pre-Flight Checklist

Upon execution, the script forces the operator to manually validate the hardware state via the terminal before entering the live countdown. Ensure you follow this exact sequence:

    Connection Order: Turn the camera ON -> Connect the shielded USB cable to the PC -> Launch the script.

    Optics: Solar ND filter firmly mounted for the partial phases. Lens focus set to MANUAL (MF) and physically taped down to prevent any accidental focus hunting.

    Camera Mode: Camera body dial must be set to strict Manual (M). ISO and Aperture must be configured manually beforehand (the script will only adjust shutter speeds).

    Storage Configuration: Set the camera storage destination EXCLUSIVELY to the internal SD card (disable the PC-only or split-saving transfer modes inside digiCamControl).

🛠️ System Requirements

    OS: Windows 10 / 11

    Software: digiCamControl (installed in its default path: C:\Program Files (x86))

    Python: Version 3.8 or higher

    Optional Dependencies: psutil (for power telemetry monitoring), ephem (for live GPS coordinate/astronomical contact tracking).