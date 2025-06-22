from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Нажми кнопку ниже, чтобы открыть календарь настроения ⬇️")

# /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Это бот для отслеживания настроения. Используй кнопки, чтобы открыть календарь, статистику и очистить данные.")

# и так далее...

app = ApplicationBuilder().token("YOUR_BOT_TOKEN").build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
