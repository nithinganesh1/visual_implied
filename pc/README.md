PC Smart Navigation — README

Overview

This folder contains the PC version of the Smart Navigation system: voice-controlled live camera detection using a YOLO model and Vosk for speech recognition. The camera continuously runs detection and updates a live preview; voice commands trigger actions (e.g., announce current detections).

Key files

- [main.py](main.py): PC entrypoint and orchestrator (voice listener, preview thread, scan/crossing handlers).
- [detector.py](detector.py): ObjectDetector using YOLO for frame-by-frame detection. Supports an `include_currency` toggle.
- [decision_engine.py](decision_engine.py): Scene analysis and crossing safety checks. Produces text summaries and (optionally) queued per-item TTS.
- [audio_manager.py](audio_manager.py): Threaded TTS queue using `pyttsx3`.
- [currency.py](currency.py): Quick test script that loads `best.pt` and draws model annotations (useful to verify the model + camera).
- [VoiceCommandManager.py](VoiceCommandManager.py): Voice helper used as reference for Vosk usage.
- [requirements.txt](requirements.txt): Python dependencies used by the PC app.

Quick setup

1. Create a virtualenv and install deps:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Ensure `best.pt` (YOLO model) is present in this folder and the Vosk model directory `vosk-model-small-en-us-0.15` exists.

Run (PC)

From the `pc` folder:

```bash
python main.py
```

Behavior and commands

- Continuous detection: the preview thread continuously runs `detector.detect_frame()` and shows a live window named "Navigation Camera" with annotated boxes.
- "scan" (voice): when you say a phrase containing `scan` the system will read out a concise summary of the latest detections immediately.
- "cross" (voice): triggers crossing safety check (multi-frame motion + lights + zebra logic) and announces `Safe to cross` or `Not safe to cross`.
- "quit" or "stop" (voice): stops the system.
- Preview window: press `q` to close the preview and shutdown.

Notes about voice recognition

- The Vosk model is used with a 16 kHz audio stream. Microphone access and correct sampling are required.
- Recognizer looks for substrings: the code checks `if "scan" in command`, `if "cross" in command`, and `if "quit" in command or "stop" in command`.
- If speech is misrecognized, try speaking clearly or test with `VoiceCommandManager.py`.

Currency detection

- `currency.py` is a minimal test script that runs the same YOLO model and displays annotations; you said this script detects currency correctly.
- `ObjectDetector` has an `include_currency` option. `main.py` is instantiated with `include_currency=True` so currency classes should be reported. To toggle at runtime:

```python
system.detector.set_include_currency(False)  # disable
system.detector.set_include_currency(True)   # enable
```

How scanning announces results

- The preview thread keeps a thread-safe `latest_detections` list.
- When you say `scan`, `scan_scene()` reads `latest_detections`, asks `DecisionEngine.analyze_scene(..., speak=False)` for a single text summary, then calls `audio.speak_immediately(summary)` so you hear one concise announcement rather than many queued items.

Troubleshooting and common issues

- Qt font warning: OpenCV/Qt may log "Cannot find font directory..." — this is informational and can be ignored, or you can install system fonts (e.g., DejaVu) if desired.
- Camera "Device or resource busy": caused by multiple readers accessing the same device. The app uses a camera lock and runs detection in one preview thread; ensure no other process (e.g., `cheese`, another script) is using the camera.
- If the camera freezes after a scan: update to the latest code (this repo uses a single preview thread + detector lock to avoid conflicts). If still frozen, try switching camera index (0 or 1) in `main.py` and `currency.py`.
- If nothing is detected in `main.py` but `currency.py` works: confirm `main.py` sets `include_currency=True` and that the YOLO model path is identical (`best.pt`). Also check that the preview thread is running (errors logged to console).
- Microphone issues: require permission and correct sampling rate (16 kHz). If no voice commands are recognized, run `VoiceCommandManager.py` to test microphone + Vosk.

Developer notes / next steps

- To add a runtime voice command to toggle currency detection, add a branch in `run()` to detect phrases like "enable currency" / "disable currency" and call `self.detector.set_include_currency(...)`.
- To reduce false triggers, increase `CONFIDENCE_THRESHOLD` in `detector.py`.
- To debug detections, run `currency.py` (quick visual confirmation) or add logging to `detector.detect_frame()`.

Contact / test checklist

- Quick checks:
  - `python currency.py` — verify model + camera annotate currency.
  - `python main.py` — say "scan" and confirm spoken summary.
  - If issues persist, provide console output and I can help pinpoint further.

License / attribution

This README is a concise developer guide for the PC folder. Adjust the camera index, model path, or Vosk model path as needed for your environment.
