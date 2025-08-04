from pathlib import Path


from weather.weather import ApiServiceError, CantGetCoordinates
from weather.weather import JSONFileWeatherStorage, save_weather
from weather.weather import get_coordinates
from weather.weather import get_weather
from weather.weather import format_weather


def main(city):
    try:
        coordinates = get_coordinates(city)
    except CantGetCoordinates:
        print("Не удалось получить координаты")
        exit(1)
    try:
        weather = get_weather(coordinates)
    except ApiServiceError:
        print(f"Не удалось получить погоду по координатам {coordinates}")
        exit(1)

    save_weather(
        weather,
        JSONFileWeatherStorage(Path.cwd() / "history.json")
    )

    return format_weather(weather)


if __name__ == '__main__':
    name_of_the_city = input()
    main(name_of_the_city)