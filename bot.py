import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Enter your bot's token
BOT_TOKEN = "******"  
WEBAPP_URL = "*****"  # ← replace with a link to your website (mini-app)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🗓 Открыть календарь", web_app={'url': WEBAPP_URL})]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Hi! 👋 This is your mood calendar. Click the button below to get started:",
        reply_markup=reply_markup
    )

# /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧠 This bot helps you track your mood.\n"
        "🗓 Press the /start button to open the calendar.\n"
        "📊 Track your stats and write comments for each day!"
    )

# Main launch
async def setup_bot_commands(application):
    await application.bot.set_my_commands([
        BotCommand("start", "Launch the bot"),
        BotCommand("help", "Help with functions")
    ])

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    app.post_init = setup_bot_commands

    print("✅ Bot starts.")
    app.run_polling()
