#!/usr/bin/env python3
"""
Audio Manager Module
Handles text-to-speech with priority queue and cooldown management
"""

import subprocess
import time
from threading import Thread, Lock
from queue import PriorityQueue, Empty
from utils import logger

class AudioManager:
    """Manages audio output with priority queue and cooldowns"""
    
    def __init__(self, cooldown_seconds=3):
        """
        Initialize audio manager
        
        Args:
            cooldown_seconds: Cooldown period per object type to avoid repetition
        """
        self.cooldown_seconds = cooldown_seconds
        
        # Priority queue for speech (lower number = higher priority)
        self.speech_queue = PriorityQueue()
        
        # Track last announcement time per object type
        self.last_announcement = {}
        
        # Lock for thread safety
        self.lock = Lock()
        
        # Background thread for processing queue
        self.running = True
        self.worker_thread = Thread(target=self._process_queue, daemon=True)
        self.worker_thread.start()
        
        logger.info("Audio manager initialized with espeak TTS")
    
    def speak(self, text, priority=5, block=False):
        """
        Speak text immediately (bypass queue for critical messages)
        
        Args:
            text: Text to speak
            priority: Priority level (lower = higher priority, default=5)
            block: Whether to wait for speech to complete
        """
        logger.info(f"Speaking (priority {priority}): {text}")
        self._tts_speak(text, block=block)
    
    def speak_with_priority(self, text, priority=5, obj_type=None):
        """
        Add speech to priority queue with optional cooldown
        
        Args:
            text: Text to speak
            priority: Priority level (1=highest, 5=normal, 10=lowest)
            obj_type: Object type for cooldown tracking
        """
        current_time = time.time()
        
        # Check cooldown if object type specified
        if obj_type:
            with self.lock:
                last_time = self.last_announcement.get(obj_type, 0)
                
                if current_time - last_time < self.cooldown_seconds:
                    logger.debug(f"Skipping '{text}' - cooldown active for {obj_type}")
                    return
                
                # Update last announcement time
                self.last_announcement[obj_type] = current_time
        
        # Add to queue
        self.speech_queue.put((priority, current_time, text))
        logger.debug(f"Queued (priority {priority}): {text}")
    
    def _process_queue(self):
        """Background thread to process speech queue"""
        while self.running:
            try:
                # Get next item from queue (blocks until available)
                priority, timestamp, text = self.speech_queue.get(timeout=0.5)
                
                # Speak the text
                self._tts_speak(text, block=True)
                
                # Mark task as done
                self.speech_queue.task_done()
                
            except Empty:
                # Queue timeout - this is normal, just continue
                continue
            except Exception as e:
                # Other errors - log them
                logger.error(f"Queue processing error: {e}", exc_info=True)
                continue
    
    def _tts_speak(self, text, block=False):
        """
        Execute text-to-speech using espeak
        
        Args:
            text: Text to speak
            block: Whether to wait for completion
        """
        try:
            # Use espeak for offline TTS (lightweight and reliable on Pi)
            cmd = ['espeak', '-s', '150', '-a', '200', text]
            
            if block:
                subprocess.run(cmd, check=True, capture_output=True)
            else:
                subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
        except FileNotFoundError:
            logger.error("espeak not found. Install with: sudo apt-get install espeak")
            # Fallback to print
            print(f"SPEECH: {text}")
        except Exception as e:
            logger.error(f"TTS error: {e}")
            print(f"SPEECH: {text}")
    
    def clear_queue(self):
        """Clear all pending speech from queue"""
        with self.lock:
            while not self.speech_queue.empty():
                try:
                    self.speech_queue.get_nowait()
                    self.speech_queue.task_done()
                except:
                    break
        
        logger.info("Speech queue cleared")
    
    def reset_cooldowns(self):
        """Reset all cooldown timers"""
        with self.lock:
            self.last_announcement.clear()
        
        logger.info("Cooldowns reset")
    
    def cleanup(self):
        """Stop background thread and cleanup"""
        logger.info("Cleaning up audio manager")
        self.running = False
        
        # Wait for worker thread to finish
        if self.worker_thread.is_alive():
            self.worker_thread.join(timeout=2)
        
        logger.info("Audio manager cleanup complete")


# Alternative implementation using pyttsx3 (if preferred)
class AudioManagerPyttsx3:
    """Alternative audio manager using pyttsx3 (heavier but more features)"""
    
    def __init__(self, cooldown_seconds=3):
        """Initialize with pyttsx3"""
        import pyttsx3
        
        self.cooldown_seconds = cooldown_seconds
        self.last_announcement = {}
        self.lock = Lock()
        
        # Initialize pyttsx3
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)  # Speed
        self.engine.setProperty('volume', 1.0)  # Volume
        
        logger.info("Audio manager initialized with pyttsx3")
    
    def speak(self, text, block=True):
        """Speak text using pyttsx3"""
        logger.info(f"Speaking: {text}")
        
        try:
            self.engine.say(text)
            if block:
                self.engine.runAndWait()
        except Exception as e:
            logger.error(f"TTS error: {e}")
            print(f"SPEECH: {text}")
    
    def speak_with_priority(self, text, priority=5, obj_type=None):
        """Speak with cooldown check"""
        current_time = time.time()
        
        if obj_type:
            with self.lock:
                last_time = self.last_announcement.get(obj_type, 0)
                
                if current_time - last_time < self.cooldown_seconds:
                    return
                
                self.last_announcement[obj_type] = current_time
        
        self.speak(text, block=False)
    
    def cleanup(self):
        """Cleanup pyttsx3"""
        try:
            self.engine.stop()
        except:
            pass
