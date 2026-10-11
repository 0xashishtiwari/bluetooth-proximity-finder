from bleak import BleakScanner

from proximity_finder.models import DeviceObservation

async def scan_once(timeout : float = 10.0) -> list[DeviceObservation]:
    
    advertisements = await BleakScanner.discover(timeout=timeout, return_adv=True)

    observations = []
    
    for address , (device, advertisement) in advertisements.items():
        name = advertisement.local_name or device.name or "Unknown"
        rssi = advertisement.rssi

        observation = DeviceObservation(address=address, name=name, rssi=rssi)
        observations.append(observation)

    return observations