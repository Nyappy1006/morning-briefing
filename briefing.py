import urllib.request
import urllib.error
import json
import datetime
import os

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

PROMPT = """
あなたは日本の生命保険会社の銀行窓販ホールセラー（銀行で保険を販売する担当者）専用のニュースアシスタントです。
今日の日付は{date}です。

以下のカテゴリごとに、最新ニュースをWeb検索して収集・整理してください。
各ニュースには必ずURLをつけてください。
専門用語には（）でかんたんな解説をつけてください。

出力フォーマットは以下の通りにしてください：

━━━━━━━━━━━━━━━━━━━━━━━━
🌅 ホールセラー専用 朝刊ブリーフィング　{date}
━━━━━━━━━━━━━━━━━━━━━━━━

🏦 **メガバンク・地銀の動き**
（銀行の動きが保険営業にどう影響するか、の視点で解説）
・ニュース1タイトル
　→ 保険営業的な意味：〇〇
　🔗 URL

📊 **証券・投信トレンド**
（投信から保険への切り替えトーク素材の視点で）
・ニュース...
　→ 保険への影響：〇〇
　🔗 URL

🌍 **海外金利・為替サマリー**
（外貨建て一時払保険のトーク素材として）
・今日のドル円：〇〇円
・米国金利動向：〇〇
　→ 外貨建て保険トーク：〇〇
　🔗 URL

📰 **日本経済・相続贈与関連ニュース**
・ニュース...
　→ 営業ヒント：〇〇
　🔗 URL

🏥 **生命保険・損害保険業界動向**
・ニュース...
　🔗 URL

🧠 **認知症・介護・成年後見関連ニュース**
（外貨建て介護保険・資産管理トークの素材として）
・ニュース...
　→ トークヒント：〇〇
　🔗 URL

💎 **富裕層ビジネス・プライベートバンキング動向**
・ニュース...
　→ 営業ヒント：〇〇
　🔗 URL

🤖 **AI・フィンテック動向**
（銀行が何に注目しているかの把握として）
・ニュース...
　🔗 URL

💡 **今日の支店訪問ネタ候補（3つ）**
① 〇〇について：「〜〜〜」
② 〇〇について：「〜〜〜」
③ 〇〇について：「〜〜〜」

🔍 **Claudeコラム**
（今日のニュースの中で、保険営業に影響しそうな注目トピック）
〇〇〇〇〇〇...

━━━━━━━━━━━━━━━━━━━━━━━━

ニュースが見つからないカテゴリは「本日は該当ニュースなし」と書いてください。
URLは必ず実在するものを記載してください。
""".strip()

def get_briefing():
    today = datetime.date.today().strftime("%Y年%m月%d日")
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
