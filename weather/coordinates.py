from geopy.geocoders import Nominatim
from typing import NamedTuple

from weather.exceptions import CantGetCoordinates


class Coordinates(NamedTuple):
    latitude: float
    longitude: float


def get_coordinates(place: str) -> Coordinates:
    """
    Returns GPS coordinates as NamedTuple.

    :return:
    """

    geolocator = Nominatim(user_agent="test")
    if location := geolocator.geocode(place):
        return Coordinates(
            latitude=location.latitude,
            longitude=location.longitude
        )
    else:
        raise CantGetCoordinates