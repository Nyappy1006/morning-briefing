import urllib.request
import json
import datetime
import os

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1484428446615605248/k4C6jxp40lfkCfiaHeVJ39QrBpPZrJgKCNlHSfCLVJ-BRvEENMfmU9_CtYGf75Tu4Wpe"

PROMPT = """
以下のタスクを実行してください。

今日は{date}です。Web検索を使って直近1週間の日本のニュースを収集し、以下の形式でまとめてください。

各カテゴリで検索し、ニュースが見つかった場合のみ記載してください。見つからない場合はそのカテゴリを省略してください。各ニュースにはURLを添付してください。専門用語には括弧で解説をつけてください。

ニュースが見つかったカテゴリについては以下の構成で書いてください。
ニュース概要（2から3文）、背景と文脈、生命保険の銀行窓販営業担当者がお客様との会話でどう活用できるか（自然につながる場合のみ、3から5文で）、URL

━━━━━━━━━━━━━━━━━━━━━━━━
朝刊ブリーフィング {date}
━━━━━━━━━━━━━━━━━━━━━━━━

今週のビッグニュース（カテゴリ問わず3から5件）

銀行・金融機関の動き

証券・投資信託トレンド

海外金利・為替

日本経済・税制・相続関連

生命保険・損害保険業界

認知症・介護・成年後見

富裕層・資産管理トレンド

AI・フィンテック

営業トーク素材（最大3つ）

今週の注目点

━━━━━━━━━━━━━━━━━━━━━━━━
""".strip()

def get_briefing():
    today = datetime.date.today().strftime("%Y%m%d")
    prompt = PROMPT.format(date=today)

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
    briefing = get_briefing()
    print("sending to discord")
    send_to_discord(briefing)
    print("done")
