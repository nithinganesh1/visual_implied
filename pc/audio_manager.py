#!/usr/bin/env python3
"""
PC Optimized Audio Manager
Thread-safe priority speech system
Designed for assistive navigation AI
"""

import time
from threading import Thread, Lock
from queue import PriorityQueue, Empty
import pyttsx3


class AudioManager:
    def __init__(self, cooldown_seconds=2):
        self.cooldown_seconds = cooldown_seconds

        # Priority queue (lower number = higher priority)
        self.speech_queue = PriorityQueue()

        # Track last announcement time per object type
        self.last_announcement = {}
        self.lock = Lock()

        # Initialize TTS engine
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 165)
        self.engine.setProperty("volume", 1.0)

        # Optional: choose first available voice
        voices = self.engine.getProperty("voices")
        if voices:
            self.engine.setProperty("voice", voices[0].id)

        # Thread control
        self.running = True
        self.worker_thread = Thread(target=self._process_queue, daemon=True)
        self.worker_thread.start()

    
    # -----------------------------------------------------
    # PUBLIC METHODS
    # -----------------------------------------------------

    def speak(self, text, priority=5, obj_type=None):
        """
        Add speech to queue with optional cooldown.
        Lower priority number = higher importance.
        """

        current_time = time.time()

        # Cooldown handling
        if obj_type:
            with self.lock:
                last_time = self.last_announcement.get(obj_type, 0)
                if current_time - last_time < self.cooldown_seconds:
                    return
                self.last_announcement[obj_type] = current_time

        self.speech_queue.put((priority, current_time, text))
        
    def speak_immediately(self, text):
        """
        Interrupt current speech and speak instantly.
        Used for emergency / critical alerts.
        """
        
        self.clear_queue()

        with self.lock:
            self.engine.stop()
            self.engine.say(text)
            self.engine.runAndWait()

    def clear_queue(self):
        """Remove all pending speech items."""
        with self.lock:
            while not self.speech_queue.empty():
                try:
                    self.speech_queue.get_nowait()
                    self.speech_queue.task_done()
                except:
                    break

    def reset_cooldowns(self):
        """Reset cooldown timers."""
        with self.lock:
            self.last_announcement.clear()

    # -----------------------------------------------------
    # INTERNAL WORKER THREAD
    # -----------------------------------------------------

    def _process_queue(self):
        while self.running:
            try:
                priority, timestamp, text = self.speech_queue.get(timeout=0.5)

                with self.lock:
                    self.engine.say(text)
                    self.engine.runAndWait()

                self.speech_queue.task_done()

            except Empty:
                continue
            except Exception as e:
                continue

    # -----------------------------------------------------
    # CLEANUP
    # -----------------------------------------------------

    def cleanup(self):
        self.running = False

        with self.lock:
            self.engine.stop()

        if self.worker_thread.is_alive():
            self.worker_thread.join(timeout=2)
