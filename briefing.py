import urllib.request
import json
import datetime

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1484428446615605248/k4C6jxp40lfkCfiaHeVJ39QrBpPZrJgKCNlHSfCLVJ-BRvEENMfmU9_CtYGf75Tu4Wpe"

payload = json.dumps({"content": "テスト送信！動作確認中🎉"}).encode("utf-8")
req = urllib.request.Request(
    DISCORD_WEBHOOK_URL,
    data=payload,
    headers={
        "Content-Type": "application/json",
        "User-Agent": "DiscordBot (test, 1.0)"
    },
    method="POST"
)
with urllib.request.urlopen(req) as res:
    print("送信成功！ステータス:", res.status)
