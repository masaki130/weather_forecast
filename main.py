import os
import re
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from openai import OpenAI
from weather import get_forecast, get_today_forecast, build_weather_context

load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

CITY = "Tokyo"

app = App(token=SLACK_BOT_TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)


def extract_question(text: str, bot_user_id: str) -> str:
    """
    メンション部分 <@BOTID> を取り除き、純粋な質問文だけを取り出す。
    質問が空の場合は「今日の天気を教えて」をデフォルトにする。
    """
    cleaned = re.sub(f"<@{bot_user_id}>", "", text).strip()
    return cleaned if cleaned else "今日の天気を教えて"


def ask_ai(question: str, weather_context: str) -> str:
    """
    今日の気象情報を根拠として、gpt-4o-miniに質問への回答を生成させる。
    """

    system_prompt = (
        "あなたは親切な天気予報アシスタントです。\n"
        "以下は本日の東京の時間帯別気象情報です。この情報のみを根拠にユーザーの質問に答えてください。\n"
        "\n"
        "回答時のルール:\n"
        "- 雨や雪が降る場合は、何時頃から降り始めるかを具体的に伝え、傘が必要かどうかをはっきり伝える\n"
        "- 気温や体感温度をもとに、どんな服装(上着の要否や枚数など)が良いか具体的にアドバイスする\n"
        "- 湿度や風速も参考にしつつ、必要であれば熱中症・乾燥・強風などの注意点にも触れる\n"
        "- 与えられた気象情報に無い内容は推測せず、その旨を正直に伝える\n"
        "- 回答は簡潔に、絵文字を交えて親しみやすく\n"
        "\n"
        f"【本日の気象情報】\n{weather_context}"
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
        temperature=0.4,
    )

    return response.choices[0].message.content


@app.event("app_mention")
def forecast_bot(event, say, context):
    try:
        bot_user_id = context["bot_user_id"]
        question = extract_question(event.get("text", ""), bot_user_id)

        # 最新予報取得(forecast.jsonを更新)
        get_forecast(CITY)

        # 今日の予報だけ取得し、AI用のテキストに変換
        forecast = get_today_forecast()
        weather_context = build_weather_context(forecast)

        # 質問+気象情報をAIに渡して回答生成
        answer = ask_ai(question, weather_context)

        say(f"🤖 {answer}")

    except Exception as e:
        say(f"⚠️ エラーが発生しました: {e}")


if __name__ == "__main__":
    SocketModeHandler(app, SLACK_APP_TOKEN).start()
