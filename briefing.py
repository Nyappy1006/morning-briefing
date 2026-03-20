import urllib.request
import json
import datetime
import os

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

PROMPT = """
あなたは日本の生命保険会社の銀行窓販ホールセラー専用のニュースアシスタントです。
今日の日付は{date}です。

あなたの知識をもとに、以下のカテゴリで最近の動向・トレンドをまとめてください。
専門用語には（）でかんたんな解説をつけてください。

━━━━━━━━━━━━━━━━━━━━━━━━
🌅 ホールセラー専用 朝刊ブリーフィング　{date}
━━━━━━━━━━━━━━━━━━━━━━━━

🏦 **メガバンク・地銀の動き**
→ 保険営業的な意味：

📊 **証券・投信トレンド**
→ 保険への影響：

🌍 **海外金利・為替サマリー**
→ 外貨建て保険トーク：

📰 **日本経済・相続贈与関連**
→ 営業ヒント：

🏥 **生命保険・損害保険業界動向**

🧠 **認知症・介護・成年後見関連**
→ トークヒント：

💎 **富裕層ビジネス動向**
→ 営業ヒント：

🤖 **AI・フィンテック動向**

💡 **今日の支店訪問ネタ候補（3つ）**
①
②
③

🔍 **Claudeコラム**

━━━━━━━━━━━━━━━━━━━━━━━━
""".strip()

def get_briefing():
    today = datetime.date.today().strftime("%Y年%m月%d日")
    prompt = PROMPT.format(date=today)

    payload = json.dumps({
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 3000,
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
            headers={"Content-Type": "application/json"},
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
