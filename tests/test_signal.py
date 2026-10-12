
import pytest

from proximity_finder.signal import RSSISmoother


def test_calculates_average():
    smoother = RSSISmoother(window_size=5)

    smoother.update(-45, timestamp=1.0)
    smoother.update(-55, timestamp=1.3)
    smoother.update(-50, timestamp=1.6)

    assert smoother.value == pytest.approx(-50.0)


def test_keeps_only_latest_readings():
    smoother = RSSISmoother(window_size=3)

    smoother.update(-40, timestamp=1.0)
    smoother.update(-50, timestamp=1.3)
    smoother.update(-60, timestamp=1.6)
    smoother.update(-70, timestamp=1.9)

    assert smoother.value == pytest.approx(-60.0)


def test_ignores_duplicate_within_debounce_window():
    smoother = RSSISmoother(debounce_seconds=0.2)

    smoother.update(-50, timestamp=1.0)
    smoother.update(-50, timestamp=1.1)

    assert smoother.value == pytest.approx(-50.0)
    assert len(smoother.readings) == 1


def test_accepts_same_rssi_after_debounce_window():
    smoother = RSSISmoother(debounce_seconds=0.2)

    smoother.update(-50, timestamp=1.0)
    smoother.update(-50, timestamp=1.3)

    assert len(smoother.readings) == 2


def test_rejects_invalid_window_size():
    with pytest.raises(ValueError):
        RSSISmoother(window_size=0)
