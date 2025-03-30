import os
import re
from dotenv import load_dotenv
import telebot
import gspread
from google.oauth2.service_account import Credentials

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN")
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")
SPREADSHEET_KEY = os.getenv("SPREADSHEET_KEY")

# Konfigurasi Telegram Bot
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Load kredensial
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)

client = gspread.authorize(creds)
spreadsheet = client.open_by_key(SPREADSHEET_KEY)
sheet = spreadsheet.sheet1 

ALLOWED_USERS = [1403097685]

@bot.message_handler(func=lambda message: message.from_user.id not in ALLOWED_USERS)
def unauthorized_access(message):
    bot.reply_to(message, "🚫 *Maaf, lu gak punya akses ke bot ini!*", parse_mode="Markdown")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message,
        "✅ *Bot To-Do List AI aktif!*\n\n"
        "Kirimkan tugas dalam format:\n"
        "`Judul, Deadline, Deskripsi`\n\n"
        "Contoh:\n"
        "`Tugas AI, deadline 5 April, presentasi proyek`",
        parse_mode="Markdown"
    )
    print("[LOG] Bot telah di-start!")

@bot.message_handler(commands=['id'])
def send_user_id(message):
    user_id = message.from_user.id
    bot.reply_to(message, f"🔍 *ID Telegram kamu:* `{user_id}`", parse_mode="Markdown")

@bot.message_handler(commands=["tasks"])
def get_tasks(message):
    user_id = message.from_user.id
    if user_id not in ALLOWED_USERS:
        bot.reply_to(message, "🚫 Maaf, kamu tidak diizinkan mengakses daftar tugas!")
        return

    tasks = sheet.get_all_values()[1:]
    if not tasks:
        bot.reply_to(message, "📭 Belum ada tugas yang tersimpan!")
    else:
        response = "📋 **Daftar Tugas:**\n\n"
        for idx, (judul, deadline, deskripsi) in enumerate(tasks, start=1):
            response += f"{idx}. **{judul}**\n   🗓 Deadline: {deadline}\n   📌 {deskripsi}\n\n"
        bot.reply_to(message, response, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    user_firstname = message.from_user.first_name
    
    user_input = message.text
    print(f"[LOG] Pesan diterima dari {user_id}: {user_input}")

    task_data = user_input.split(",")

    if len(task_data) == 3:
        task_title, deadline, description = [t.strip() for t in task_data]
        sheet.append_row([task_title, deadline, description])
        
        bot.reply_to(message, f"✅ *Mantap, Bos {user_firstname}!*\nTugas lo udah masuk ke sistem!\n\n📌 *Judul:* {task_title}\n📅 *Deadline:* {deadline}\n📝 *Deskripsi:* {description}\n jangan \
            lupa dikerjain ya bos 😏", parse_mode="Markdown")
    else:
        bot.reply_to(message, "❌ *Format salah, Bos!*\n\nKirim dengan format:\n`Judul, Deadline, Deskripsi`", parse_mode="Markdown")

print("[LOG] Bot berjalan...")
bot.polling()
