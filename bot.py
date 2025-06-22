import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Укажи токен своего бота
BOT_TOKEN = "7666621990:AAGxkqd-rMSjzMeEZgCLm_iPU__fBSFf_DE"  # ← замени на свой токен
WEBAPP_URL = "https://calendar-nr7j.onrender.com"  # ← замени на ссылку на свой сайт (мини-приложение)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🗓 Открыть календарь", web_app={'url': WEBAPP_URL})]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Привет! 👋 Это твой календарь настроения.\nНажми кнопку ниже, чтобы начать:",
        reply_markup=reply_markup
    )

# /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧠 Этот бот помогает отслеживать настроение.\n"
        "🗓 Нажми кнопку /start, чтобы открыть календарь.\n"
        "📊 Следи за статистикой и записывай комментарии к каждому дню!"
    )

# Основной запуск
async def setup_bot_commands(application):
    await application.bot.set_my_commands([
        BotCommand("start", "Запустить бота"),
        BotCommand("help", "Помощь по функциям")
    ])

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    app.post_init = setup_bot_commands

    print("✅ Бот запущен.")
    app.run_polling()
