"""
Fixed GPS Module
Returns a constant location (no serial, no threading)
"""

import time
from utils import logger


class GPSModule:
    """Fixed GPS module (no hardware required)"""

    def __init__(self):
        # Fixed coordinates
        self.latitude = 11.258753
        self.longitude = 75.780411
        self.last_update = time.time()

        logger.info("Fixed GPS module initialized")

    def get_location(self):
        """Return fixed location"""
        return (self.latitude, self.longitude)

    def get_location_string(self):
        """Return formatted location string"""
        return f"{self.latitude},{self.longitude}"

    def is_available(self):
        """Always available"""
        return True

    def cleanup(self):
        """No cleanup required"""
        pass
