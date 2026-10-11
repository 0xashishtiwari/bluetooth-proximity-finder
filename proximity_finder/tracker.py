import time

from proximity_finder.models import DeviceObservation

class DeviceTracker:
    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout
        self.devices = {}
        

    def update(self , observation: DeviceObservation):
        self.devices[observation.address] = {
            
            "name": observation.name,
            "rssi": observation.rssi,
            "last_seen": time.monotonic()
        }
    
    def remove_stale_devices(self):
        current_time = time.monotonic()
        
        stale_addresses = [
            address for address, device in self.devices.items()
            if current_time - device["last_seen"] > self.timeout    
        ]
        for address in stale_addresses:
            del self.devices[address]
    
    def get_devices(self):
        self.remove_stale_devices()
        
        return sorted(
            self.devices.items(),
            key=lambda item: item[1]["rssi"],
            reverse=True
        )