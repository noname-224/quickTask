from .exceptions import ApiServiceError, CantGetCoordinates
from .coordinates import get_coordinates
from .weather_api_service import get_weather
from .weather_formatter import format_weather


def get_weather_text(city):
    try:
        coordinates = get_coordinates(city)
    except CantGetCoordinates:
        return "Не удалось получить координаты"

    try:
        weather = get_weather(coordinates)
    except ApiServiceError:
        return f"Не удалось получить погоду по координатам {coordinates}"

    return format_weather(weather)




if __name__ == '__main__':
    name_of_the_city = input()
    get_weather_text(name_of_the_city)