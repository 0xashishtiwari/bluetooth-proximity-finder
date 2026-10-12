import time
from collections import deque

class RSSISmoother:
    def __init__(self , window_size:int = 5 , debounce_seconds: float = 0.2):
        if window_size < 1:
            raise ValueError("window_size must be at least 1")
        if debounce_seconds < 0:
            raise ValueError("debounce_seconds must be non-negative")
        
        self.readings = deque(maxlen=window_size)
        self.debounce_seconds = debounce_seconds
        self.last_rssi = None
        self.last_timestamp = None
    
    
    def update(self, rssi: int, timestamp: float | None = None) -> float:
        if timestamp is None:
            timestamp = time.monotonic()

        is_duplicate = (
            self.last_rssi == rssi
            and self.last_timestamp is not None
            and timestamp >= self.last_timestamp
            and timestamp - self.last_timestamp < self.debounce_seconds
        )

        if is_duplicate:
            return self.value

        self.readings.append(rssi)
        self.last_rssi = rssi
        self.last_timestamp = timestamp

        return self.value

    
    @property
    def value(self) -> float | None:
        if not self.readings:
           raise ValueError("No RSSI readings available to compute average.")
        return sum(self.readings) / len(self.readings)