import pytest

from proximity_finder.models import DeviceObservation
from proximity_finder.tracker import DeviceTracker


@pytest.fixture
def clock(monkeypatch):
    current_time = {"value": 100.0}
    monkeypatch.setattr(
        "proximity_finder.tracker.time.monotonic",
        lambda: current_time["value"],
    )
    return current_time


def test_update_stores_device_observation(clock):
    tracker = DeviceTracker()

    observation = DeviceObservation(
        address="AA:BB:CC:DD:EE:FF",
        name="Test Device",
        rssi=-60,
    )
    tracker.update(observation)

    device = tracker.devices["AA:BB:CC:DD:EE:FF"]
    assert device["name"] == "Test Device"
    assert device["rssi"] == -60
    assert device["last_seen"] == 100.0


def test_devices_are_sorted_by_strongest_rssi(clock):
    tracker = DeviceTracker()

    tracker.update(DeviceObservation("device-1", "Far", -90))
    tracker.update(DeviceObservation("device-2", "Near", -45))
    tracker.update(DeviceObservation("device-3", "Middle", -65))

    devices = tracker.get_devices()

    assert [device[0] for device in devices] == [
        "device-2",
        "device-3",
        "device-1",
    ]


def test_stale_devices_are_removed(clock):
    tracker = DeviceTracker(timeout=10.0)

    tracker.update(DeviceObservation("device-1", "Old Device", -60))

    clock["value"] = 111.0
    devices = tracker.get_devices()

    assert devices == []
    assert "device-1" not in tracker.devices