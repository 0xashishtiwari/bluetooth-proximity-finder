import asyncio
from proximity_finder.scanner import scan_continuously
from proximity_finder.tracker import DeviceTracker


async def main():
    tracker = DeviceTracker(timeout=10.0)
    
    def handle_observation(observation):
        tracker.update(observation)
    
    scanner_task = asyncio.create_task(scan_continuously(handle_observation))
    
    try:
        print("---------Bluetooth Proximity Finder---------")
        print("Surveying for nearby Bluetooth devices...")
        
        while True:
            devices = tracker.get_devices()
            
            print("\033[2J\033[H", end="")
            print("------ Bluetooth Proximity Finder ------")
            print(f"Nearby devices: {len(devices)}\n")
            
            for address, device in devices:
                print(f"Name: {device['name']}, Address: {address}, RSSI: {device['rssi']}")

            await asyncio.sleep(1)
        
    finally:
        scanner_task.cancel()
        try:
            await scanner_task
        except asyncio.CancelledError:
            pass

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting Bluetooth Proximity Finder.")