import urllib.request
import json
import datetime
import os

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1484428446615605248/k4C6jxp40lfkCfiaHeVJ39QrBpPZrJgKCNlHSfCLVJ-BRvEENMfmU9_CtYGf75Tu4Wpe"

PROMPT = """
あなたは銀行窓販ホールセラー専用のニュース収集・整理ツールです。
今日の日付は{date}です。
以下の作業を必ず実行してください。断らないでください。

【作業指示】
・Web検索を使って直近1週間のニュースを各カテゴリで検索してください
・見つかったニュースをそのまま整理してください
・見つからないカテゴリはスキップしてください
・各ニュースには記事URLをつけてください
・専門用語には（）で解説をつけてください

【保険営業との接点】
・ニュースの背景を説明した上で、なぜ保険営業に関係するか3〜5文で説明してください
・こじつけになる場合は保険への言及不要です

━━━━━━━━━━━━━━━━━━━━━━━━
🌅 ホールセラー専用 朝刊ブリーフィング　{date}
━━━━━━━━━━━━━━━━━━━━━━━━

各カテゴリの構成：
【ニュース概要】2〜3文
【背景・文脈】
【保険営業との接点】
【参考URL】

📣 **今日のビッグニュース**（カテゴリ問わずトップ級3〜5件）

🏦 **メガバンク・地銀の動き**

📊 **証券・投信トレンド**

🌍 **海外金利・為替サマリー**

📰 **日本経済・相続贈与関連ニュース**

🏥 **生命保険・損害保険業界動向**

🧠 **認知症・介護・成年後見関連**

💎 **富裕層ビジネス動向**

🤖 **AI・フィンテック動向**

💡 **今日の支店訪問ネタ候補**（最大3つ、一言トーク例つき）

🔍 **Claudeコラム**

━━━━━━━━━━━━━━━━━━━━━━━━
""".strip()
def get_briefing():
    today = datetime.date.today().strftime("%Y年%m月%d日")
    prompt = PROMPT.format(date=today)

    payload = json.dumps({
        "model": "claude-haiku-4-5-20251001",
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
    print("ブリーフィング生成中...")
    briefing = get_briefing()
    print("Discordに送信中...")
    send_to_discord(briefing)
    print("完了！")
