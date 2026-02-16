#!/usr/bin/env python3
"""
Smart Navigation System - PC Version
Voice Controlled + Live Camera
No Hardware Dependencies
"""

import cv2
import threading
import time
try:
    from gpiozero import Button
    HAS_GPIO = True
except Exception:
    HAS_GPIO = False

from detector import ObjectDetector
from decision_engine import DecisionEngine
from audio_manager import AudioManager


class PCNavigationSystem:

    def __init__(self):
        print("Initializing PC Navigation System...")

        # Core modules
        self.audio = AudioManager()
        # Enable currency detection to match currency.py behavior
        self.detector = ObjectDetector(model_path="best.pt", camera_index=1, include_currency=True)
        self.decision_engine = DecisionEngine(self.audio)

        # Camera lock for thread-safe access
        self.camera_lock = threading.Lock()
        self.detector.set_camera_lock(self.camera_lock)
        # Latest detections (continuously updated by preview thread)
        self.latest_detections = []
        self.detections_lock = threading.Lock()

        # Button setup (GPIO if available) or fallback to keyboard
        self.scan_button = None
        if HAS_GPIO:
            try:
                self.scan_button = Button(17, pull_up=True, hold_time=2.0)
                # Short press -> scan; hold -> check crossing
                self.scan_button.when_pressed = lambda: threading.Thread(target=self.scan_scene, daemon=True).start()
                self.scan_button.when_held = lambda: threading.Thread(target=self.check_crossing, daemon=True).start()
                print("Using GPIO button on pin 17: press to scan, hold to check crossing")
            except Exception as e:
                print("GPIO initialization failed:", e)
                self.scan_button = None
        else:
            print("No GPIO available — use keyboard commands: scan | crossing | quit")

        self.running = True

        self.audio.speak_immediately("Navigation system ready")
        print("Say: scan | crossing | quit")

    # --------------------------------------------------
    # VOICE LISTENER
    # --------------------------------------------------

    # No voice listener on PC — scanning is triggered by button or keyboard

    # --------------------------------------------------
    # MAIN LOOP
    # --------------------------------------------------

    def run(self):
        # Start camera preview thread
        camera_thread = threading.Thread(target=self.camera_preview, daemon=True)
        camera_thread.start()

        # If GPIO button present, button callbacks will trigger actions
        if HAS_GPIO and self.scan_button:
            while self.running:
                time.sleep(0.1)
        else:
            # Fallback: simple keyboard input loop
            print("Type a command (scan | crossing | quit) and press Enter")
            while self.running:
                try:
                    command = input().strip().lower()
                except EOFError:
                    break

                if not command:
                    continue

                print("Heard:", command)

                if "scan" in command:
                    self.scan_scene()
                elif "cross" in command or "crossing" in command:
                    self.check_crossing()
                elif "quit" in command or "stop" in command:
                    self.shutdown()

    # --------------------------------------------------
    # CAMERA PREVIEW
    # --------------------------------------------------
    def camera_preview(self):
        while self.running:
            # detector.detect_frame now returns (detections, frame)
            detections, _ = self.detector.detect_frame()

            # update latest detections thread-safely
            with self.detections_lock:
                self.latest_detections = detections

            # No GUI display on headless systems; small sleep to yield
            time.sleep(0.01)
        # Release camera when stopping
        self.detector.cap.release()
        try:
            cv2.destroyAllWindows()
        except Exception:
            pass

    # --------------------------------------------------
    # SCAN SCENE
    # --------------------------------------------------

    def scan_scene(self):
        self.audio.speak("Scanning")

        # Use the most recent detections from the preview thread
        with self.detections_lock:
            detections = list(self.latest_detections)

        if not detections:
            self.audio.speak("No significant objects detected")
            return

        print("\n=== DETECTIONS ===")
        for d in detections:
            print(
                f"{d['class']} | "
                f"conf: {d['confidence']:.2f} | "
                f"{d['location']} | "
                f"{d['distance']}"
            )

        summary = self.decision_engine.analyze_scene(detections, speak=False)

        if summary:
            # Speak immediately the concise summary of detections
            self.audio.speak_immediately(summary)

    # --------------------------------------------------
    # CROSSING CHECK
    # --------------------------------------------------

    def check_crossing(self):
        self.audio.speak("Checking crossing safety")

        is_safe, reason = self.decision_engine.check_crossing_safety(
            self.detector,
            num_frames=5,
            interval=0.2
        )

        if is_safe:
            self.audio.speak_immediately(f"Safe to cross. {reason}")
        else:
            self.audio.speak_immediately(f"Not safe to cross. {reason}")

    # --------------------------------------------------
    # CLEAN SHUTDOWN
    # --------------------------------------------------

    def shutdown(self):
        print("Shutting down...")
        self.running = False
        self.audio.cleanup()
        cv2.destroyAllWindows()


# --------------------------------------------------
# ENTRY
# --------------------------------------------------

if __name__ == "__main__":
    system = PCNavigationSystem()
    system.run()
