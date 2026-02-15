#!/usr/bin/env python3
"""
GSM Module
Handles SMS sending via AT commands using pyserial
"""

import serial
import time
from utils import logger

class GSMModule:
    """GSM module for sending SMS alerts"""
    
    def __init__(self, phone_number, port='/dev/serial0', baudrate=9600, timeout=5):
        """
        Initialize GSM module
        
        Args:
            phone_number: Emergency contact phone number (with country code)
            port: Serial port for GSM module
            baudrate: Baud rate for serial communication
            timeout: Serial timeout in seconds
        """
        self.phone_number = phone_number
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        
        logger.info(f"GSM module initialized for {phone_number}")
        logger.info(f"GSM port: {port} @ {baudrate} baud")
    
    def send_sms(self, message):
        """
        Send SMS using AT commands
        
        Args:
            message: Message text to send
        
        Returns:
            bool: True if SMS sent successfully, False otherwise
        """
        logger.info(f"Attempting to send SMS: {message}")
        
        gsm_conn = None
        
        try:
            # Open serial connection to GSM module
            gsm_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            
            logger.info("GSM serial connection opened")
            time.sleep(2)  # Wait for module to stabilize
            
            # Test AT command
            if not self._send_at_command(gsm_conn, "AT", "OK"):
                logger.error("GSM module not responding to AT")
                return False
            
            # Set SMS text mode
            if not self._send_at_command(gsm_conn, "AT+CMGF=1", "OK"):
                logger.error("Failed to set SMS text mode")
                return False
            
            # Set character set to GSM
            self._send_at_command(gsm_conn, "AT+CSCS=\"GSM\"", "OK")
            
            # Send SMS command with phone number
            cmd = f'AT+CMGS="{self.phone_number}"'
            gsm_conn.write((cmd + '\r').encode())
            time.sleep(2)
            
            # Check for '>' prompt
            response = gsm_conn.read(100).decode('ascii', errors='ignore')
            logger.debug(f"CMGS response: {response}")
            
            if '>' not in response:
                logger.error("Did not receive SMS prompt '>'")
                return False
            
            # Send message text followed by Ctrl+Z
            gsm_conn.write(message.encode())
            gsm_conn.write(b'\x1A')  # Ctrl+Z to send
            time.sleep(3)
            
            # Read response
            response = gsm_conn.read(200).decode('ascii', errors='ignore')
            logger.debug(f"SMS send response: {response}")
            
            # Check for success
            if 'OK' in response or '+CMGS:' in response:
                logger.info("SMS sent successfully")
                return True
            else:
                logger.error("SMS send failed - no OK response")
                return False
            
        except serial.SerialException as e:
            logger.error(f"GSM serial error: {e}")
            return False
        
        except Exception as e:
            logger.error(f"GSM error: {e}")
            return False
        
        finally:
            # Close connection
            if gsm_conn and gsm_conn.is_open:
                gsm_conn.close()
                logger.debug("GSM connection closed")
    
    def _send_at_command(self, conn, command, expected_response, timeout=2):
        """
        Send AT command and check for expected response
        
        Args:
            conn: Serial connection
            command: AT command string
            expected_response: Expected response string
            timeout: Timeout in seconds
        
        Returns:
            bool: True if expected response received
        """
        try:
            # Clear input buffer
            conn.reset_input_buffer()
            
            # Send command
            conn.write((command + '\r').encode())
            
            # Wait and read response
            time.sleep(timeout)
            response = conn.read(200).decode('ascii', errors='ignore')
            
            logger.debug(f"AT: {command} -> {response.strip()}")
            
            return expected_response in response
            
        except Exception as e:
            logger.error(f"AT command error: {e}")
            return False
    
    def check_signal(self):
        """
        Check GSM signal strength
        
        Returns:
            int: Signal strength (0-31) or -1 if unavailable
        """
        gsm_conn = None
        
        try:
            gsm_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=2
            )
            
            time.sleep(1)
            
            # Send signal quality command
            gsm_conn.write(b'AT+CSQ\r')
            time.sleep(1)
            
            response = gsm_conn.read(100).decode('ascii', errors='ignore')
            
            # Parse response: +CSQ: <rssi>,<ber>
            if '+CSQ:' in response:
                parts = response.split('+CSQ:')[1].split(',')
                rssi = int(parts[0].strip())
                logger.info(f"GSM signal strength: {rssi}/31")
                return rssi
            
            return -1
            
        except Exception as e:
            logger.error(f"Signal check error: {e}")
            return -1
        
        finally:
            if gsm_conn and gsm_conn.is_open:
                gsm_conn.close()
    
    def is_available(self):
        """
        Check if GSM module is available and responding
        
        Returns:
            bool: True if GSM module responds to AT
        """
        gsm_conn = None
        
        try:
            gsm_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=2
            )
            
            time.sleep(1)
            
            # Test AT command
            result = self._send_at_command(gsm_conn, "AT", "OK")
            return result
            
        except Exception as e:
            logger.error(f"GSM availability check failed: {e}")
            return False
        
        finally:
            if gsm_conn and gsm_conn.is_open:
                gsm_conn.close()


# Mock GSM for testing without hardware
class MockGSMModule:
    """Mock GSM module for testing"""
    
    def __init__(self, phone_number):
        self.phone_number = phone_number
        logger.info(f"Mock GSM initialized for {phone_number}")
    
    def send_sms(self, message):
        """Simulate SMS sending"""
        logger.info(f"MOCK SMS to {self.phone_number}: {message}")
        print(f"\n{'='*60}")
        print(f"MOCK SMS SENT")
        print(f"To: {self.phone_number}")
        print(f"Message: {message}")
        print(f"{'='*60}\n")
        return True
    
    def check_signal(self):
        """Return mock signal strength"""
        return 25
    
    def is_available(self):
        """Mock GSM is always available"""
        return True
