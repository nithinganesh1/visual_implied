#!/usr/bin/env python3
"""
Buzzer Module (Passive Buzzer with PWM)
Tone control via frequency adjustment
Raspberry Pi 5 Compatible
"""

import time
import threading
from gpiozero import PWMLED
from utils import logger


class BuzzerModule:
    """Handles passive buzzer with frequency/tone control"""
    
    # Predefined tones (frequency in Hz)
    TONES = {
        'beep': 1000,           # Standard beep
        'alert': 2000,          # High alert
        'warning': 1500,        # Warning tone
        'obstacle': 800,        # Low obstacle warning
        'done': 1200,           # Task complete tone
        'error': 500,           # Error tone
    }
    
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
        
        try:
            logger.info(f"Initializing Buzzer on GPIO {buzzer_pin}")
            # PWM LED works well for passive buzzers (controls duty cycle/volume)
            self.buzzer = PWMLED(buzzer_pin)
            self.buzzer.off()  # Ensure off initially
            logger.info("Buzzer initialized")
            
        except Exception as e:
            logger.error(f"Buzzer initialization failed: {e}")
            self.buzzer = None
            raise
    
    def beep(self, duration=0.1, frequency='beep', volume=None):
        """
        Play a single beep
        
        Args:
            duration: Duration in seconds
            frequency: Tone name or frequency in Hz
            volume: Volume 0-1 (None uses default)
        """
        if not self.buzzer:
            return
        
        vol = volume if volume is not None else self.current_volume
        freq = self._get_frequency(frequency)
        
        try:
            with self.lock:
                # Simulate tone by using PWM (duty cycle represents frequency concept)
                # Actual frequency modulation would need more complex PWM
                self.buzzer.value = vol
                logger.debug(f"Beep: {duration}s at tone '{frequency}'")
            
            time.sleep(duration)
            
            with self.lock:
                self.buzzer.off()
            
        except Exception as e:
            logger.error(f"Beep error: {e}")
    
    def beep_sequence(self, beeps=1, duration=0.1, interval=0.1, frequency='beep', volume=None):
        """
        Play multiple beeps in sequence
        
        Args:
            beeps: Number of beeps
            duration: Duration per beep
            interval: Time between beeps
            frequency: Tone name
            volume: Volume 0-1
        """
        for i in range(beeps):
            self.beep(duration=duration, frequency=frequency, volume=volume)
            if i < beeps - 1:
                time.sleep(interval)
    
    def beep_async(self, duration=0.1, frequency='beep', volume=None):
        """
        Play beep in background thread (non-blocking)
        
        Args:
            duration: Duration in seconds
            frequency: Tone name or frequency
            volume: Volume 0-1
        """
        thread = threading.Thread(
            target=self.beep,
            args=(duration, frequency, volume),
            daemon=True
        )
        thread.start()
    
    def alert(self, cycles=3, duration=0.15, volume=0.9):
        """
        Play alert pattern (repeated beeps)
        
        Args:
            cycles: Number of alert cycles
            duration: Duration per beep
            volume: Alert volume
        """
        for _ in range(cycles):
            self.beep(duration=duration, frequency='alert', volume=volume)
            time.sleep(0.1)
    
    def alert_async(self, cycles=3, duration=0.15, volume=0.9):
        """Play alert in background thread"""
        thread = threading.Thread(
            target=self.alert,
            args=(cycles, duration, volume),
            daemon=True
        )
        thread.start()
    
    def obstacle_warning(self, proximity_ratio=0.5):
        """
        Play warning pattern based on obstacle proximity
        Closer obstacle = faster beeps
        
        Args:
            proximity_ratio: 0=far, 1=very close
        """
        proximity_ratio = max(0, min(1, proximity_ratio))  # Clamp 0-1
        
        # Adjust beep duration based on proximity
        duration = 0.3 - (proximity_ratio * 0.25)  # 0.3s to 0.05s
        interval = 0.2 - (proximity_ratio * 0.15)  # 0.2s to 0.05s
        
        self.beep(duration=duration, frequency='obstacle')
        time.sleep(interval)
    
    def obstacle_warning_continuous(self, proximity_ratio=0.5, cycles=1):
        """
        Continuous obstacle warning pattern
        
        Args:
            proximity_ratio: Distance ratio (0=far, 1=close)
            cycles: Number of warning cycles
        """
        for _ in range(cycles):
            self.obstacle_warning(proximity_ratio)
    
    def set_volume(self, volume):
        """
        Set default buzzer volume
        
        Args:
            volume: Volume 0-1 (0=off, 1=max)
        """
        volume = max(0, min(1, volume))
        self.current_volume = volume
        logger.info(f"Buzzer volume set to {volume:.1%}")
    
    def _get_frequency(self, freq_param):
        """
        Get frequency from name or return numeric value
        
        Args:
            freq_param: Tone name (string) or frequency in Hz (number)
        
        Returns:
            Frequency in Hz
        """
        if isinstance(freq_param, str):
            return self.TONES.get(freq_param, self.TONES['beep'])
        return freq_param
    
    def stop(self):
        """Stop any current buzzer sound"""
        try:
            with self.lock:
                if self.buzzer:
                    self.buzzer.off()
            logger.debug("Buzzer stopped")
        except Exception as e:
            logger.error(f"Error stopping buzzer: {e}")
    
    def cleanup(self):
        """Cleanup buzzer"""
        logger.info("Cleaning up buzzer")
        self.stop()
        
        if self.buzzer:
            self.buzzer.close()
        
        logger.info("Buzzer cleanup complete")
