
import asyncio
import os
import time

from proximity_finder.audio import proximity_beeps
from proximity_finder.signal import RSSISmoother
from proximity_finder.scanner import scan_continuously
from proximity_finder.tracker import DeviceTracker
from proximity_finder.target import TargetMatcher
from proximity_finder.proximity import estimate_distance


SCAN_TIMEOUT = 10.0
TARGET_SEARCH_TIMEOUT = 30.0
TARGET_LOST_TIMEOUT = 10.0
REFRESH_INTERVAL = 1.0


def clear_screen():
    """Clear the terminal instead of accumulating old output."""
    os.system("cls" if os.name == "nt" else "clear")


async def wait_for_menu_key():
    """On Windows, press M to return to the main menu."""
    if os.name != "nt":
        # On other platforms, this task waits until cancelled.
        await asyncio.Future()
        return

    import msvcrt

    while True:
        if msvcrt.kbhit():
            key = msvcrt.getwch().lower()

            if key == "m":
                return

        await asyncio.sleep(0.1)


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
    menu_task = asyncio.create_task(wait_for_menu_key())

    try:
        while True:
            if menu_task.done():
                await menu_task
                return

            if scanner_task.done():
                scanner_task.result()
                raise RuntimeError("Bluetooth scanner stopped unexpectedly.")

            devices = tracker.get_devices()
            active_addresses = {address for address, _ in devices}

            # Remove smoothing state for devices no longer tracked.
            for address in list(smoothers):
                if address not in active_addresses:
                    del smoothers[address]

            clear_screen()
            print("====== Bluetooth Proximity Finder ======")
            print("Mode: SURVEY")
            print("Press M to return to the main menu.")
            print(f"\nNearby devices: {len(devices)}\n")

            for address, device in devices:
                smoother = smoothers.get(address)
                smoothed_rssi = (
                    smoother.value if smoother else device["rssi"]
                )

                print(f"Name: {device['name']}")
                print(f"Address: {address}")
                print(
                    f"  Raw RSSI: {device['rssi']} dBm | "
                    f"Smoothed RSSI: {smoothed_rssi:.1f} dBm"
                )
                print("-" * 45)

            await asyncio.sleep(REFRESH_INTERVAL)

    finally:
        for task in (scanner_task, menu_task):
            task.cancel()

        await asyncio.gather(
            scanner_task,
            menu_task,
            return_exceptions=True,
        )


async def run_hunt(target: str):
    matcher = TargetMatcher(target)
    tracker = DeviceTracker(timeout=TARGET_LOST_TIMEOUT)
    smoother = RSSISmoother(
        window_size=5,
        debounce_seconds=0.2,
    )

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

    def is_target_found():
        return (
            last_seen_at is not None
            and time.monotonic() - last_seen_at <= TARGET_LOST_TIMEOUT
        )

    def get_distance():
        if not is_target_found() or smoothed_rssi is None:
            return None

        return estimate_distance(
            rssi=smoothed_rssi,
            reference_rssi=-52.3,
            path_loss_exponent=3.67,
        )

    scanner_task = asyncio.create_task(
        scan_continuously(handle_observation)
    )
    audio_task = asyncio.create_task(
        proximity_beeps(get_distance, is_target_found)
    )
    menu_task = asyncio.create_task(wait_for_menu_key())

    try:
        while True:
            if menu_task.done():
                await menu_task
                return

            for task in (scanner_task, audio_task):
                if task.done():
                    task.result()
                    raise RuntimeError(
                        "A background task stopped unexpectedly."
                    )

            now = time.monotonic()
            devices = tracker.get_devices()

            clear_screen()
            print("====== Bluetooth Proximity Finder ======")
            print("Mode: HUNT")
            print(f"Target: {target}")
            print("Audio: Sonar enabled")
            print("Press M to return to the main menu.")

            if last_seen_at is None:
                elapsed = now - started_at
                remaining = TARGET_SEARCH_TIMEOUT - elapsed

                if remaining <= 0:
                    print("\nStatus: NOT FOUND")
                    print("Target was not detected within 30 seconds.")
                    print("\nReturning to the main menu...")
                    await asyncio.sleep(2)
                    return

                print("\nStatus: SEARCHING")
                print(f"Time remaining: {remaining:.1f}s")

            elif not is_target_found():
                print("\nStatus: LOST")
                print("Searching for target again...")
                print("Audio paused.")

            else:
                print("\nStatus: FOUND")
                print(f"Name: {target_name}")
                print(f"Address: {target_address}")

                target_device = next(
                    (
                        device
                        for address, device in devices
                        if address == target_address
                    ),
                    None,
                )

                if target_device:
                    print(f"Raw RSSI: {target_device['rssi']} dBm")

                print(f"Smoothed RSSI: {smoothed_rssi:.1f} dBm")

                distance = get_distance()
                if distance is not None:
                    print(f"Estimated distance: {distance:.2f} m")

            await asyncio.sleep(REFRESH_INTERVAL)

    finally:
        for task in (scanner_task, audio_task, menu_task):
            task.cancel()

        await asyncio.gather(
            scanner_task,
            audio_task,
            menu_task,
            return_exceptions=True,
        )


async def main():
    while True:
        clear_screen()
        print("====== Bluetooth Proximity Finder ======")
        print("1. Survey nearby devices")
        print("2. Hunt for a specific device")
        print("0. Exit")

        choice = input("\nSelect mode (0/1/2): ").strip()

        if choice == "0":
            print("Exiting Bluetooth Proximity Finder.")
            return

        try:
            if choice == "1":
                await run_survey()

            elif choice == "2":
                clear_screen()
                target = input(
                    "Enter target device name or Bluetooth address: "
                ).strip()

                if not target:
                    print("Target cannot be empty.")
                    await asyncio.sleep(1.5)
                    continue

                await run_hunt(target)

            else:
                print("Invalid choice. Please select 0, 1, or 2.")
                await asyncio.sleep(1.5)

        except Exception as error:
            clear_screen()
            print("An error occurred:")
            print(f"{type(error).__name__}: {error}")
            print("\nReturning to the main menu...")
            await asyncio.sleep(2)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBluetooth Proximity Finder stopped.")
