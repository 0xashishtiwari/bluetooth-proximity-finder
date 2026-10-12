from bleak import BleakScanner
import asyncio
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


async def scan_continuously(on_observation):
    def detection_callback(device , advertisement):
        name = advertisement.local_name or device.name or "Unknown"
        rssi = advertisement.rssi

      
        observation = DeviceObservation(address=device.address, name=name, rssi=rssi)
        on_observation(observation)

    async with BleakScanner(detection_callback=detection_callback):
        print("Starting continuous scan for Bluetooth devices...")
        await asyncio.Event().wait()  # Keep the scanner running indefinitely