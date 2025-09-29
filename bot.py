import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# 🔑 Your credentials
PLANT_ID_API_KEY = "QLlJESkkmrWOnAQB0tb9uAboCV6ZWriav19kj58aSfFRFXWVrg"
TELEGRAM_BOT_TOKEN = "8492265073:AAGZbhb-MACZlBJJUfdcoonfh7WE5XBknIk"

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text("📸 تصویر موصول ہو گئی! بیماری کی جانچ جاری ہے... (20-30 سیکنڈ)")

    try:
        # Get the highest resolution photo
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        file_url = file.file_path  # Telegram gives direct URL

        # Call Plant.id API
        response = requests.post(
            "https://api.plant.id/v2/identify",
            json={
                "images": [file_url],
                "language": "ur",  # Urdu responses!
                "disease_details": True,
                "similar_images": False
            },
            headers={"Api-Key": PLANT_ID_API_KEY}
        )

        data = response.json()

        if "suggestions" not in data or not data["suggestions"]:
            await update.message.reply_text("❌ بیماری کی نشاندہی نہیں ہو سکی۔ براہ کرم واضح تصویر بھیجیں۔")
            return

        # Get top suggestion
        suggestion = data["suggestions"][0]
        disease_name = suggestion["name"]
        probability = suggestion["probability"]
        treatment = suggestion.get("description", "علاج کی تفصیل دستیاب نہیں۔")

        # Format Urdu response
        msg = (
            f"🚨 تشخیص: *{disease_name}*\n"
            f"✅ اعتماد: {round(probability * 100, 1)}%\n\n"
            f"💡 علاج:\n{treatment}\n\n"
            f"ℹ️ نوٹ: یہ مشورہ AI پر مبنی ہے۔ شدید صورتحال میں مقامی ایگری آفس سے رابطہ کریں۔"
        )

        await update.message.reply_text(msg, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("⚠️ سسٹم میں خرابی آ گئی۔ براہ کرم دوبارہ کوشش کریں یا تصویر دوبارہ بھیجیں۔")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌾 *سمارٹ ایگری ایڈوائزر میں خوش آمدید!*\n\n"
        "📸 اپنے فصل کی بیماری کی تشخیص کے لیے صرف ایک تصویر بھیجیں!\n"
        "ہم آپ کو فوری مشورہ اردو میں دیں گے۔",
        parse_mode="Markdown"
    )

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, start))
    app.add_handler(MessageHandler(filters.COMMAND, start))
    logger.info("Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
