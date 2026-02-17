#!/usr/bin/env python3
"""
Smart Assistive Navigation System for Visually Impaired Users
Main Entry Point - Raspberry Pi 5 Optimized
"""

import sys
import time
import signal
from threading import Event

from detector import ObjectDetector
from button_handler import ButtonHandler
from decision_engine import DecisionEngine
from audio_manager import AudioManager
from gps_module import GPSModule
from gsm_module import GSMModule
from ocr_module import OCRModule
from ultrasonic_module import UltrasonicModule
from buzzer_module import BuzzerModule
from utils import logger

class NavigationSystem:
    """Main system orchestrator"""
    
    def __init__(self):
        self.running = Event()
        self.running.set()
        
        # Initialize modules
        logger.info("Initializing Smart Navigation System...")
        
        try:
            # Core components
            self.audio = AudioManager()
            self.detector = ObjectDetector(model_path="best.pt", include_currency=True)
            self.gps = GPSModule()
            self.gsm = GSMModule(phone_number="+916282670289")
            self.decision_engine = DecisionEngine(self.audio)
            self.ocr = OCRModule(languages=['en', 'hi'], gpu=False)
            
            # Button handler (will manage button events)
            self.button_handler = ButtonHandler(
                on_single_press=self.handle_single_press,
                on_double_press=self.handle_double_press,
                on_emergency_button=self.handle_emergency,
                on_ocr_button=self.handle_ocr_button
            )
            
            # Optional: Ultrasonic sensor and Buzzer (run independently in background threads)
            try:
                self.buzzer = BuzzerModule(buzzer_pin=26)
                self.ultrasonic = UltrasonicModule(
                    trigger_pin=23, 
                    echo_pin=24, 
                    threshold_distance=30  # Alert when object < 30cm
                )
                # Connect obstacle detection to buzzer feedback
                self.ultrasonic.on_obstacle_alert = self._on_obstacle_detected
                self.ultrasonic.on_obstacle_clear = self._on_obstacle_cleared
                logger.info("Ultrasonic and Buzzer modules initialized")
            except Exception as e:
                logger.warning(f"Ultrasonic/Buzzer initialization failed: {e} (will continue without them)")
                self.buzzer = None
                self.ultrasonic = None
            
            # System state
            self.last_scan_results = None
            self.waiting_for_crossing_confirmation = False
            self.confirmation_timer = None
            
            logger.info("System initialization complete")
            self.audio.speak("Navigation system ready")
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            sys.exit(1)
    
    def handle_single_press(self):
        """Handle single button press - perform one-time scan"""
        logger.info("Single press detected - performing scene scan")
        self.audio.speak("Scanning")

        try:
            detections = self.detector.detect_once()

            if not detections:
                print("No objects detected")
                self.audio.speak("No significant objects detected")
                return

            # Print all detections (clean format)
            print("\n=== DETECTIONS ===")
            for d in detections:
                print(
                    f"{d['class']} | "
                    f"conf: {d['confidence']:.2f} | "
                    f"{d['location']} | "
                    f"{d['distance']}"
                )

            # Show highest priority object
            top = detections[0]
            print("\n>>> HIGHEST PRIORITY:")
            print(
                f"{top['class']} | "
                f"{top['location']} | "
                f"{top['distance']}"
            )

            # Store results
            self.last_scan_results = detections

            # Speak result
            summary = self.decision_engine.analyze_scene(detections)

            # Zebra confirmation logic
            zebra_detected = any(d['class'] == 'zebra' for d in detections)

            if zebra_detected:
                self.waiting_for_crossing_confirmation = True
                self.audio.speak(
                    "Zebra crossing detected. Do you want to check if it is safe to cross?"
                )

                import threading
                self.confirmation_timer = threading.Timer(
                    3.0, self.cancel_confirmation
                )
                self.confirmation_timer.start()

        except Exception as e:
            logger.error(f"Scan error: {e}")
            self.audio.speak("Scan error occurred")

        
    def handle_double_press(self):
        """Handle double press - confirm crossing safety check"""
        if self.waiting_for_crossing_confirmation:
            # Cancel timeout timer
            if self.confirmation_timer:
                self.confirmation_timer.cancel()
            
            logger.info("Double press - confirming crossing safety check")
            self.waiting_for_crossing_confirmation = False
            
            # Run crossing safety analysis
            self.check_crossing_safety()
        else:
            logger.info("Double press ignored - no pending confirmation")
    
    def cancel_confirmation(self):
        """Cancel crossing confirmation if timeout reached"""
        if self.waiting_for_crossing_confirmation:
            logger.info("Crossing confirmation timeout - canceling")
            self.waiting_for_crossing_confirmation = False
            self.audio.speak("Confirmation timeout")
    
    def check_crossing_safety(self):
        """Analyze crossing safety with vehicle motion detection"""
        logger.info("Checking crossing safety...")
        self.audio.speak("Checking crossing safety")
        
        try:
            # Perform multi-frame analysis for vehicle motion
            is_safe, reason = self.decision_engine.check_crossing_safety(
                self.detector,
                num_frames=5,
                interval=0.2
            )
            
            if is_safe:
                self.audio.speak(f"Safe to cross. {reason}")
            else:
                self.audio.speak(f"Not safe to cross. {reason}")
                
        except Exception as e:
            logger.error(f"Crossing safety check error: {e}")
            self.audio.speak("Safety check error")
    
    def handle_emergency(self):
        """Handle emergency alert - press and hold or emergency button"""
        logger.info("EMERGENCY TRIGGERED")
        self.audio.speak("Sending emergency alert")
        
        try:
            # Get current GPS location
            location = self.gps.get_location()
            
            if location:
                lat, lon = location
                maps_link = f"https://maps.google.com/?q={lat},{lon}"
                message = f"EMERGENCY ALERT! Location: {lat},{lon} - {maps_link}"
            else:
                message = "EMERGENCY ALERT! Location unavailable."
            
            # Send SMS
            success = self.gsm.send_sms(message)
            
            if success:
                self.audio.speak("Emergency alert sent successfully")
                logger.info(f"Emergency SMS sent: {message}")
            else:
                self.audio.speak("Emergency alert failed. Please seek help nearby.")
                logger.error("Emergency SMS failed")
                
        except Exception as e:
            logger.error(f"Emergency handler error: {e}")
            self.audio.speak("Emergency alert failed")
    
    def handle_ocr_button(self):
        """Handle OCR button press - read text from latest frame"""
        logger.info("OCR button pressed - extracting text from frame")
        self.audio.speak("Extracting text")
        
        try:
            # Get the latest frame
            frame = self.detector.get_latest_frame()
            
            if frame is None:
                logger.error("No frame available for OCR")
                self.audio.speak("No frame available. Please try again")
                return
            
            # Perform OCR
            extracted_text, detections, annotated_frame = self.ocr.extract_text(frame)
            
            if extracted_text:
                logger.info(f"Extracted text: {extracted_text}")
                self.audio.speak(f"Text found: {extracted_text}")
                print(f"\n=== EXTRACTED TEXT ===")
                print(extracted_text)
                print(f"Detections: {len(detections)}")
                for det in detections:
                    print(f"  - {det['text']} (confidence: {det['confidence']:.2f})")
            else:
                logger.info("No text detected in frame")
                self.audio.speak("No text detected in the frame")
        
        except Exception as e:
            logger.error(f"OCR handler error: {e}")
            self.audio.speak("Error during text extraction")
    
    def _on_obstacle_detected(self, distance_cm):
        """Callback when ultrasonic detects obstacle within threshold"""
        logger.warning(f"Obstacle detected at {distance_cm:.1f}cm")
        
        # Provide buzzer and audio feedback
        if self.buzzer:
            # Play warning pattern based on distance (closer = faster)
            proximity = 1.0 - (distance_cm / 30.0)  # Normalize to 0-1
            self.buzzer.obstacle_warning_continuous(proximity_ratio=proximity, cycles=2)
        
        # Optional: Also speak alert
        if distance_cm < 20:
            self.audio.speak("Obstacle very close", priority=1)
        elif distance_cm < 30:
            self.audio.speak("Obstacle ahead", priority=2)
    
    def _on_obstacle_cleared(self):
        """Callback when obstacle is cleared"""
        logger.info("Obstacle cleared")
        
        # Play confirmation beep
        if self.buzzer:
            self.buzzer.beep_async(duration=0.1, frequency='done', volume=0.6)
    
    def shutdown(self, signum=None, frame=None):
        """Clean shutdown"""
        logger.info("Shutting down navigation system...")
        self.audio.speak("System shutting down")
        
        self.running.clear()
        
        # Cleanup modules
        if hasattr(self, 'button_handler'):
            self.button_handler.cleanup()
        if hasattr(self, 'detector'):
            self.detector.cleanup()
        if hasattr(self, 'gps'):
            self.gps.cleanup()
        if hasattr(self, 'audio'):
            self.audio.cleanup()
        if hasattr(self, 'ocr'):
            self.ocr.cleanup()
        if hasattr(self, 'ultrasonic') and self.ultrasonic:
            self.ultrasonic.cleanup()
        if hasattr(self, 'buzzer') and self.buzzer:
            self.buzzer.cleanup()
        
        logger.info("Shutdown complete")
        sys.exit(0)
    
    def run(self):
        """Main run loop"""
        # Register signal handlers
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)
        
        logger.info("Navigation system running. Press button to scan.")
        
        try:
            # Keep main thread alive while button events are handled
            while self.running.is_set():
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            self.shutdown()


def main():
    """Application entry point"""
    try:
        system = NavigationSystem()
        system.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
