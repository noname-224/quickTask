OPENWEATHER_API_KEY = "046ac7a13d814ede5d397352c002b831"

OPENWEATHER_URL_TEMPLATE = (
    "https://api.openweathermap.org/data/2.5/weather?"
    "lat={latitude}&lon={longitude}&"
    "appid=" + OPENWEATHER_API_KEY + "&lang=ru"
    "&units=metric"
)