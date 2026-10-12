
import asyncio
import time
from proximity_finder.signal import RSSISmoother
from proximity_finder.scanner import scan_continuously
from proximity_finder.tracker import DeviceTracker
from proximity_finder.target import TargetMatcher


SCAN_TIMEOUT = 10.0
TARGET_SEARCH_TIMEOUT = 30.0
TARGET_LOST_TIMEOUT = 10.0
REFRESH_INTERVAL = 1.0


async def run_survey():
    tracker = DeviceTracker(timeout=SCAN_TIMEOUT)
    smoothers = {}

    def handle_observation(observation):
        tracker.update(observation)

        smoother = smoothers.get(observation.address)

        if smoother is None:
            smoother = RSSISmoother(
                window_size=5,
                debounce_seconds=0.2,
            )
            smoothers[observation.address] = smoother

        smoother.update(observation.rssi)

    scanner_task = asyncio.create_task(
        scan_continuously(handle_observation)
    )

    try:
        print("Survey Mode started. Press Ctrl+C to stop.")

        while True:
            devices = tracker.get_devices()

            print("\033[2J\033[H", end="")
            print("------ Bluetooth Proximity Finder ------")
            print("Mode: SURVEY")
            print(f"Nearby devices: {len(devices)}\n")

            for address, device in devices:
                smoother = smoothers.get(address)
                smoothed_rssi = (
                    smoother.value if smoother else device["rssi"]
                )

                print(
                    f"Name: {device['name']}, "
                    f"Address: {address}"
                )
                print(
                    f"  Raw RSSI: {device['rssi']} dBm | "
                    f"Smoothed RSSI: {smoothed_rssi:.1f} dBm"
                )

            await asyncio.sleep(REFRESH_INTERVAL)

    finally:
        scanner_task.cancel()

        try:
            await scanner_task
        except asyncio.CancelledError:
            pass



async def run_hunt(target: str):
    matcher = TargetMatcher(target)
    tracker = DeviceTracker(timeout=TARGET_LOST_TIMEOUT)
    smoother = RSSISmoother(window_size=5, debounce_seconds=0.2)

    started_at = time.monotonic()
    last_seen_at = None
    smoothed_rssi = None
    target_address = None
    target_name = None

    def handle_observation(observation):
        nonlocal last_seen_at
        nonlocal smoothed_rssi
        nonlocal target_address
        nonlocal target_name

        if matcher.matches(observation):
            tracker.update(observation)

            smoothed_rssi = smoother.update(observation.rssi)
            last_seen_at = time.monotonic()
            target_address = observation.address
            target_name = observation.name

    scanner_task = asyncio.create_task(
        scan_continuously(handle_observation)
    )

    try:
        while True:
            now = time.monotonic()
            devices = tracker.get_devices()

            print("\033[2J\033[H", end="")
            print("------ Bluetooth Proximity Finder ------")
            print("Mode: HUNT")
            print(f"Target: {target}")

            if last_seen_at is None:
                elapsed = now - started_at

                if elapsed >= TARGET_SEARCH_TIMEOUT:
                    print("\nStatus: NOT FOUND")
                    print(
                        f"Target was not detected within "
                        f"{TARGET_SEARCH_TIMEOUT:.0f} seconds."
                    )
                    raise SystemExit(1)

                print("\nStatus: SEARCHING")
                print(
                    f"Time remaining: "
                    f"{TARGET_SEARCH_TIMEOUT - elapsed:.1f} seconds"
                )

            elif now - last_seen_at > TARGET_LOST_TIMEOUT:
                print("\nStatus: LOST")
                print("Target signal has not been detected recently.")
                print("Continuing to search...")

            else:
                print("\nStatus: FOUND")
                print(f"Name: {target_name}")
                print(f"Address: {target_address}")

                if devices:
                    print(f"Raw RSSI: {devices[0][1]['rssi']} dBm")

                if smoothed_rssi is not None:
                    print(f"Smoothed RSSI: {smoothed_rssi:.1f} dBm")

            await asyncio.sleep(REFRESH_INTERVAL)

    finally:
        scanner_task.cancel()

        try:
            await scanner_task
        except asyncio.CancelledError:
            pass



async def main():
    print("------ Bluetooth Proximity Finder ------")
    print("1. Survey nearby devices")
    print("2. Hunt for a specific device")

    choice = input("Select mode (1/2): ").strip()

    if choice == "1":
        await run_survey()

    elif choice == "2":
        target = input(
            "Enter target device name or Bluetooth address: "
        ).strip()

        if not target:
            print("Error: Target cannot be empty.")
            raise SystemExit(1)

        await run_hunt(target)

    else:
        print("Invalid choice. Please select 1 or 2.")
        raise SystemExit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting Bluetooth Proximity Finder.")
