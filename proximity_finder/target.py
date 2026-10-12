
from proximity_finder.models import DeviceObservation


class TargetMatcher:
    def __init__(self, target: str):
        self.target = target.strip().casefold()

    def matches(self, observation: DeviceObservation) -> bool:
        target_address = observation.address.strip().casefold()
        target_name = observation.name.strip().casefold()

        return (
            target_address == self.target
            or target_name == self.target
        )
