
from proximity_finder.models import DeviceObservation
from proximity_finder.target import TargetMatcher


def test_matches_device_by_address():
    matcher = TargetMatcher("AA:BB:CC:DD")
    observation = DeviceObservation(
        address="aa:bb:cc:dd",
        name="Unknown",
        rssi=-45,
    )

    assert matcher.matches(observation)


def test_matches_device_by_name():
    matcher = TargetMatcher("My Phone")
    observation = DeviceObservation(
        address="AA:BB:CC:DD",
        name="my phone",
        rssi=-45,
    )

    assert matcher.matches(observation)


def test_does_not_match_other_device():
    matcher = TargetMatcher("My Phone")
    observation = DeviceObservation(
        address="AA:BB:CC:DD",
        name="Jio STB",
        rssi=-60,
    )

    assert not matcher.matches(observation)
