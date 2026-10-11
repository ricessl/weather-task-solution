import json
from collections import defaultdict
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


@dataclass
class WeatherData:
    city: str
    temperature_c: int
    country: str


def load_cities(filename: str = "cities.txt") -> list[str]:
    with open(filename, "r", encoding="utf-8") as file:
        cities = [line.strip() for line in file if line.strip()]
    return list(dict.fromkeys(cities))


def get_weather(city: str) -> WeatherData:
    url = f"https://wttr.in/{quote(city)}?format=j1"
    request = Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; WeatherTask/1.0)"},
    )

    with urlopen(request, timeout=20) as response:
        data = json.loads(response.read().decode("utf-8"))

    temperature = int(data["current_condition"][0]["temp_C"])
    country = data["nearest_area"][0]["country"][0]["value"]

    return WeatherData(
        city=city,
        temperature_c=temperature,
        country=country,
    )


def print_city_weather(weather_data: list[WeatherData]) -> None:
    print("Weather by city:")
    for weather in weather_data:
        print(f"{weather.city}, {weather.country} {weather.temperature_c:+d} °C")


def print_country_statistics(weather_data: list[WeatherData]) -> None:
    countries = defaultdict(list)

    for weather in weather_data:
        countries[weather.country].append(weather.temperature_c)

    print("\nStatistics by country:")
    for country in sorted(countries):
        temperatures = countries[country]
        average = sum(temperatures) / len(temperatures)
        print(
            f"{country} - {len(temperatures)} cities, "
            f"avg: {average:+.1f} °C, "
            f"min: {min(temperatures):+d} °C, "
            f"max: {max(temperatures):+d} °C"
        )


def main() -> None:
    try:
        cities = load_cities()
    except OSError as error:
        print(f"Could not read cities.txt: {error}")
        return

    if not cities:
        print("The cities.txt file is empty.")
        return

    weather_data = []
    failed_cities = []

    for city in cities:
        try:
            weather_data.append(get_weather(city))
            print(f"Received weather for {city}")
        except (HTTPError, URLError, TimeoutError, KeyError, IndexError,
                ValueError, json.JSONDecodeError) as error:
            failed_cities.append(city)
            print(f"Could not get weather for {city}: {error}")

    print()
    if weather_data:
        print_city_weather(weather_data)
        print_country_statistics(weather_data)
    else:
        print("Weather data could not be retrieved for any city.")

    if failed_cities:
        print("\nCities with errors: " + ", ".join(failed_cities))


if __name__ == "__main__":
    main()
