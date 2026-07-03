import os
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from weather import get_forecast, get_today_forecast

load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")

app = App(token=SLACK_BOT_TOKEN)

@app.event("app_mention")
def forecast_bot(event, say):

    # 最新予報取得
    get_forecast("Tokyo")

    # 今日の予報だけ取得
    forecast = get_today_forecast()

    message = "📅 今日の天気予報\n\n"

    for item in forecast:

        message += (
            f"🕒 {item['time']}\n"
            f"天気：{item['weather']}\n"
            f"気温：{item['temp']}℃\n"
            f"体感：{item['feels_like']}℃\n"
            f"湿度：{item['humidity']}%\n"
            f"風速：{item['wind']}m/s\n\n"
        )

    say(message)

if __name__ == "__main__":
    SocketModeHandler(app, SLACK_APP_TOKEN).start()