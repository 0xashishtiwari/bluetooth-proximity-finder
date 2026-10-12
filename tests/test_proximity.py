
import pytest

from proximity_finder.proximity import estimate_distance


def test_reference_distance_is_one_meter():
    assert estimate_distance(-50, reference_rssi=-50) == pytest.approx(1.0)


def test_weaker_signal_estimates_greater_distance():
    distance = estimate_distance(-60, reference_rssi=-50)

    assert distance == pytest.approx(3.16227766)


def test_stronger_signal_estimates_shorter_distance():
    distance = estimate_distance(-40, reference_rssi=-50)

    assert distance == pytest.approx(0.316227766)


def test_rejects_invalid_path_loss_exponent():
    with pytest.raises(ValueError):
        estimate_distance(-60, path_loss_exponent=0)


def test_rejects_non_finite_rssi():
    with pytest.raises(ValueError):
        estimate_distance(float("nan"))


def test_calibrated_reference_distance_is_one_meter():
    assert estimate_distance(
        -45,
        reference_rssi=-45,
        path_loss_exponent=2.0,
    ) == pytest.approx(1.0)