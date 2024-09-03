import aiohttp
import asyncio
import time
import telebot
import qrcode
import io
from datetime import datetime, timedelta, date
from threading import Lock
from bs4 import BeautifulSoup
import requests 
import tempfile
import subprocess, sys
import random
import json
import os
import sqlite3
import hashlib
import zipfile
from PIL import Image, ImageOps, ImageDraw, ImageFont
from io import BytesIO
from urllib.parse import urljoin, urlparse, urldefrag
from telebot import TeleBot, types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

THỜI_GIAN_CHỜ = timedelta(seconds=300)
FREE_GIỚI_HẠN_CHIA_SẺ = 400
VIP_GIỚI_HẠN_CHIA_SẺ = 1000
viptime = 100
ALLOWED_GROUP_ID = -1002191171631   # ID BOX
admin_diggory = "khangdino" # ví dụ : để user name admin là @diggory347 bỏ dấu @ đi là đc
name_bot = "DINO BOT"
telegram = "@dichcutelegramm"
web = "https://lequockhang.site"
facebook = "no" 
allowed_group_id = -1002191171631 # ID BOX
users_keys = {}
key = ""
freeuser = []
auto_spam_active = False
last_sms_time = {}
allowed_users = []
processes = []
ADMIN_ID =  5759867629 # ID ADMIN
connection = sqlite3.connect('user_data.db')
cursor = connection.cursor()
last_command_time = {}
user_cooldowns = {}
share_count = {}
global_lock = Lock()
admin_mode = False
share_log = []
tool = 'https://lequockhang.site/tool.html/'
BOT_LINK = 'https://t.me/spamython_bot'
TOKEN = '6939568666:AAEmlN0662Fgkow6m-HXsa6eIU3mwBjd28g'  
bot = TeleBot(TOKEN)

ADMIN_ID = 7193749511  # id admin
admins = {7193749511}
bot_admin_list = {}
cooldown_dict = {}
allowed_users = []
muted_users = {}

def get_time_vietnam():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
def check_command_cooldown(user_id, command, cooldown):
    current_time = time.time()
    
    if user_id in last_command_time and current_time - last_command_time[user_id].get(command, 0) < cooldown:
        remaining_time = int(cooldown - (current_time - last_command_time[user_id].get(command, 0)))
        return remaining_time
    else:
        last_command_time.setdefault(user_id, {})[command] = current_time
        return None

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        expiration_time TEXT
    )
