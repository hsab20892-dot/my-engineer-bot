import logging
import asyncio
import os
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from youtubesearchpython import VideosSearch
import google.generativeai as genai

# ==========================================
# 1. إعدادات السيرفر الوهمي (لإبقاء البوت حياً)
# ==========================================
app = Flask('')

@app.route('/')
def home():
    return "I am alive! Bot is running..."

def run_http():
    # Render يعطينا رقم البورت في متغير البيئة PORT
    # إذا لم نجده نستخدم 8080
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_http)
    t.start()

# ==========================================
# 2. إعدادات البوت
# ==========================================
# سنستخدم متغيرات البيئة لاحقاً للأمان، لكن الآن ضع مفاتيحك هنا مباشرة
TELEGRAM_TOKEN = "8439189368:AAFop6SsPM3QIg0IJ7ZVkBYaykulVcivFiI"
GOOGLE_API_KEY = "AIzaSyAWDygdWRhqQlCOr5fBF7IMUqpEMA_QOsc"

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.ERROR
)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    text = update.message.text
    user_name = update.message.from_user.first_name
    
    # تحية
    if "صباح الخير" in text:
        await update.message.reply_text(f"صباح النور يا {user_name} 🌹")
        return

    # يوتيوب
    if "يوتيوب" in text or "فيديو" in text:
        try:
            query = text.replace("يوتيوب", "").replace("فيديو", "").strip()
            if not query: return
            msg = await update.message.reply_text(f"🔎 {query}...")
            search = VideosSearch(query, limit=1)
            result = search.result()
            if result['result']:
                await update.message.reply_text(result['result'][0]['link'])
                await context.bot.delete_message(chat_id=update.message.chat_id, message_id=msg.message_id)
            else:
                await update.message.reply_text("ما لقيت شي.")
        except: pass
        return

    # ذكاء اصطناعي
    try:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
        response = model.generate_content(text)
        if response.text:
            await update.message.reply_text(f"💡 **المهندس:**\n{response.text}", parse_mode='Markdown')
        else:
            await update.message.reply_text("ما عندي رد.")
    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text("حدث خطأ في الاتصال.")

if __name__ == '__main__':
    # تشغيل السيرفر الوهمي في الخلفية
    keep_alive()
    
    # تشغيل البوت
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    message_handler = MessageHandler(filters.TEXT, handle_message)
    application.add_handler(message_handler)
    print("Bot is running on Render...")
    application.run_polling()