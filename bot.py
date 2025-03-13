import telebot
import os

TOKEN = os.getenv("BOT_TOKEN")  # Get bot token from GitHub secrets
ADMIN_ID = os.getenv("ADMIN_ID")  # Your Telegram user ID

bot = telebot.TeleBot(TOKEN)

# Handle user messages
@bot.message_handler(func=lambda message: True)
def forward_to_admin(message):
    bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
    bot.send_message(message.chat.id, "📩 Your message has been sent to the admin!")

# Handle admin replies
@bot.message_handler(commands=['reply'])
def reply_to_user(message):
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        bot.send_message(message.chat.id, "Usage: /reply <user_id> <message>")
        return
    user_id = args[1]
    reply_text = args[2]
    bot.send_message(user_id, f"📬 Admin: {reply_text}")

bot.polling()