''') 
connection.commit()

def TimeStamp():
  now = str(date.today())
  return now


def load_users_from_database():
  cursor.execute('SELECT user_id, expiration_time FROM users')
  rows = cursor.fetchall()
  for row in rows:
    user_id = row[0]
    expiration_time = datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
    if expiration_time > datetime.now():
      allowed_users.append(user_id)


def save_user_to_database(connection, user_id, expiration_time):
  cursor = connection.cursor()
  cursor.execute(
    '''
        INSERT OR REPLACE INTO users (user_id, expiration_time)
        VALUES (?, ?)
    ''', (user_id, expiration_time.strftime('%Y-%m-%d %H:%M:%S')))
  connection.commit()
###



###
####
start_time = time.time()

def load_allowed_users():
    try:
        with open('admin_vip.txt', 'r') as file:
            allowed_users = [int(line.strip()) for line in file]
        return set(allowed_users)
    except FileNotFoundError:
        return set()

vip_users = load_allowed_users()

async def share_post(session, token, post_id, share_number):
    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate',
        'connection': 'keep-alive',
        'content-length': '0',
        'host': 'graph.facebook.com'
    }
    try:
        url = f'https://graph.facebook.com/me/feed'
        params = {
            'link': f'https://m.facebook.com/{post_id}',
            'published': '0',
            'access_token': token
        }
        async with session.post(url, headers=headers, params=params) as response:
            res = await response.json()
            print(f"Chia sẻ bài viết thành công: {res}")
    except Exception as e:
        print(f"Lỗi khi chia sẻ bài viết: {e}")

async def get_facebook_post_id(session, post_url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, như Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

        async with session.get(post_url, headers=headers) as response:
            response.raise_for_status()
            text = await response.text()

        soup = BeautifulSoup(text, 'html.parser')
        meta_tag = soup.find('meta', attrs={'property': 'og:url'})

        if meta_tag and 'content' in meta_tag.attrs:
            linkpost = meta_tag['content'].split('/')[-1]
            async with session.post('https://scaninfo.vn/api/fb/getID.php?url=', data={"link": linkpost}) as get_id_response:
                get_id_post = await get_id_response.json()
                if 'success' in get_id_post:
                    post_id = get_id_post["id"]
                return post_id
        else:
            raise Exception("Không tìm thấy ID bài viết trong các thẻ meta")

    except Exception as e:
        return f"Lỗi: {e}"


@bot.message_handler(commands=['time'])
def handle_time(message):
    uptime_seconds = int(time.time() - start_time)
    
    uptime_minutes, uptime_seconds = divmod(uptime_seconds, 60)
    bot.reply_to(message, f'Bot đã hoạt động được: {uptime_minutes} phút, {uptime_seconds} giây')
#tiktok
def fetch_tiktok_data(url):
    api_url = f'https://tikwm.com/api/?url={url}'
    try:
        response = requests.get(api_url)
        response.raise_for_status()  
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching TikTok data: {e}")
        return None

@bot.message_handler(commands=['tiktok'])
def tiktok_command(message):
    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) == 2:
        url = command_parts[1].strip()
        data = fetch_tiktok_data(url)
        
        if data and 'code' in data and data['code'] == 0:
            video_title = data['data'].get('title', 'N/A')
            video_url = data['data'].get('play', 'N/A')
            music_title = data['data']['music_info'].get('title', 'N/A')
            music_url = data['data']['music_info'].get('play', 'N/A')
            
            reply_message = f"Tiêu đề Video: {video_title}\nĐường dẫn Video: {video_url}\n\nTiêu đề Nhạc: {music_title}\nĐường dẫn Nhạc: {music_url}"
            bot.reply_to(message, reply_message)
        else:
            bot.reply_to(message, "Không thể lấy dữ liệu từ TikTok.")
    else:
        bot.reply_to(message, "Hãy cung cấp một đường dẫn TikTok hợp lệ.")
				
import telebot
import google.generativeai as genai
from io import BytesIO
import requests

# Configure Google Gemini API
api_key = 'AIzaSyD8Wt-XBu2jZV3sEUKsT_IxjSxMCe5D894'
genai.configure(api_key=api_key)


# Create the model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(generation_config=generation_config)

# Create a chat session
chat_session = model.start_chat(history=[])

@bot.message_handler(commands=['gpt'])
def handle_gpt(message):
    user_input = ' '.join(message.text.split()[1:])
    if not user_input:
        bot.reply_to(message, "Please provide a message after the /gpt command.")
        return

    response = chat_session.send_message(user_input)
    bot.reply_to(message, response.text)

@bot.message_handler(commands=['generate_image'])
def handle_image(message):
    user_input = ' '.join(message.text.split()[1:])
    if not user_input:
        bot.reply_to(message, "Please provide a description for the image after the /generate_image command.")
        return

    # Replace this with actual image generation API call
    image_url = generate_image(user_input)
    
    if image_url:
        # Download the image
        image_response = requests.get(image_url)
        image_data = BytesIO(image_response.content)
        
        # Send the image
        bot.send_photo(message.chat.id, photo=image_data)
    else:
        bot.reply_to(message, "Failed to generate image.")

def generate_image(description):
    # This function should call your image generation API and return the image URL
    # Example (this is a placeholder and needs to be replaced with your actual image generation code):
    return "https://example.com/path/to/generated/image.png"

		



@bot.message_handler(commands=['tool'])
def send_tool_links(message):
    markup = types.InlineKeyboardMarkup()
    
    tool_links = [
        ("https://http://lequockhang.site/tool.html", "Tool Free")
    ]
    
    for link, desc in tool_links:
        markup.add(types.InlineKeyboardButton(text=desc, url=link))
    
    bot.reply_to(message, "Ok", reply_markup=markup)
####
#####
video_url = 'https://v16m-default.akamaized.net/67c8daa5f2a69c404bee8a982b27c162/66d20e49/video/tos/alisg/tos-alisg-pve-0037c001/o4Dv7LjIQDAbBoMpgIfACgXhgCefJcUntyczQL/?a=0&bti=OUBzOTg7QGo6OjZAL3AjLTAzYCMxNDNg&ch=0&cr=0&dr=0&lr=all&cd=0%7C0%7C0%7C0&cv=1&br=4912&bt=2456&cs=0&ds=6&ft=XE5bCqT0majPD12BLCT73wUOx5EcMeF~O5&mime_type=video_mp4&qs=0&rc=ODtpNWRpO2g2ZGg8OTg7M0BpMzdxcjg6ZnZwajMzODczNEAwMi5fMDBjXzExMmEzNl8yYSNsLl9pcjRvc2hgLS1kMS1zcw%3D%3D&vvpl=1&l=202408301223484AE9A7771AD77010DDFA&btag=e00088000&shp=6da16bae&shcp=-'
@bot.message_handler(commands=['add', 'adduser'])
def add_user(message):
    admin_id = message.from_user.id
    if admin_id != ADMIN_ID:
        bot.reply_to(message, 'mày làm cái chó gì vậy chỉ có admin mới dùng được lệnh này')
        return

    if len(message.text.split()) == 1:
        bot.reply_to(message, 'VUI LÒNG NHẬP ID NGƯỜI DÙNG')
        return

    user_id = int(message.text.split()[1])
    allowed_users.append(user_id)
    expiration_time = datetime.now() + timedelta(days=30)
    connection = sqlite3.connect('user_data.db')
    save_user_to_database(connection, user_id, expiration_time)
    connection.close()

    # Gửi video với tiêu đề
    caption_text = (f'NGƯỜI DÙNG CÓ ID {user_id}🏆🏆🏆🏆🏆🏆🏆🏆                                ĐÃ ĐƯỢC THÊM VÀO DANH SÁCH ĐƯỢC PHÉP SỬ DỤNG LỆNH /spamvip')
    bot.send_video(
        message.chat.id,
        video_url,
        caption=caption_text
    )

load_users_from_database()

def is_key_approved(chat_id, key):
    if chat_id in users_keys:
        user_key, timestamp = users_keys[chat_id]
        if user_key == key:
            current_time = datetime.datetime.now()
            if current_time - timestamp <= datetime.timedelta(hours=2):
                return True
            else:
                del users_keys[chat_id]
    return False

@bot.message_handler(commands=['share'])
def share(message):
    global bot_active, global_lock, admin_mode
    chat_id = message.chat.id
    user_id = message.from_user.id
    current_time = datetime.now()


    if not bot_active:
        msg = bot.reply_to(message, 'Bot hiện đang tắt.')
        time.sleep(10)
        try:
            bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
        except telebot.apihelper.ApiTelegramException as e:
            print(f"Error deleting message: {e}")
        return

    if chat_id != ALLOWED_GROUP_ID:
        msg = bot.reply_to(message, 'Làm Trò Gì Khó Coi Vậy')
        time.sleep(10)
        try:
            bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
        except telebot.apihelper.ApiTelegramException as e:
            print(f"Error deleting message: {e}")
        return
    
    if admin_mode and user_id not in admins:
        msg = bot.reply_to(message, 'Chế độ admin hiện đang bật, đợi tí đi.')
        time.sleep(10)
        try:
            bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
        except telebot.apihelper.ApiTelegramException as e:
            print(f"Error deleting message: {e}")
        return
    
    try:
        global_lock.acquire()  
        
        args = message.text.split()
        if user_id not in allowed_users and user_id not in freeuser:
            bot.reply_to(message, 'bot chỉ hoạt động khi bạn mua key và get key bằng lệnh /laykey')
            return
        if len(args) != 3:
            msg = bot.reply_to(message, '''
