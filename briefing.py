import urllib.request
import json
import datetime
import os

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1484428446615605248/k4C6jxp40lfkCfiaHeVJ39QrBpPZrJgKCNlHSfCLVJ-BRvEENMfmU9_CtYGf75Tu4Wpe"

def get_briefing():
    today_dt = datetime.date.today()
    today = today_dt.strftime("%Y年%m月%d日")
    
    # 土日（5, 6）なら実行せずに終了
    if today_dt.weekday() >= 5:
        print(f"今日は{today}（週末）のため、実行をスキップします。")
        return None

    # カテゴリを3つに絞り、Haikuでも精度が出るように調整
    prompt = f"""今日は{today}。銀行窓販ホールセラー向けに、以下3点に絞ってWeb検索し簡潔にまとめて。
URLを各ニュースに添付。専門用語は括弧で解説。

【朝刊ブリーフィング {today}】
1. 金融・市場の主要動向（為替・金利・株価）
2. 投資信託・証券トレンド（新商品、NISA関連など）
3. 保険・相続・介護業界の最新ニュース
"""

    payload = json.dumps({
        "model": "claude-3-5-haiku-20241022", 
        "max_tokens": 2500,
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

    try:
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode("utf-8"))
            
        text = ""
        for block in data.get("content", []):
            if block.get("type") == "text":
                text += block.get("text", "")
        return text
    except Exception as e:
        print(f"APIエラーが発生しました: {e}")
        return None

def send_to_discord(message):
    if not message:
        return
    
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
    print("プロセス開始...")
    briefing = get_briefing()
    if briefing:
        send_to_discord(briefing)
        print("Discordへの送信が完了しました。")
    else:
        print("本日の配信はありません。")
