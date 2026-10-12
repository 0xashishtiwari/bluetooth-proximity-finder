
import pytest

from proximity_finder.audio import beep_interval


def test_closer_target_has_faster_beeps():
    assert beep_interval(0.5) < beep_interval(2.0)


def test_beep_interval_is_capped():
    assert beep_interval(100) == 1.5


def test_invalid_distance_is_rejected():
    with pytest.raises(ValueError):
        beep_interval(-1)
