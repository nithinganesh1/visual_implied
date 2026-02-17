#!/usr/bin/env python3
"""
Button Handler Module using gpiozero
Supports single/double/triple press detection and emergency button
Raspberry Pi 5 Compatible
"""

import time
from threading import Timer
from gpiozero import Button
from utils import logger

class ButtonHandler:
    """Manages button inputs with press counting logic"""
    
    def __init__(self, on_single_press=None, on_double_press=None, 
                 on_triple_press=None, on_emergency_button=None, on_ocr_button=None,
                 on_ocr_single_press=None, on_ocr_double_press=None,
                 primary_button_pin=17, emergency_button_pin=None, ocr_button_pin=27,
                 double_press_window=0.5, triple_press_window=0.8):
        """
        Initialize button handler
        
        Args:
            on_single_press: Callback for primary button single press
            on_double_press: Callback for primary button double press
            on_triple_press: Callback for primary button triple press
            on_emergency_button: Callback for emergency button
            on_ocr_button: Callback for OCR button (legacy)
            on_ocr_single_press: Callback for OCR button single press (face recognition)
            on_ocr_double_press: Callback for OCR button double press (OCR)
            primary_button_pin: GPIO pin for primary button
            emergency_button_pin: GPIO pin for emergency button (optional)
            ocr_button_pin: GPIO pin for OCR button (default=27)
            double_press_window: Time window for double press detection (seconds)
            triple_press_window: Time window for triple press detection (seconds)
        """
        self.on_single_press = on_single_press
        self.on_double_press = on_double_press
        self.on_triple_press = on_triple_press
        self.on_emergency_button = on_emergency_button
        self.on_ocr_button = on_ocr_button
        self.on_ocr_single_press = on_ocr_single_press or on_single_press  # Fallback to on_single_press
        self.on_ocr_double_press = on_ocr_double_press or on_ocr_button  # Fallback to on_ocr_button
        
        self.double_press_window = double_press_window
        self.triple_press_window = triple_press_window
        
        # Press counting state
        self.press_count = 0
        self.press_timer = None
        self.last_press_time = 0
        
        # Initialize primary button with gpiozero
        logger.info(f"Initializing primary button on GPIO {primary_button_pin}")
        self.primary_button = Button(
            primary_button_pin,
            pull_up=True,
            bounce_time=0.05,
            hold_time=2.0
        )

        
        # Attach event handler
        self.primary_button.when_pressed = self._handle_button_press
        self.primary_button.when_held = self._handle_hold

        
        # Initialize emergency button if specified
        self.emergency_button = None
        if emergency_button_pin is not None:
            logger.info(f"Initializing emergency button on GPIO {emergency_button_pin}")
            self.emergency_button = Button(
                emergency_button_pin,
                pull_up=True,
                bounce_time=0.05
            )
            self.emergency_button.when_pressed = self._handle_emergency_press
        
        # Initialize OCR button (GPIO 27) with press counting
        # Single press = Face recognition
        # Double press = OCR text reading
        self.ocr_button = None
        self.ocr_press_count = 0
        self.ocr_press_timer = None
        self.ocr_press_window = 0.5
        
        if ocr_button_pin is not None:
            logger.info(f"Initializing GPIO {ocr_button_pin} (Single=Face Recognition, Double=OCR)")
            self.ocr_button = Button(
                ocr_button_pin,
                pull_up=True,
                bounce_time=0.05
            )
            self.ocr_button.when_pressed = self._handle_ocr_button_press
        
        logger.info("Button handler initialized")
    
    def _handle_button_press(self):
        """Handle primary button press with counting logic"""
        current_time = time.time()
        
        # Increment press count
        self.press_count += 1
        
        logger.debug(f"Button press {self.press_count} detected at {current_time:.2f}")
        
        # Cancel any existing timer
        if self.press_timer:
            self.press_timer.cancel()
        
        # Determine timeout based on current press count
        if self.press_count == 1:
            # Wait for potential second press
            timeout = self.double_press_window
        elif self.press_count == 2:
            # Wait for potential third press
            timeout = self.triple_press_window - self.double_press_window
        else:
            # Three or more presses - execute immediately
            timeout = 0.05
        
        # Set timer to execute action after timeout
        self.press_timer = Timer(timeout, self._execute_action)
        self.press_timer.start()
        
        self.last_press_time = current_time
    def _handle_hold(self):
        logger.info("Button held - EMERGENCY triggered")

        if self.press_timer:
            self.press_timer.cancel()

        self.press_count = 0

        if self.on_emergency_button:
            self.on_emergency_button()

    
    def _execute_action(self):
        """Execute appropriate action based on press count"""
        count = self.press_count
        
        logger.info(f"Executing action for {count} press(es)")
        
        try:
            if count == 1:
                # Single press
                if self.on_single_press:
                    self.on_single_press()
            elif count == 2:
                # Double press
                if self.on_double_press:
                    self.on_double_press()
            elif count >= 3:
                # Triple press (or more) - emergency
                if self.on_triple_press:
                    self.on_triple_press()
        except Exception as e:
            logger.error(f"Error executing button action: {e}")
        finally:
            # Reset press count
            self.press_count = 0
    
    def _handle_emergency_press(self):
        """Handle dedicated emergency button press"""
        logger.info("Emergency button pressed")
        
        try:
            if self.on_emergency_button:
                self.on_emergency_button()
        except Exception as e:
            logger.error(f"Error executing emergency action: {e}")
    
    def _handle_ocr_button_press(self):
        """Handle GPIO 27 press with counting logic"""
        # Increment press count
        self.ocr_press_count += 1
        
        logger.debug(f"GPIO 27 press {self.ocr_press_count} detected")
        
        # Cancel any existing timer
        if self.ocr_press_timer:
            self.ocr_press_timer.cancel()
        
        # Wait for potential second press
        self.ocr_press_timer = Timer(self.ocr_press_window, self._execute_ocr_action)
        self.ocr_press_timer.start()
    
    def _execute_ocr_action(self):
        """Execute action based on GPIO 27 press count"""
        count = self.ocr_press_count
        
        logger.info(f"GPIO 27 executing action for {count} press(es)")
        
        try:
            if count == 1:
                # Single press = Face Recognition
                if self.on_ocr_single_press:
                    logger.info("Face Recognition triggered")
                    self.on_ocr_single_press()
            elif count >= 2:
                # Double press or more = OCR
                if self.on_ocr_double_press:
                    logger.info("OCR triggered")
                    self.on_ocr_double_press()
        except Exception as e:
            logger.error(f"Error executing GPIO 27 action: {e}")
        finally:
            # Reset press count
            self.ocr_press_count = 0
    
    def cleanup(self):
        """Cleanup GPIO resources"""
        logger.info("Cleaning up button handler")
        
        # Cancel any pending timers
        if self.press_timer:
            self.press_timer.cancel()
        
        # Close buttons (gpiozero handles cleanup automatically)
        if self.primary_button:
            self.primary_button.close()
        
        if self.emergency_button:
            self.emergency_button.close()
        
        if self.ocr_button:
            self.ocr_button.close()
        
        logger.info("Button handler cleanup complete")


