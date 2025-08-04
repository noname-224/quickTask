from datetime import datetime
from pathlib import Path
from typing import TypedDict, List
import json

from weather.weather_api_service import Weather
from weather.weather_formatter import format_weather


class WeatherStorage:
    """Interface for any storage saving weather"""
    def save(self, weather: Weather) -> None:
        raise NotImplementedError


class PlainFileWeatherStorage(WeatherStorage):
    """Store weather in plain text file"""
    def __init__(self, file: Path):
        self.file = file

    def save(self, weather: Weather) -> None:
        now = datetime.now()
        formatted_weather = format_weather(weather)
        with open(self.file, "a") as file:
            file.write(f"{now}\n{formatted_weather}")


class HistoryRecord(TypedDict):
    date: str
    weather: str


class JSONFileWeatherStorage(WeatherStorage):
    """Store weather in JSON file"""
    def __init__(self, jsonfile: Path):
        self._jsonfile = jsonfile
        self._init_storage()

    def save(self, weather: Weather) -> None:
        history = self._read_history()
        history.append({
            "date": str(datetime.now()),
            "weather": format_weather(weather)
        })
        self._write(history)

    def _init_storage(self):
        if not self._jsonfile.exists():
            self._jsonfile.write_text("[]")

    def _read_history(self) -> List[HistoryRecord]:
        with open(self._jsonfile, "r") as file:
            return json.load(file)

    def _write(self, history: List[HistoryRecord]) -> None:
        with open(self._jsonfile, "w") as file:
            json.dump(history, file, ensure_ascii=False, indent=4)

def save_weather(weather: Weather, storage: WeatherStorage) -> None:
    storage.save(weather)