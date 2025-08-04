from weather.weather_api_service import Weather


def format_weather(weather: Weather) -> str:
    """Format weather data in string"""
    return (f"{weather.city}, температура {weather.temperature}°C, "
            f"{weather.weather_type.value}\n"
            f"Восход: {weather.sunrise.strftime('%H:%M')}\n"
            f"Закат: {weather.sunset.strftime('%H:%M')}\n")


if __name__ == '__main__':
    from datetime import datetime
    from weather_api_service import WeatherType
    print(format_weather(Weather(
        temperature=25,
        weather_type=WeatherType.CLEAR,
        sunrise=datetime.fromisoformat("2025-08-03 04:21:32"),
        sunset=datetime.fromisoformat("2025-08-03 20:58:11"),
        city="Лоев"
    )))