╔══════════════════
║<|> /laykey trước khi sài hoặc mua
║<|> /key <key> để nhập key 
║<|> ví dụ /key ABCDXYZ
║<|> /share {link_buff} {số lần chia sẻ}
╚══════════════════''')
            time.sleep(10)
            try:
                bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
            except telebot.apihelper.ApiTelegramException as e:
                print(f"Error deleting message: {e}")
            return

        post_id, total_shares = args[1], int(args[2])

        # Kiểm tra người dùng VIP hoặc Free
        if user_id in allowed_users:
            handle_vip_user(message, user_id, post_id, total_shares, current_time)
        elif user_id in freeuser:
            handle_free_user(message, user_id, post_id, total_shares, current_time)
            
    except Exception as e:
        msg = bot.reply_to(message, f'Lỗi: {e}')
        time.sleep(10)
        try:
            bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
        except telebot.apihelper.ApiTelegramException as e:
            print(f"Error deleting message: {e}")

    finally:
        if global_lock.locked():
            global_lock.release()  

def handle_vip_user(message, user_id, post_id, total_shares, current_time):
    if user_id in user_cooldowns:
        last_share_time = user_cooldowns[user_id]
        if current_time < last_share_time + timedelta(seconds=viptime):
            remaining_time = (last_share_time + timedelta(seconds=viptime) - current_time).seconds
            msg = bot.reply_to(message, f'Bạn cần đợi {remaining_time} giây trước khi chia sẻ lần tiếp theo.\nvip Delay')
            time.sleep(10)
            bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
            return
    if total_shares > VIP_GIỚI_HẠN_CHIA_SẺ:
        msg = bot.reply_to(message, f'Số lần chia sẻ vượt quá giới hạn {VIP_GIỚI_HẠN_CHIA_SẺ} lần.')
        time.sleep(10)
        bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
        return
     #phân file token khác nhau
    file_path = 'token.txt'
    with open(file_path, 'r') as file:
        tokens = file.read().split('\n')

    total_live = len(tokens)

    sent_msg = bot.reply_to(message,
        f'Bot Chia Sẻ Bài Viết\n\n'
        f'║Số Lần Chia Sẻ: {total_shares}\n'
        f'║Free Max 400 Share\n'
        f'║{message.from_user.username} Đang Dùng Vip',
        parse_mode='HTML'
    )

    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
#check live token
    if total_live == 0:
        bot.edit_message_text(chat_id=message.chat.id, message_id=sent_msg.message_id, text='Không có token nào hoạt động.')
        return

    share_log.append({
        'username': message.from_user.username,
        'user_id': user_id,
        'time': current_time.strftime('%Y-%m-%d %H:%M:%S'),
        'post_id': post_id,
        'total_shares': total_shares
    })

    async def share_with_delay(session, token, post_id, count):
        await share_post(session, token, post_id, count)
        await asyncio.sleep(1)

    async def main():
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i in range(total_shares):
                token = random.choice(tokens)
                share_number = share_count.get(user_id, 0) + 1
                share_count[user_id] = share_number
                tasks.append(share_with_delay(session, token, post_id, share_number))
            await asyncio.gather(*tasks)

    asyncio.run(main())

    bot.edit_message_text(chat_id=message.chat.id, message_id=sent_msg.message_id, text='Đơn của bạn đã hoàn thành')

def handle_free_user(message, user_id, post_id, total_shares, current_time):
    if user_id in user_cooldowns:
        last_share_time = user_cooldowns[user_id]
        if current_time < last_share_time + THỜI_GIAN_CHỜ:
            remaining_time = (last_share_time + THỜI_GIAN_CHỜ - current_time).seconds
            msg = bot.reply_to(message, f'Bạn cần đợi {remaining_time} giây trước khi chia sẻ lần tiếp theo.')
            time.sleep(10)
            bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
            return

    if total_shares > FREE_GIỚI_HẠN_CHIA_SẺ:
        msg = bot.reply_to(message, f'Số lần chia sẻ vượt quá giới hạn {FREE_GIỚI_HẠN_CHIA_SẺ} lần.')
        time.sleep(10)
        bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
        return
    #token free
    file_path = 'token.txt'
    with open(file_path, 'r') as file:
        tokens = file.read().split('\n')

    total_live = len(tokens)

    sent_msg = bot.reply_to(message,
        f'Bot Chia Sẻ Bài Viết\n\n'
        f'║Số lần share: {total_shares}\n'
        f'║Vip Max 1000 Share\n'
        f'║{message.from_user.username} Đang Share Free',
        parse_mode='HTML'
    )

    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    if total_live == 0:
        bot.edit_message_text(chat_id=message.chat.id, message_id=sent_msg.message_id, text='Không có token nào hoạt động.')
        return

    share_log.append({
        'username': message.from_user.username,
        'user_id': user_id,
        'time': current_time.strftime('%Y-%m-%d %H:%M:%S'),
        'post_id': post_id,
        'total_shares': total_shares
    })

    async def share_with_delay(session, token, post_id, count):
        await share_post(session, token, post_id, count)
        await asyncio.sleep(1)

    async def main():
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i in range(total_shares):
                token = random.choice(tokens)
                share_number = share_count.get(user_id, 0) + 1
                share_count[user_id] = share_number
                tasks.append(share_with_delay(session, token, post_id, share_number))
            await asyncio.gather(*tasks)

    asyncio.run(main())

    user_cooldowns[user_id] = current_time

    bot.edit_message_text(chat_id=message.chat.id, message_id=sent_msg.message_id, text='Đơn của bạn đã hoàn thành')
@bot.message_handler(commands=['vip'])
def handle_vip(message):
    chat_id = message.chat.id
    if message.from_user.id not in vip_users:
        bot.reply_to(message, "Bạn không phải là thành viên VIP.")
        return

   
@bot.message_handler(commands=['ls'])
def sharelog(message):
    if message.from_user.id in admins:
        if not share_log:
            bot.reply_to(message, 'chưa ai sử dụng hết')
            return
        
        log_text = "Danh sách người đã sử dụng lệnh share:\n"
        for log in share_log:
            log_text += f"<blockquote>Lịch_Sử\n- User: {log['username']} (ID: {log['user_id']})\n- vào lúc {log['time']}\n- Post LINK: <a href='{log['post_id']}'>link</a>\n- Số lần chia sẻ: {log['total_shares']}\n</blockquote>"
        
        bot.reply_to(message, log_text, parse_mode='HTML')
    else:
        bot.reply_to(message, 'admin mới xem đc á m')
@bot.message_handler(commands=['admod'])
def handle_on(message):
    global admin_mode
    if message.from_user.id in admins:
        admin_mode = True
        bot.reply_to(message, "Chế độ admin đã bật.")
    else:
        bot.reply_to(message, "Bạn không có quyền bật chế độ admin.")
###


@bot.message_handler(commands=['unadmod'])
def handle_off(message):
    global admin_mode
    if message.from_user.id in admins:
        admin_mode = False
        bot.reply_to(message, "Chế độ admin đã tắt.")
    else:
        bot.reply_to(message, "Bạn không có quyền tắt chế độ admin.")
@bot.message_handler(commands=['off'])
def bot_off(message):
    global bot_active
    if message.from_user.id in admins:
        bot_active = False
        bot.reply_to(message, 'Bot đã được tắt.')
    else:
        bot.reply_to(message, 'Bạn không có quyền thực hiện thao tác này.')
@bot.message_handler(commands=['on'])
def bot_on(message):
    global bot_active
    if message.from_user.id in admins:
        bot_active = True
        bot.reply_to(message, 'Bot đã được bật.')
    else:
        bot.reply_to(message, 'Bạn không có quyền thực hiện thao tác này.')
				
import telebot
from telebot import types


name_bot = "DINO TOOL"  # Thay thế tên bot của bạn

@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    username = message.from_user.username
    response_message = (
        "```\n"  # Mở đầu khối mã với ba dấu backtick
        f"┌───⭓ {name_bot}\n"
        f"│» Xin chào @{username}\n"
        "│» 🆘 /help : Lệnh trợ giúp\n"
        "│» 📲 /spam : Spam SMS FREE\n"
        "│» 💎 /spamvip : Spam SMS VIP - Mua Vip 30k/Tháng\n"
        "│» 🆔 /id : Lấy ID Tele Của Bản Thân\n"
        "│» 🔊 /voice : Đổi Văn Bản Thành Giọng Nói\n"
				"│» 🤖 /gpt Trò Chuyển Với GPT\n"
        "│» 🎁 /qr : Tạo QR\n"
        "│» 😶 /face : Lấy ảnh mặt random\n"
        "│» 🎵 /tiktok : Check Thông Tin - Tải Video Tiktok\n"
        "│» 🛠️ /tool : Tải Tool\n"
        "│» ⏰ /time : Check thời gian hoạt động\n"
        "│» 👥 /ad : Có bao nhiêu admin\n"
        "│» 📝 /code : Lấy Code HTML của web\n"
        "│» 🌐 /tv : Đổi Ngôn Ngữ Sang Tiếng Việt\n"
        "│» 🔧 LỆNH CHO ADMIN\n"
        "│» 🔄 /rs : Khởi Động Lại\n"
        "│» 📴 /freeoff : Tắt lệnh spam free\n"
        "│» 📴 /freeon : Bật lệnh spam free\n"
        "│» ➕ /add : Thêm người dùng sử dụng /spamvip\n"
        "│» ➕ /remove : xoá khỏi danh sách sử dụng vip\n"
        "│» 🌠🌠🌠NHÓM CHAT BOT @dinotool\n"
        "└───────────⧕\n"
        "```"  # Kết thúc khối mã với ba dấu backtick
    )

    bot.reply_to(message, response_message, parse_mode='MarkdownV2')




import time
import telebot
from datetime import datetime, timedelta
import os
import tempfile
import subprocess
import time
from datetime import datetime, timedelta
import telebot
from telebot import types


# Khai báo giá trị cần thiết
bot_active = True
admin_mode = False
free_mode = True  # Biến để kiểm soát trạng thái của lệnh /spam
last_usage = {}
user_usage_count = {}
blacklist = {"112", "113", "114", "115", "116", "117", "118", "119", "0", "1", "2", "3", "4"}
admins = set()
ADMIN_ID = 7193749511  # Thay đổi thành ID của admin
group_id = -1002191171631  # Thay đổi thành ID của nhóm
# Kiểm tra quyền admin
def is_admin(user_id):
    return user_id == ADMIN_ID

# Lệnh /freeoff
@bot.message_handler(commands=['freeoff'])
def freeoff(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, 'mày làm cái chó gì vậy chỉ có admin mới dùng được lệnh này')
        return

    global free_mode
    free_mode = False
    bot.reply_to(message, "Lệnh /spam hiện tại đã bị vô hiệu hóa hãy thử lại sau khi Admin bật lại nhé📴📴📴")

# Lệnh /freeon
@bot.message_handler(commands=['freeon'])
def freeon(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, 'mày làm cái chó gì vậy chỉ có admin mới dùng được lệnh này')
        return

    global free_mode
    free_mode = True
    bot.reply_to(message, "Lệnh /spam đã được kích hoạt lại bạn có thể sử dụng lại được lệnh spam rồi nhé🔛🔛🔛.")

		

@bot.message_handler(commands=['spam'])
def spam(message):
    if message.chat.id != group_id:
        return

    user_id = message.from_user.id
    user_first_name = message.from_user.first_name
    user_username = message.from_user.username
    current_time = time.time()

    if not bot_active:
        msg = bot.reply_to(message, 'Bot hiện đang tắt.')
        time.sleep(10)
        try:
            bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
        except telebot.apihelper.ApiTelegramException as e:
            print(f"Error deleting message: {e}")
        return

    if admin_mode and user_id not in admins:
        bot.reply_to(message, 'Có lẽ admin đang fix gì đó, hãy đợi một chút.')
        return

    if not free_mode:
        bot.reply_to(message, "Lệnh /spam hiện tại đã bị vô hiệu hóa hãy thử lại sau khi Admin bật lại nhé📴📴📴.")
        return

    if user_id in last_usage and current_time - last_usage[user_id] < 100:
        wait_time = 100 - (current_time - last_usage[user_id])
        bot.reply_to(message, f"Vui lòng đợi {wait_time:.1f} giây trước khi sử dụng lệnh lại.")
        return

    last_usage[user_id] = current_time

    params = message.text.split()[1:]
    if len(params) != 2:
        bot.reply_to(message, "Ví dụ 📞 /spam 037373737 2")
        return

    sdt, count = params

    if not count.isdigit():
        bot.reply_to(message, "📞 Số lần spam không hợp lệ. Vui lòng chỉ nhập số.")
        return

    count = int(count)

    if count > 2:
        bot.reply_to(message, "📞 /spam sdt 2 gói free giới hạn là 2. Đợi 100⏰⏰⏰ giây để sử dụng lại.")
        return

    if sdt in blacklist:
        bot.reply_to(message, f"Số điện thoại {sdt} đã bị cấm spam.")
        return

    end_time = datetime.now() + timedelta(minutes= 2 )
    formatted_end_time = end_time.strftime("%d/%m/%Y %H:%M:%S")


    diggory_chat3 = f'''
