import urllib.request
import json
import datetime
import os

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1484428446615605248/k4C6jxp40lfkCfiaHeVJ39QrBpPZrJgKCNlHSfCLVJ-BRvEENMfmU9_CtYGf75Tu4Wpe"

def get_weather():
    url = (
        "https://api.open-meteo.com/v1/forecast"
        "?latitude=35.6762&longitude=139.6503"
        "&current=temperature_2m,weathercode"
        "&hourly=temperature_2m,weathercode"
        "&daily=temperature_2m_max,temperature_2m_min"
        "&timezone=Asia%2FTokyo"
        "&forecast_days=1"
    )
    weather_map = {
        0:"快晴",1:"晴れ",2:"晴れ時々曇り",3:"曇り",
        45:"霧",48:"霧",51:"小雨",53:"雨",55:"強雨",
        61:"小雨",63:"雨",65:"強雨",71:"小雪",73:"雪",75:"大雪",
        80:"にわか雨",81:"雨",82:"強雨",95:"雷雨",96:"雷雨",99:"雷雨"
    }
    try:
        with urllib.request.urlopen(url) as res:
            data = json.loads(res.read().decode("utf-8"))
        temp_max = data["daily"]["temperature_2m_max"][0]
        temp_min = data["daily"]["temperature_2m_min"][0]
        hours = data["hourly"]["time"]
        codes = data["hourly"]["weathercode"]
        temps = data["hourly"]["temperature_2m"]
        slots = [6,9,12,15,18,21]
        lines = []
        for h in slots:
            for i,t in enumerate(hours):
                if t.endswith(f"T{h:02d}:00"):
                    lines.append(f"{h}時:{weather_map.get(codes[i],'不明')}{temps[i]}°C")
                    break
        return f"最高{temp_max}°C/最低{temp_min}°C　" + "　".join(lines)
    except:
        return "取得失敗"

PROMPT = """今日は{date}。銀行窓販ホールセラー向けニュースをWeb検索でまとめてください。

ルール：
・今日のニュース優先。なければ直近3日以内。それもなければそのカテゴリは丸ごと省略
・謝罪や「確認できませんでした」等の表現禁止。ない場合は黙って省略
・URLを各ニュースに添付
・専門用語は括弧で解説
・保険営業との接点：自然につながる場合のみ一言。こじつけ禁止

構成：ニュース概要（2〜3文）→背景→保険ヒント（任意）→URL

━━━━━━━━━━━━━━━━━━━━━━━━
朝刊ブリーフィング {date}
東京：{weather}
━━━━━━━━━━━━━━━━━━━━━━━━

今日のビッグニュース（3〜5件）
銀行・金融機関の動き
証券・投資信託トレンド
分配型投信の減配・分配金変更情報
投信×一時払い保険クロスセルネタ
海外金利・為替
日本経済・税制・相続関連
生命保険・損害保険業界
認知症・介護・成年後見
富裕層・資産管理トレンド
AI・フィンテック
今日の支店訪問ネタ（最大3つ、トーク例つき）
Claudeコラム（注目点があれば）

━━━━━━━━━━━━━━━━━━━━━━━━""".strip()

def get_briefing(weather):
    today = datetime.date.today().strftime("%Y年%m月%d日")
    prompt = PROMPT.format(date=today, weather=weather)

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
    print("start")
    weather = get_weather()
    briefing = get_briefing(weather)
    send_to_discord(briefing)
    print("done")
