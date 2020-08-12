# 載入需要的模組
from __future__ import unicode_literals
import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.models import ImageSendMessage, VideoSendMessage, LocationSendMessage, StickerSendMessage
import time
from linebot.exceptions import LineBotApiError
import configparser

import requests
import re
import random
import urllib3
from bs4 import BeautifulSoup

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

def oil_price():
    target_url = 'https://gas.goodlife.tw/'
    rs = requests.session()
    res = rs.get(target_url, verify=False)
    res.encoding = res.apparent_encoding
    soup = BeautifulSoup(res.text, 'html.parser')
    title = soup.select('#main')[0].text.replace('\n', '').split('(')[0]
    gas_price = soup.select('#gasprice')[0].text.replace('\n\n\n', '').replace(' ', '')
    cpc = soup.select('#cpc')[0].text.replace(' ', '')
    content = '{}\n{}{}'.format(title, gas_price, cpc)
    return content

def google():
    target_url = 'https://news.google.com/topstories?hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant'
    print('Start parsing google news....')
    rs = requests.session()
    res = rs.get(target_url, verify=False)
    soup = BeautifulSoup(res.text, 'html.parser')
    content = ''
    for index, news in enumerate(soup.find_all(class_='NiLAwe')):
        try:
            if index == 10:
                return content
            title = news.find(class_='DY5T1d').text
            link = 'https://news.google.com/' + news.find(class_='DY5T1d')['href']
            image = news.find(class_='tvs3Id')['src']
            content += '\n{}\n{}\n{}\n\n\n'.format(image, title, link)
        except:
            print('')
    return content

def technews():
    target_url = 'https://technews.tw/'
    print('Start parsing movie ...')
    rs = requests.session()
    res = rs.get(target_url, verify=False)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    content = ""

    for index, data in enumerate(soup.select('article div h1.entry-title a')):
        if index == 12:
            return content
        title = data.text
        link = data['href']
        content += '{}\n{}\n\n'.format(title, link)
    return content

def panx():
    target_url = 'https://panx.asia/'
    print('Start parsing ptt hot....')
    rs = requests.session()
    res = rs.get(target_url, verify=False)
    soup = BeautifulSoup(res.text, 'html.parser')
    content = ""
    for data in soup.select('div.container div.row div.desc_wrap h2 a'):
        title = data.text
        link = data['href']
        content += '{}\n{}\n\n'.format(title, link)
    return content

def movie():
    target_url = 'http://www.atmovies.com.tw/movie/next/0/'
    print('Start parsing movie ...')
    rs = requests.session()
    res = rs.get(target_url, verify=False)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    content = ""
    for index, data in enumerate(soup.find_all(class_='filmtitle')):
        if index == 20:
            return content
        title = data.text.replace('\t', '').replace('\r', '')
        link = "http://www.atmovies.com.tw" + data.find('a', href=True)['href']
        #image = data.find_previous_sibling('a').find('img')['src']
        content += '{}\n{}\n'.format(title, link)
    return content

def weather():
    target_url = 'https://weather.yam.com/%E5%85%A7%E5%9F%94%E9%84%89/%E5%B1%8F%E6%9D%B1%E7%B8%A3'
    print('Start parsing weather ...')
    rs = requests.session()
    res = rs.get(target_url, verify=False)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    
    content = ''
    descs = soup.find(class_='info').find(class_='container').find_all('p')
    for desc in descs:
        content += '\n{}'.format(desc.text)
    
    today = soup.find(class_='today')
    temperature = today.find(class_='tempB').text
    content += '\n氣溫：{}\n'.format(temperature)

    others = today.select('.right .wrap .detail')[0].find_all('p')
    for other in others:
        content += '\n{}'.format(other.text)
    
    return content

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print("event.reply_token:", event.reply_token)
    print("event.message.text:", event.message.text)

    if event.message.text == "Google新聞":
        content = google()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0
    
    if event.message.text == "油價查詢":
        content = oil_price()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0

    if event.message.text == "科技新報":
        content = technews()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0

    if event.message.text == "泛新聞":
        content = panx()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0

    if event.message.text == "電影":
        content = movie()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0

    if event.message.text == "氣象":
        content = weather()
        line_bot_api.reply_message(
           event.reply_token,
           TextSendMessage(text=content))
        return 0

    text_split = event.message.text.split()
    if text_split[0] == "爬ptt表特":
        # content = text_split[1] #篇數

        import requests
        from bs4 import BeautifulSoup
        articles_switch = text_split[1] - 1
        url = "https://www.ptt.cc/bbs/Beauty/index.html"

        #18歲驗證
        session = requests.Session()
        session.post('https://www.ptt.cc/ask/over18', data = {'from' : url, 'yes' : 'yes'})
        response = session.get(url)
        soup     = BeautifulSoup(response.text, 'html.parser')

        #存第一頁文章網址
        article_list = soup.select('div.title a')
        img_url = []
        for t in article_list:
            img_url.append('https://www.ptt.cc' + t['href'])
        if (text_split[1] <= len(img_url)) and (text_split[1] > 0):
            #取第幾篇文章
            response = session.get(img_url[articles_switch]) #篇數
            soup     = BeautifulSoup(response.text, 'html.parser')
            img_list = soup.select('div.richcontent a')

            #存出圖檔網址
            img = []
            for t in img_list:
               img.append(t['href'])
        
            if len(img) > 0:
                content = '搜索到了!'
                for i in img:
                    #傳出圖檔
                    try:
                        line_bot_api.push_message(to, ImageSendMessage(original_content_url = 'https:' + i, preview_image_url = 'https:' + i))
                    except LineBotApiError as e:
                        # error handle
                        raise e
                    #傳出圖檔
        
            else: 
                content = '此篇沒有圖片喔'
        else:
            content = '超過文章數了，請輸入正常的數字'



        line_bot_api.reply_message(
           event.reply_token,
           TextSendMessage(text=content))
        return 0
# # 學你說話，存user_id
# @handler.add(MessageEvent, message=TextMessage)
# def echo(event):
#     if event.source.user_id != "Udeadbeefdeadbeefdeadbeefdeadbeef": #忽略line的webhook驗證時的錯誤
#         line_bot_api.reply_message(
#             event.reply_token,
#             TextSendMessage(text=event.message.text)
#         )

#         user_id = event.source.user_id #存user_id
#         push_message(user_id) #開始進行主動推播訊息
        

# #主動推播
# def push_message(user_id):
#     # push message to one user
#     line_bot_api.push_message(user_id, TextSendMessage(text='Hello World!'))

if __name__ == "__main__":
    app.run()