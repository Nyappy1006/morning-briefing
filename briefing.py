import urllib.request
import json
import datetime
import os

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1484428446615605248/k4C6jxp40lfkCfiaHeVJ39QrBpPZrJgKCNlHSfCLVJ-BRvEENMfmU9_CtYGf75Tu4Wpe"

def get_weather():
    url = "https://api.open-meteo.com/v1/forecast?latitude=35.6762&longitude=139.6503&current=temperature_2m,weathercode&timezone=Asia%2FTokyo"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode("utf-8"))
        temp = data["current"]["temperature_2m"]
        code = data["current"]["weathercode"]
        weather_map = {
            0: "快晴", 1: "晴れ", 2: "晴れ時々曇り", 3: "曇り",
            45: "霧", 48: "霧",
            51: "小雨", 53: "雨", 55: "強雨",
            61: "小雨", 63: "雨", 65: "強雨",
            71: "小雪", 73: "雪", 75: "大雪",
            80: "にわか雨", 81: "雨", 82: "強雨",
            95: "雷雨", 96: "雷雨", 99: "雷雨"
        }
        weather = weather_map.get(code, "不明")
        return f"{weather}　{temp}°C"
    except:
        return "取得できませんでした"

PROMPT = """
以下のタスクを実行してください。

今日は{date}です。Web検索を使って今日のニュースを優先して収集してください。今日の情報がなければ直近3日以内、それもなければそのカテゴリはスキップしてください。新しい情報がないカテゴリは省略してください。無理に埋めないでください。

各ニュースにはURLをつけてください。専門用語には括弧で解説をつけてください。

保険営業との接点について：もし読んでいて自然に「これは保険の話につながるな」と思えた場合のみ、一言添える程度でOKです。無理につなげる必要はありません。つながらなければ書かなくていいです。

ニュースが見つかったカテゴリは以下の構成で書いてください。
ニュース概要（2から3文）、背景と文脈、もし自然につながるなら保険営業のヒント一言、URL

━━━━━━━━━━━━━━━━━━━━━━━━
朝刊ブリーフィング {date}
{weather}
━━━━━━━━━━━━━━━━━━━━━━━━

今日のビッグニュース（カテゴリ問わずトップ3から5件）

銀行・金融機関の動き

証券・投資信託トレンド

分配型投信の減配・分配金変更情報（事実があれば。なければスキップ）

投信×一時払い保険クロスセルネタ（今注目の投信トレンドと一時払い保険をセットで提案できる切り口。新しい動きがなければスキップ）

海外金利・為替

日本経済・税制・相続関連

生命保険・損害保険業界

認知症・介護・成年後見

富裕層・資産管理トレンド

AI・フィンテック

今日の支店訪問ネタ候補（見つかったニュースから最大3つ、一言トーク例つき）

Claudeコラム（今日特に注目すべき点があれば。なければスキップ）

━━━━━━━━━━━━━━━━━━━━━━━━
""".strip()

def get_briefing(weather):
    today = datetime.date.today().strftime("%Y年%m月%d日")
    prompt = PROMPT.format(date=today, weather=f"東京の天気：{weather}")

    payload = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 4000,
        "tools": [{"type": "web_search_20250305", "name": "web_search"}],
        "messages": [{"role": "user", "content": prompt}]
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01"
        },
        method="POST"
    )

    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode("utf-8"))

    text = ""
    for block in data.get("content", []):
        if block.get("type") == "text":
            text += block.get("text", "")

    return text

def send_to_discord(message):
    chunks = []
    while len(message) > 1900:
        split_pos = message[:1900].rfind("\n")
        if split_pos == -1:
            split_pos = 1900
        chunks.append(message[:split_pos])
        message = message[split_pos:]
    chunks.append(message)

    for chunk in chunks:
        payload = json.dumps({"content": chunk}).encode("utf-8")
        req = urllib.request.Request(
            DISCORD_WEBHOOK_URL,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "DiscordBot (morning-briefing, 1.0)"
            },
            method="POST"
        )
        with urllib.request.urlopen(req) as res:
            pass

if __name__ == "__main__":
    print("briefing start")
    weather = get_weather()
    briefing = get_briefing(weather)
    print("sending to discord")
    send_to_discord(briefing)
    print("done")