✅ 𝐓𝐇𝐎̂𝐍𝐆 𝐓𝐈𝐍 𝐒𝐏𝐀𝐌𝐅𝐑𝐄𝐄 ✅
━━━━━━━━━━━━━━━━━━━━━━
👤 Tên telegram: {user_first_name}
👤 Username: {user_username if user_username else "Không có"}
🆔 ID: {user_id}
📞 Số điện thoại: {sdt}
⏳ Thời gian: 2 phút
🕒 Thời gian dự kiến kết thúc: {formatted_end_time}
━━━━━━━━━━━━━━━━━━━━━━
🤖 𝘽𝙊𝙏 𝘽𝙔 :@dinotool
━━━━━━━━━━━━━━━━━━━━━━
✨ Spam đã được khởi động! Chúng tôi sẽ hành tấn công spam hoàn tất.
━━━━━━━━━━━━━━━━━━━━━━
👤 Bạn đang sử dụng gói miễn phí
👉 hay liên hệ ngay admin để kích hoạt gói VIP với trải nghiệm tốt hơn
━━━━━━━━━━━━━━━━━━━━━━
➡️ Để liên hệ admin và xem hướng dẫn, vui lòng gõ /start.
━━━━━━━━━━━━━━━━━━━━━━


'''

		
    # Gửi thông tin spam một lần
    bot.reply_to(message, diggory_chat3)

    script_filename = "dec.py"  # Tên file Python trong cùng thư mục
    try:
        # Kiểm tra xem file có tồn tại không
        if not os.path.isfile(script_filename):
            bot.reply_to(message, "Không tìm thấy file script. Vui lòng kiểm tra lại.")
            return

        # Đọc nội dung file với mã hóa utf-8
        with open(script_filename, 'r', encoding='utf-8') as file:
            script_content = file.read()

        # Tạo file tạm thời
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_file:
            temp_file.write(script_content.encode('utf-8'))
            temp_file_path = temp_file.name

        # Chạy file tạm thời
        process = subprocess.Popen(["python", temp_file_path, sdt, str(count)])
    except FileNotFoundError:
        bot.reply_to(message, "Không tìm thấy file.")
    except Exception as e:
        bot.reply_to(message, f"Lỗi xảy ra: {str(e)}")

import subprocess
import tempfile
import os
import time
from datetime import datetime, timedelta
import telebot

last_usage = {}  # Lưu trữ thời gian sử dụng lệnh cuối cùng của mỗi người dùng
bot_active = True  # Trạng thái hoạt động của bot
admin_mode = False  # Chế độ admin

@bot.message_handler(commands=['spamvip'])
def supersms(message):
    user_id = message.from_user.id
    user_first_name = message.from_user.first_name
    user_username = message.from_user.username

    # Tính thời gian kết thúc dự kiến
    end_time = datetime.now() + timedelta(minutes=15)
    formatted_end_time = end_time.strftime("%d/%m/%Y %H:%M:%S")

    current_time = time.time()

    if user_id not in allowed_users:
        bot.reply_to(message, 'Hãy Mua Vip Để Sử Dụng https://t.me/dichcutelegramm 🤙 @dinotool.chỉ 30k/30 ngày sử dụng không giới hạn lượt spam bot hoạt động 24/24⏰⏰⏰')
        return

    if not bot_active:
        msg = bot.reply_to(message, 'Bot hiện đang tắt.')
        time.sleep(10)
        try:
            bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
        except telebot.apihelper.ApiTelegramException as e:
            print(f"Error deleting message: {e}")
        return

    if admin_mode and user_id not in admins:
        msg = bot.reply_to(message, 'có lẽ admin đang fix gì đó hãy đợi xíu')

    if user_id in last_usage and current_time - last_usage[user_id] < 50:
        bot.reply_to(message, f"Vui lòng đợi⏱⏱⏱{50 - (current_time - last_usage[user_id]):.1f} giây trước khi sử dụng lệnh lại.")
        return

    last_usage[user_id] = current_time

    params = message.text.split()[1:]
    if len(params) != 2:
        bot.reply_to(message, " ví dụ 📞 /spamvip 037373737 50")
        return

    sdt, count = params

    if not count.isdigit():
        bot.reply_to(message, "📞 Số lần spam không hợp lệ. Vui lòng chỉ nhập số.")
        return

    count = int(count)

    if count > 100:
        bot.reply_to(message, "📞 /spam sdt số_lần tối đa là 30 - 100, đợi 50 giây để sử dụng lại.")
        return

    if sdt in blacklist:
        bot.reply_to(message, f"Số điện thoại {sdt} đã bị cấm spam.")
        return

    diggory_chat3 = f'''
