
import asyncio
import math
import sys


def beep_interval(distance: float) -> float:
    """Closer target means faster sonar pings."""
    if not math.isfinite(distance) or distance < 0:
        raise ValueError("distance must be a finite, non-negative number")

    return max(0.15, min(1.5, distance * 0.4))


def play_sonar_ping():
    """Play a short sonar-like frequency sweep on Windows."""
    if sys.platform != "win32":
        print("\a", end="", flush=True)
        return

    import winsound

    # Short descending tones create a sonar-like ping.
    winsound.Beep(1400, 35)
    winsound.Beep(1000, 65)


async def proximity_beeps(get_distance, is_target_found):
    """Play sonar pings while the target is detected."""
    try:
        while True:
            if not is_target_found():
                await asyncio.sleep(0.2)
                continue

            distance = get_distance()
            if distance is None:
                await asyncio.sleep(0.2)
                continue

            interval = beep_interval(distance)
            play_sonar_ping()
            await asyncio.sleep(interval)

    except asyncio.CancelledError:
        raise
