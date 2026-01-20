import os
from flask import Flask, send_from_directory
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import threading

# --- Flask Server for Streaming ---
app = Flask(__name__)
PORT = int(os.environ.get("PORT", 8080))
# Koyeb URL will be: https://your-app-name.koyeb.app
DOMAIN = os.environ.get("DOMAIN", "https://international-angelia-uhhy5-754bbc99.koyeb.app") 

@app.route('/stream/<filename>')
def stream_video(filename):
    # This serves the video file from the 'downloads' folder
    return send_from_directory('downloads', filename)

@app.route('/')
def health_check():
    return "Bot is running!", 200

# --- Telegram Bot Logic ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a video file, and I'll give you a streaming link!")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video = update.message.video
    file = await context.bot.get_file(video.file_id)
    
    # Save the file locally to serve it
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    
    file_path = f"downloads/{video.file_id}.mp4"
    await file.download_to_drive(file_path)
    
    streaming_link = f"https://{DOMAIN}/stream/{video.file_id}.mp4"
    await update.message.reply_text(f"🎥 Your Video Link:\n{streaming_link}")

def run_flask():
    app.run(host='0.0.0.0', port=PORT)

if __name__ == '__main__':
    # Start Flask in a separate thread so it doesn't block the bot
    threading.Thread(target=run_flask).start()

    # Start the Telegram Bot
    token = os.environ.get("BOT_TOKEN")
    application = ApplicationBuilder().token(token).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))
    
    application.run_polling()
