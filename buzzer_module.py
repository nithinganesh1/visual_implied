#!/usr/bin/env python3
"""
Buzzer Module (Passive Buzzer with PWM)
Continuous tone with frequency modulation based on proximity
Raspberry Pi 5 Compatible
"""

import time
import threading
from gpiozero import PWMLED
from utils import logger


class BuzzerModule:
    """Handles passive buzzer with continuous PWM tone control"""
    
    def __init__(self, buzzer_pin=26):
        """
        Initialize passive buzzer
        
        Args:
            buzzer_pin: GPIO pin for buzzer PWM (default 26)
        """
        self.buzzer_pin = buzzer_pin
        self.lock = threading.Lock()
        self.current_frequency = None
        self.current_volume = 0.8
        
        # Continuous tone control
        self.tone_running = False
        self.tone_thread = None
        self.target_frequency = None
        self.target_volume = None
        
        try:
            logger.info(f"Initializing Buzzer on GPIO {buzzer_pin}")
            # PWM LED for passive buzzer control
            self.buzzer = PWMLED(buzzer_pin)
            self.buzzer.off()  # Ensure off initially
            logger.info("Buzzer initialized")
            
        except Exception as e:
            logger.error(f"Buzzer initialization failed: {e}")
            self.buzzer = None
            raise
    
    def _continuous_tone(self, volume=0.8):
        """
        Play continuous tone (runs in background thread)
        Simple PWM approach: on/off rapidly to simulate frequency
        
        Args:
            volume: Volume 0-1
        """
        while self.tone_running:
            try:
                with self.lock:
                    if not self.tone_running:
                        break
                    vol = self.target_volume if self.target_volume else volume
                    freq = self.target_frequency if self.target_frequency else 1000
                
                # Calculate on/off timing based on frequency
                # Higher frequency = shorter on/off cycle
                period = 1.0 / freq  # Period in seconds
                on_time = period * 0.5 * vol  # 50% duty cycle * volume
                off_time = period * 0.5
                
                # PWM simulation
                self.buzzer.on()
                time.sleep(on_time)
                self.buzzer.off()
                time.sleep(off_time)
                
            except Exception as e:
                logger.error(f"Continuous tone error: {e}")
                break
    
    def play_continuous(self, frequency=1000, volume=0.8):
        """
        Start continuous tone playback (non-blocking)
        
        Args:
            frequency: Frequency in Hz (1000=standard, 2000=high, 500=low)
            volume: Volume 0-1
        """
        if self.tone_running:
            logger.debug("Tone already playing")
            return
        
        self.tone_running = True
        self.target_frequency = frequency
        self.target_volume = volume
        
        self.tone_thread = threading.Thread(
            target=self._continuous_tone,
            args=(volume,),
            daemon=True
        )
        self.tone_thread.start()
        logger.info(f"Continuous tone started: {frequency}Hz")
    
    def stop_tone(self):
        """Stop continuous tone immediately"""
        with self.lock:
            self.tone_running = False
        
        if self.tone_thread and self.tone_thread.is_alive():
            self.tone_thread.join(timeout=0.5)
        
        if self.buzzer:
            self.buzzer.off()
        
        logger.debug("Tone stopped")
    
    def beep(self, duration=0.1, frequency=1000, volume=None):
        """
        Play a single beep (simple, doesn't block main code)
        
        Args:
            duration: Duration in seconds
            frequency: Frequency in Hz
            volume: Volume 0-1 (None uses default)
        """
        vol = volume if volume is not None else self.current_volume
        
        thread = threading.Thread(
            target=self._beep_thread,
            args=(duration, frequency, vol),
            daemon=True
        )
        thread.start()
    
    def _beep_thread(self, duration, frequency, volume):
        """Background thread for single beep"""
        try:
            self.play_continuous(frequency=frequency, volume=volume)
            time.sleep(duration)
            self.stop_tone()
        except Exception as e:
            logger.error(f"Beep error: {e}")
    
    def obstacle_warning_adaptive(self, distance_cm, max_distance=30):
        """
        Play adaptive warning based on distance
        
        Proximity-based pattern:
        - 20cm< : 2s tone, 2s interval     (closest - continuous alarm)
        - 10-20cm : 1s tone, 1s interval   (close - fast warning)
        - 5-10cm : 0.5s tone, 0.5s interval (very close - rapid)
        - <5cm : continuous tone
        
        Args:
            distance_cm: Distance in centimeters
            max_distance: Maximum threshold distance
        """
        # Determine pattern based on distance
        if distance_cm < 5:
            # Very close - continuous warning
            self.play_continuous(frequency=2000, volume=0.9)
        
        elif distance_cm < 10:
            # 0.5s beep, 0.5s interval pattern
            logger.info(f"Rapid beep pattern: {distance_cm:.1f}cm")
            self._beep_pattern(
                beep_duration=0.5,
                interval=0.5,
                beep_frequency=2000,
                volume=0.85
            )
        
        elif distance_cm < 20:
            # 1s beep, 1s interval pattern
            logger.info(f"Fast beep pattern: {distance_cm:.1f}cm")
            self._beep_pattern(
                beep_duration=1.0,
                interval=1.0,
                beep_frequency=1500,
                volume=0.8
            )
        
        else:
            # 2s beep, 2s interval pattern
            logger.info(f"Slow beep pattern: {distance_cm:.1f}cm")
            self._beep_pattern(
                beep_duration=2.0,
                interval=2.0,
                beep_frequency=1000,
                volume=0.7
            )
    
    def _beep_pattern(self, beep_duration, interval, beep_frequency, volume):
        """
        Play beep pattern in background thread
        
        Args:
            beep_duration: Duration of each beep
            interval: Time between beeps
            beep_frequency: Frequency in Hz
            volume: Volume 0-1
        """
        thread = threading.Thread(
            target=self._beep_pattern_thread,
            args=(beep_duration, interval, beep_frequency, volume),
            daemon=True
        )
        thread.start()
    
    def _beep_pattern_thread(self, beep_duration, interval, frequency, volume):
        """Background thread for beep patterns"""
        try:
            # Play continuous tone for beep_duration
            self.play_continuous(frequency=frequency, volume=volume)
            time.sleep(beep_duration)
            self.stop_tone()
            
            # Silent interval
            time.sleep(interval)
            
            # Restart pattern if still needed
            if self.tone_running:
                self._beep_pattern(beep_duration, interval, frequency, volume)
        
        except Exception as e:
            logger.error(f"Beep pattern error: {e}")
    
    def set_volume(self, volume):
        """
        Set default buzzer volume
        
        Args:
            volume: Volume 0-1 (0=off, 1=max)
        """
        volume = max(0, min(1, volume))
        self.current_volume = volume
        logger.info(f"Buzzer volume set to {volume:.1%}")
    
    def cleanup(self):
        """Cleanup buzzer"""
        logger.info("Cleaning up buzzer")
        self.stop_tone()
        
        if self.buzzer:
            self.buzzer.close()
        
        logger.info("Buzzer cleanup complete")

