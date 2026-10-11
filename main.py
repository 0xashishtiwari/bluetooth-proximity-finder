import asyncio
from proximity_finder.scanner import scan_once


async def main():
    print("------Bluetooth Proximity Finder------")
    print("Scanning for nearby Bluetooth devices...")

    devices = await scan_once(timeout=10.0)
    
    devices.sort(key=lambda d: d.rssi, reverse=True)
    
    print(f"Found {len(devices)} devices:")

    for device in devices:
        print(f"Address: {device.address}, Name: {device.name}, RSSI: {device.rssi} dBm")

if __name__ == "__main__":
    asyncio.run(main())