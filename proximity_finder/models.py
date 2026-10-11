from dataclasses import dataclass

@dataclass
class DeviceObservation:
    address: str
    name: str
    rssi: int
    
    