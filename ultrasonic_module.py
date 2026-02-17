#!/usr/bin/env python3
"""
Ultrasonic Sensor Module (HC-SR04)
Continuous distance monitoring in background thread
Raspberry Pi 5 Compatible
"""

import time
import threading
from gpiozero import DistanceSensor
from utils import logger


class UltrasonicModule:
    """Handles HC-SR04 ultrasonic sensor distance measurements"""
    
    def __init__(self, trigger_pin=23, echo_pin=24, threshold_distance=50):
        """
        Initialize ultrasonic sensor
        
        Args:
            trigger_pin: GPIO pin for trigger (default 23)
            echo_pin: GPIO pin for echo (default 24)
            threshold_distance: Distance in cm to trigger alerts (default 50cm)
        """
        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
        self.threshold_distance = threshold_distance
        
        # Current measurements
        self.current_distance = None
        self.obstacle_detected = False
        self.lock = threading.Lock()
        
        # Background thread
        self.running = False
        self.thread = None
        
        # Callback for obstacle detection
        self.on_obstacle_alert = None
        self.on_obstacle_clear = None
        
        try:
            logger.info(f"Initializing HC-SR04 on Trigger={trigger_pin}, Echo={echo_pin}")
            self.sensor = DistanceSensor(echo=echo_pin, trigger=trigger_pin)
            logger.info("Ultrasonic sensor initialized")
            
            # Start background monitoring thread
            self.start_monitoring()
            
        except Exception as e:
            logger.error(f"Ultrasonic sensor initialization failed: {e}")
            self.sensor = None
            raise
    
    def start_monitoring(self):
        """Start background distance monitoring thread"""
        if self.running:
            logger.warning("Monitoring already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        logger.info("Ultrasonic monitoring thread started")
    
    def _monitor_loop(self):
        """Background thread loop for continuous distance monitoring"""
        previous_obstacle_state = False
        
        while self.running:
            try:
                # Get distance in cm
                distance_m = self.sensor.distance  # Returns distance in meters
                distance_cm = distance_m * 100
                
                with self.lock:
                    self.current_distance = distance_cm
                    
                    # Check if obstacle within threshold
                    is_obstacle = distance_cm < self.threshold_distance
                    self.obstacle_detected = is_obstacle
                
                # Detect state change
                if is_obstacle and not previous_obstacle_state:
                    # Obstacle entered threshold
                    logger.info(f"Obstacle detected at {distance_cm:.1f}cm")
                    if self.on_obstacle_alert:
                        self.on_obstacle_alert(distance_cm)
                
                elif not is_obstacle and previous_obstacle_state:
                    # Obstacle cleared
                    logger.info(f"Obstacle cleared - distance: {distance_cm:.1f}cm")
                    if self.on_obstacle_clear:
                        self.on_obstacle_clear()
                
                previous_obstacle_state = is_obstacle
                
                # Sleep before next measurement
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Ultrasonic monitoring error: {e}")
                time.sleep(0.5)
    
    def get_distance(self):
        """Get current distance in cm"""
        with self.lock:
            return self.current_distance
    
    def is_obstacle_detected(self):
        """Check if obstacle is within threshold"""
        with self.lock:
            return self.obstacle_detected
    
    def set_threshold(self, distance_cm):
        """Update obstacle detection threshold"""
        self.threshold_distance = distance_cm
        logger.info(f"Ultrasonic threshold updated to {distance_cm}cm")
    
    def cleanup(self):
        """Stop monitoring and cleanup"""
        logger.info("Cleaning up ultrasonic sensor")
        self.running = False
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)
        
        if self.sensor:
            self.sensor.close()
        
        logger.info("Ultrasonic sensor cleanup complete")
