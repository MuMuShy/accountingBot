from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
from openai_api import OpenAIAPI
import os
from dotenv import load_dotenv
from model import db,Expense,User
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("SQLALCHEMY_DATABASE_URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 建議設定為 False，以避免警告
db.init_app(app)
migrate = Migrate(app, db)
line_key=os.environ.get("LINE_BOT_API")
line_secrect=os.environ.get("LINE_SECRECT")
line_bot_api = LineBotApi(line_key)
handler = WebhookHandler(line_secrect)

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print(event)
    line_user_id = event.source.user_id
    openai_api = OpenAIAPI()
    openai_response = openai_api.get_classification(event.message.text)

    user = User.query.filter_by(line_user_id=line_user_id).first()
    if user is None:
        user = User(line_user_id=line_user_id)
        db.session.add(user)
        db.session.commit()

    parts = openai_response.split()
    print(parts)
    if len(parts) == 3:
        category, item, price = parts
        # 將資料寫入資料庫
        expense = Expense(category=category, item=item, price=float(price), user=user)
        db.session.add(expense)
        db.session.commit()

        response_message = f"已成功記錄開支：\n類別：{category}\n品項：{item}\n價格：{price}"
    else:
        response_message = "抱歉，無法正確辨識您的輸入。"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=response_message)
    )

if __name__ == "__main__":
    app.run(port=3030)
