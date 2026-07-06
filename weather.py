import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")


def get_forecast(city="Tokyo"):
    """
    Forecast APIから予報を取得し、forecast.jsonへ保存
    """

    url = "https://api.openweathermap.org/data/2.5/forecast"

    params = {
        "q": city,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",
        "lang": "ja"
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    forecast = response.json()

    os.makedirs("output", exist_ok=True)

    with open("output/forecast.json", "w", encoding="utf-8") as f:
        json.dump(forecast, f, ensure_ascii=False, indent=4)

    return forecast


def load_forecast():
    """
    保存したforecast.jsonを読み込む
    """

    with open("output/forecast.json", "r", encoding="utf-8") as f:
        return json.load(f)


def get_today_forecast():
    """
    今日の予報だけ取得
    """

    forecast = load_forecast()

    today = datetime.now().strftime("%Y-%m-%d")

    today_forecast = []

    for item in forecast["list"]:

        if item["dt_txt"].startswith(today):

            today_forecast.append({
                "time": item["dt_txt"][11:16],
                "weather": item["weather"][0]["description"],
                "temp": item["main"]["temp"],
                "feels_like": item["main"]["feels_like"],
                "humidity": item["main"]["humidity"],
                "wind": item["wind"]["speed"]
            })

    return today_forecast


def build_weather_context(forecast_list):
    """
    今日の予報リストを、AIに渡しやすいテキスト形式に変換する
    """

    if not forecast_list:
        return "本日の予報データは取得できませんでした。"

    lines = []
    for item in forecast_list:
        lines.append(
            f"{item['time']} - 天気:{item['weather']} "
            f"気温:{item['temp']}℃ 体感:{item['feels_like']}℃ "
            f"湿度:{item['humidity']}% 風速:{item['wind']}m/s"
        )

    return "\n".join(lines)
