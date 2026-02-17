#!/usr/bin/env python3
"""
HARDWARE CONNECTION GUIDE
HC-SR04 Ultrasonic Sensor + Passive Buzzer
Raspberry Pi 5
"""

HARDWARE_SETUP = """
╔════════════════════════════════════════════════════════════════════╗
║         ULTRASONIC SENSOR (HC-SR04) + BUZZER WIRING              ║
╚════════════════════════════════════════════════════════════════════╝

┌─ HC-SR04 ULTRASONIC SENSOR ─────────────────────┐
│                                                   │
│  HC-SR04 Pin    →    Raspberry Pi 5 GPIO        │
│  ────────────────────────────────────────────    │
│  VCC             →    5V Power                   │
│  GND             →    Ground                     │
│  TRIG            →    GPIO 23 (Trigger)          │
│  ECHO            →    GPIO 24 (Echo)             │
│                                                   │
│  IMPORTANT: Add 1k resistor between ECHO and    │
│  GPIO 24 to protect from 5V signal!             │
│                                                   │
│  Wiring Diagram:                                │
│  ┌──────────┐                                   │
│  │ HC-SR04  │                                   │
│  ├──────────┤                                   │
│  │5V  - VCC ├─────────────→ [5V Power]          │
│  │GND - GND ├─────────────→ [Ground]            │
│  │TRIG ├─────────────→ [GPIO 23]                │
│  │ECHO ├──[1k Ω]──→ [GPIO 24]                   │
│  └──────────┘                                   │
│              └──→ [Ground]                      │
│                                                   │
└───────────────────────────────────────────────────┘

┌─ PASSIVE BUZZER ────────────────────────────────┐
│                                                   │
│  Buzzer Pin    →    Raspberry Pi                │
│  ──────────────────────────────────────────     │
│  (+) VCC        →    5V Power                   │
│  (-) GND        →    Ground                     │
│  Signal (PWM)   →    GPIO 26 (PWM-capable)     │
│                                                   │
│  Optional: Add 1µF capacitor across buzzer     │
│  pins for noise reduction                       │
│                                                   │
│  Wiring Diagram:                                │
│  ┌──────────┐                                   │
│  │ Buzzer   │                                   │
│  ├──────────┤                                   │
│  │ (+)      ├─────────────→ [GPIO 26 PWM]      │
│  │ (-)      ├─────────────→ [Ground]           │
│  └──────────┘                                   │
│                                                   │
└───────────────────────────────────────────────────┘

GPIO PIN REFERENCE (Raspberry Pi 5)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Specific Pins Used:
  GPIO 23   - HC-SR04 Trigger (Ultrasonic)
  GPIO 24   - HC-SR04 Echo   (Ultrasonic)
  GPIO 26   - Passive Buzzer (PWM)
  GPIO 17   - Primary Button (existing)
  GPIO 27   - OCR Button     (existing)

┌─────────────────────────────────┐
│   RASPBERRY PI 5 GPIO HEADER    │
│   (40-pin connector)            │
│                                 │
│   3V3  ├──────────────┤ GND     │
│   5V   ├──────────────┤ GND     │
│   GPIO2├──────────────┤ GPIO3   │
│   5V   ├──────────────┤ GND     │
│   GPIO4├──────────────┤ GPIO14  │
│   GND  ├──────────────┤ GPIO15  │
│   GPIO17├──────────────┤ GPIO27  │ ← OCR Button
│   GPIO22├──────────────┤ GPIO23  │ ← Ultrasonic TRIG
│   3V3  ├──────────────┤ GPIO24  │ ← Ultrasonic ECHO
│   GPIO10├──────────────┤ GPIO25  │
│   GPIO11├──────────────┤ GPIO8   │
│   GND  ├──────────────┤ GPIO7   │
│   GPIO0 ├──────────────┤ GPIO1   │
│   GPIO5 ├──────────────┤ GPIO6   │
│   GPIO12├──────────────┤ GPIO13  │
│   GND  ├──────────────┤ GPIO19  │
│   GPIO16├──────────────┤ GPIO26  │ ← Buzzer PWM
│   GPIO20├──────────────┤ GPIO21  │
│   GND  ├──────────────┤ GPIO9   │
│                                 │
└─────────────────────────────────┘

INSTALLATION & SETUP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Install dependencies:
   pip install -r requirements.txt

   For PWM support:
   sudo apt-get install python3-pigpio

2. Run hardware diagnostics:
   python3 test_sensors.py buzzer      # Test buzzer separately
   python3 test_sensors.py ultrasonic  # Test sensor separately
   python3 test_sensors.py integrated  # Test both together

3. Run main system:
   python3 main.py

   The system will automatically:
   ✓ Initialize HC-SR04 on GPIO 23/24
   ✓ Initialize Buzzer on GPIO 26
   ✓ Start background monitoring
   ✓ Warn when obstacles detected

FEATURES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Continuous distance monitoring (background thread)
✓ Automatic buzzer warning when obstacle < 30cm
✓ Frequency-based alert (closer = faster beeps)
✓ Multiple tone options:
  - beep      (1000 Hz) - standard beep
  - alert     (2000 Hz) - high alert
  - obstacle  (800 Hz)  - obstacle warning
  - done      (1200 Hz) - task complete
  - error     (500 Hz)  - error tone

✓ Completely independent from main navigation
✓ No interference with existing code
✓ Can be disabled by removing try-except catch

TROUBLESHOOTING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Issue: Buzzer not working
  → Check GPIO 26 PWM capabilty
  → Verify 5V power supply
  → Try test_sensors.py buzzer

Issue: Distance readings always 0
  → Check 1k resistor on Echo pin
  → Verify GPIO 24 connection
  → Test with test_sensors.py ultrasonic

Issue: Objects detected too far/close
  → Adjust threshold_distance in main.py (default 30cm)
  → ultrasonic.set_threshold(50)  # Change to 50cm

DISTANCES TO CUSTOMIZE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

In main.py __init__, adjust:
  threshold_distance=30    # Alert if < 30cm
  proximity_ratio          # Controls buzz speed

Code location:
  self.ultrasonic = UltrasonicModule(
      trigger_pin=23,
      echo_pin=24,
      threshold_distance=30  # ← Change here
  )

PERFORMANCE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Ultrasonic: ~ 100ms measurement interval
✓ Buzzer: Non-blocking (uses threads)
✓ CPU impact: < 5% per module
✓ Runs completely independently from detection

SUPPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

For debugging, check logs:
  tail -f /tmp/navigation.log

Enable debug mode in logger config
"""

if __name__ == "__main__":
    print(HARDWARE_SETUP)