# Alternative implementation for two-button system
class TwoButtonHandler:
    """
    Simplified handler for two-button configuration:
    - Button 1: Scan/Confirm
    - Button 2: Emergency
    """
    
    def __init__(self, on_scan=None, on_confirm=None, on_emergency=None,
                 scan_button_pin=17, emergency_button_pin=27,
                 confirm_timeout=10.0):
        """
        Initialize two-button handler
        
        Args:
            on_scan: Callback for scan button press
            on_confirm: Callback for confirm (second press within timeout)
            on_emergency: Callback for emergency button
            scan_button_pin: GPIO pin for scan/confirm button
            emergency_button_pin: GPIO pin for emergency button
            confirm_timeout: Time window for confirmation (seconds)
        """
        self.on_scan = on_scan
        self.on_confirm = on_confirm
        self.on_emergency = on_emergency
        self.confirm_timeout = confirm_timeout
        
        # Confirmation state
        self.waiting_for_confirm = False
        self.confirm_timer = None
        
        # Initialize buttons
        logger.info(f"Initializing scan button on GPIO {scan_button_pin}")
        self.scan_button = Button(scan_button_pin, pull_up=True, bounce_time=0.05)
        self.scan_button.when_pressed = self._handle_scan_press
        
        logger.info(f"Initializing emergency button on GPIO {emergency_button_pin}")
        self.emergency_button = Button(emergency_button_pin, pull_up=True, bounce_time=0.05)
        self.emergency_button.when_pressed = self._handle_emergency_press
        
        logger.info("Two-button handler initialized")
    
    def _handle_scan_press(self):
        """Handle scan/confirm button press"""
        if self.waiting_for_confirm:
            # Second press - confirmation
            logger.info("Confirmation detected")
            self._cancel_confirm_timer()
            self.waiting_for_confirm = False
            
            if self.on_confirm:
                self.on_confirm()
        else:
            # First press - scan
            logger.info("Scan button pressed")
            
            if self.on_scan:
                # Execute scan callback (may set waiting_for_confirm)
                self.on_scan()
    
    def _handle_emergency_press(self):
        """Handle emergency button press"""
        logger.info("Emergency button pressed")
        
        if self.on_emergency:
            self.on_emergency()
    
    def set_waiting_for_confirm(self, waiting=True):
        """
        Enable confirmation mode with timeout
        Called by main system after zebra detection
        """
        self.waiting_for_confirm = waiting
        
        if waiting:
            # Start timeout timer
            self.confirm_timer = Timer(self.confirm_timeout, self._confirm_timeout)
            self.confirm_timer.start()
            logger.info(f"Waiting for confirmation ({self.confirm_timeout}s timeout)")
        else:
            self._cancel_confirm_timer()
    
    def _confirm_timeout(self):
        """Handle confirmation timeout"""
        if self.waiting_for_confirm:
            logger.info("Confirmation timeout")
            self.waiting_for_confirm = False
    
    def _cancel_confirm_timer(self):
        """Cancel confirmation timer"""
        if self.confirm_timer:
            self.confirm_timer.cancel()
            self.confirm_timer = None
    
    def cleanup(self):
        """Cleanup GPIO resources"""
        logger.info("Cleaning up two-button handler")
        
        self._cancel_confirm_timer()
        
        if self.scan_button:
            self.scan_button.close()
        
        if self.emergency_button:
            self.emergency_button.close()
        
        logger.info("Two-button handler cleanup complete")
