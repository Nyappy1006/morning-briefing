import urllib.request
import json
import datetime
import os

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1484428446615605248/k4C6jxp40lfkCfiaHeVJ39QrBpPZrJgKCNlHSfCLVJ-BRvEENMfmU9_CtYGf75Tu4Wpe"

PROMPT = """
あなたは日本の生命保険会社の銀行窓販ホールセラー専用のニュースアシスタントです。
今日の日付は{date}です。

【検索ルール】
・Yahoo!ニュース、NHKニュース、日経電子版、ロイター、ブルームバーグ、産経、朝日、毎日などを検索してください
・直近1週間以内のニュースを優先してください
・1週間以内のニュースが見つからないカテゴリはスキップしてください
・各ニュースには必ず記事URLをつけてください
・専門用語には（）でかんたんな解説をつけてください

【保険営業へのつなげ方】
・ニュースの背景・文脈を丁寧に説明した上で、なぜ保険営業に関係するのかを3〜5文で論理的に説明してください
・「お客様がこういう状況にあるとき、こういう話題を振ると自然につながる」という実践的な視点で書いてください
・無理やりこじつけるくらいなら保険への言及はしないでください

━━━━━━━━━━━━━━━━━━━━━━━━
🌅 ホールセラー専用 朝刊ブリーフィング　{date}
━━━━━━━━━━━━━━━━━━━━━━━━

各カテゴリの構成：
【ニュース概要】記事の内容を2〜3文で説明
【背景・文脈】なぜこれが今起きているのか
【保険営業との接点】お客様との会話にどうつなげるか（3〜5文で丁寧に）
【参考URL】

📣 **今日のビッグニュース**（カテゴリ問わず各メディアのトップ級ニュース3〜5件）
【ニュース概要】
【参考URL】

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
