# 載入需要的模組
from __future__ import unicode_literals
import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import time
from linebot.exceptions import LineBotApiError
import configparser

app = Flask(__name__)

# LINE 聊天機器人的基本資料
config = configparser.ConfigParser()
config.read('config.ini')

line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token')) #聊天機器人的 Chennel access token
handler = WebhookHandler(config.get('line-bot', 'channel_secret')) #聊天機器人的 Channel secret

# 接收 LINE 的資訊
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 學你說話，存user_id
@handler.add(MessageEvent, message=TextMessage)
def echo(event):
    if event.source.user_id != "Udeadbeefdeadbeefdeadbeefdeadbeef": #忽略line的webhook驗證時的錯誤
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text)
        )

        user_id = event.source.user_id #存user_id
        # push_message(user_id) #開始進行主動推播訊息
        

#主動推播
def push_message(user_id):
    # push message to one user
    line_bot_api.push_message(user_id, TextSendMessage(text='Hello World!'))

if __name__ == "__main__":
    app.run()