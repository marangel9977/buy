from flask import Flask, request, abort
from linebot.v3.webhook import WebhookHandler
from linebot.v3.messaging import MessagingApi, Configuration, ApiClient
from linebot.v3.messaging.models import ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.exceptions import InvalidSignatureError
import os

app = Flask(__name__)

CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")

configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

FORMS = {
    "委託門票": "https://docs.google.com/forms/d/e/1FAIpQLSf_phone_form_link",
    "委託場次": "https://docs.google.com/forms/d/e/1FAIpQLSf_computer_form_link",
    "委託張數": "https://docs.google.com/forms/d/e/1FAIpQLSf_unlock_form_link"
}

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_text = event.message.text.strip()
    response_text = ""

    for keyword, link in FORMS.items():
        if keyword in user_text:
            response_text = f"📋 請點選下方連結填寫「{keyword}」報修單：\n👉 {link}"
            break

    if not response_text:
        response_text = (
            "歡迎使用007電腦手機工作室報修系統，請輸入以下任一關鍵字開始：\n"
            "📱 事前委託\n💻 演唱會\n🔓 預約"
        )

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=response_text)]
            )
        )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