✅ 𝐓𝐇𝐎̂𝐍𝐆 𝐓𝐈𝐍 𝐒𝐏𝐀𝐌𝐕𝐈𝐏 ✅
━━━━━━━━━━━
👤 Tên telegram: {user_first_name} 
👤 Username: {user_username if user_username else "Không có"} 
🆔 ID: {user_id}
📞 Số điện thoại: {sdt} 

🕒 Thời gian dự kiến kết thúc: {formatted_end_time}
🤖 𝘽𝙊𝙏 𝘽𝙔 :@dinotool
━━━━━━━━━━━
✨ Spam đã được khởi động! Chúng tôi sẽ thông báo khi quá trình spam hoàn tất.
━━━━━━━━━━━
━━━━━━━━━━━
➡️ Để liên hệ admin và xem hướng dẫn Vui lòng gõ /start.

━━━━━━━━━━━
'''

    # Tên file Python trong cùng thư mục
    scripts = ["dec.py", "spam.py"]
    
    try:
        # Kiểm tra và chạy cả hai script
        for script_filename in scripts:
            if os.path.isfile(script_filename):
                with open(script_filename, 'r', encoding='utf-8') as file:
                    script_content = file.read()

                with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_file:
                    temp_file.write(script_content.encode('utf-8'))
                    temp_file_path = temp_file.name

                # Chạy script song song với các tham số
                subprocess.Popen(["python", temp_file_path, sdt, str(count)])
            else:
                bot.reply_to(message, f"Tập tin {script_filename} không tìm thấy.")
                return
        
        bot.send_message(message.chat.id, diggory_chat3)

    except Exception as e:
        bot.reply_to(message, f"Lỗi xảy ra: {str(e)}")

				
import telebot
from gtts import gTTS
import os

@bot.message_handler(commands=['voice'])
def handle_voice(message):
    # Lấy văn bản từ lệnh
    text = ' '.join(message.text.split()[1:])
    if text:
        # Tạo âm thanh từ văn bản
        tts = gTTS(text=text, lang='vi')
        file_path = 'voice.mp3'
        tts.save(file_path)
        
        # Gửi âm thanh tới người dùng
        with open(file_path, 'rb') as voice_file:
            bot.send_voice(chat_id=message.chat.id, voice=voice_file)
        
        # Xóa file âm thanh sau khi gửi
        os.remove(file_path)

        # Trả lời người dùng với nội dung văn bản đã nhập
        bot.reply_to(message, f"Bạn đã yêu cầu chuyển văn bản thành giọng nói: \"{text}\"")
    else:
        bot.reply_to(message, 'Vui lòng cung cấp văn bản sau lệnh /voice')
				
				
@bot.message_handler(commands=['ad'])
def send_admin_info(message):
    bot.send_message(
        message.chat.id, 
        f"Only One => Is : {ADMIN_NAME}\nID: `{ADMIN_ID}`", 
        parse_mode='Markdown'
    )

@bot.message_handler(func=lambda message: message.text.isdigit())
def copy_user_id(message):
    bot.send_message(message.chat.id, f"ID của bạn đã được sao chép: `{message.text}`", parse_mode='Markdown')
ADMIN_NAME = "KhangDino"
@bot.message_handler(commands=['id'])
def get_user_id(message):
    if len(message.text.split()) == 1:  
        user_id = message.from_user.id
        bot.reply_to(message, f"ID của bạn là: `{user_id}`", parse_mode='Markdown')
    else:  
        username = message.text.split('@')[-1].strip()
        try:
            user = bot.get_chat(username)  # Lấy thông tin người dùng từ username
            bot.reply_to(message, f"ID của {user.first_name} là: `{user.id}`", parse_mode='Markdown')
        except Exception as e:
            bot.reply_to(message, "Không tìm thấy người dùng có username này.")
@bot.message_handler(commands=['ID'])
def handle_id_command(message):
    chat_id = message.chat.id
    bot.reply_to(message, f"ID của nhóm này là: {chat_id}")


import time

def restart_program():
    """Khởi động lại script chính và môi trường chạy."""
    python = sys.executable
    script = sys.argv[0]
    # Khởi động lại script chính từ đầu
    try:
        subprocess.Popen([python, script])
    except Exception as e:
        print(f"Khởi động lại không thành công: {e}")
    finally:
        time.sleep(10)  # Đợi một chút để đảm bảo instance cũ đã ngừng hoàn toàn
        sys.exit()
@bot.message_handler(commands=['remove', 'removeuser'])
def remove_user(message):
    admin_id = message.from_user.id
    if admin_id != ADMIN_ID:
        bot.reply_to(message, 'BẠN KHÔNG CÓ QUYỀN SỬ DỤNG LỆNH NÀY')
        return

    if len(message.text.split()) == 1:
        bot.reply_to(message, 'VUI LÒNG NHẬP ID NGƯỜI DÙNG')
        return

    user_id = int(message.text.split()[1])

    if user_id in allowed_users:
        allowed_users.remove(user_id)
        connection = sqlite3.connect('user_data.db')
        remove_user_from_database(connection, user_id)
        connection.close()
        bot.reply_to(message, f'❌ NGƯỜI DÙNG CÓ ID {user_id} ĐÃ BỊ XÓA KHỎI DANH SÁCH VIP')
    else:
        bot.reply_to(message, f'NGƯỜI DÙNG CÓ ID {user_id} KHÔNG CÓ TRONG DANH SÁCH VIP')

def remove_user_from_database(connection, user_id):
    cursor = connection.cursor()
    cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
    connection.commit()
		
@bot.message_handler(commands=['rs'])
def handle_reset(message):
    if message.from_user.id == ADMIN_ID:
        bot.reply_to(message, "Khởi động lại thành công")
        restart_program()
    else:
        bot.reply_to(message, "Bạn không có quyền truy cập vào lệnh này!")
####
@bot.message_handler(commands=['tv'])
def tieng_viet(message):
    chat_id = message.chat.id
    message_id = message.message_id
    
    keyboard = types.InlineKeyboardMarkup()
    url_button = types.InlineKeyboardButton("Tiếng Việt 🇻🇳", url='https://t.me/setlanguage/abcxyz')
    keyboard.add(url_button)
    
    bot.send_message(chat_id, 'Click Vào Nút "<b>Tiếng Việt</b>" để đổi thành tv VN in đờ bét.', reply_markup=keyboard, parse_mode='HTML')
    
    # Delete user's command message
    try:
        bot.delete_message(chat_id, message_id)
    except Exception as e:
        bot.send_message(chat_id, f"Không thể xóa tin nhắn: {e}", parse_mode='HTML')

				
		
# Hàm xử lý lệnh /qr
@bot.message_handler(commands=['qr'])
def generate_qr(message):
    # Lấy nội dung sau lệnh /qr
    text = message.text[4:].strip()
    if not text:
        bot.reply_to(message, 'Vui lòng cung cấp nội dung để tạo mã QR.')
        return

    # Tạo mã QR
    qr = qrcode.make(text)
    bio = io.BytesIO()
    bio.name = 'image.png'
    qr.save(bio, 'PNG')
    bio.seek(0)

    # Gửi ảnh mã QR cho người dùng
    bot.send_photo(message.chat.id, bio)

    # Trả lời người dùng với nội dung đã yêu cầu
    bot.reply_to(message, f"Bạn đã yêu cầu tạo mã QR cho nội dung: {text}")
		
# Xử lý lệnh /face
@bot.message_handler(commands=['face'])
def send_random_face(message):
    # Lấy ảnh từ API
    url = "https://thispersondoesnotexist.com"
    try:
        response = requests.get(url)
        # Kiểm tra nếu phản hồi từ API thành công
        if response.status_code == 200:
            photo = BytesIO(response.content)
            # Gửi ảnh lại cho người dùng
            bot.send_photo(message.chat.id, photo)
            # Trả lời người dùng với nội dung đã yêu cầu
            bot.reply_to(message, "Đây là ảnh khuôn mặt ngẫu nhiên mà bạn đã yêu cầu.")
        else:
            # Thông báo lỗi nếu không lấy được ảnh
            bot.reply_to(message, "Không thể lấy ảnh. Vui lòng thử lại sau.")
    except requests.exceptions.RequestException as e:
        # Xử lý ngoại lệ nếu có lỗi trong quá trình kết nối
        bot.reply_to(message, "Có lỗi xảy ra khi kết nối tới server. Vui lòng thử lại sau.")
        print(f"Error: {e}")
				
if __name__ == "__main__":
    bot_active = True
    bot.infinity_polling()