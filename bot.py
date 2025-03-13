import telebot
import os
import json

TOKEN = os.getenv("BOT_TOKEN")  # Bot token from GitHub Secrets
ADMIN_IDS = os.getenv("ADMIN_IDS").split(",")  # Multiple admin IDs

bot = telebot.TeleBot(TOKEN)

LOG_FILE = "messages_log.json"

# Load message log
def load_logs():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as file:
            return json.load(file)
    return {}

# Save message log
def save_log(user_id, message):
    logs = load_logs()
    logs[str(user_id)] = message
    with open(LOG_FILE, "w") as file:
        json.dump(logs, file)

# Handle user messages and forward them to admins
@bot.message_handler(func=lambda message: True)
def forward_to_admin(message):
    save_log(message.chat.id, message.text)
    
    keyboard = telebot.types.InlineKeyboardMarkup()
    reply_button = telebot.types.InlineKeyboardButton(text="Reply", callback_data=f"reply_{message.chat.id}")
    keyboard.add(reply_button)

    for admin_id in ADMIN_IDS:
        bot.send_message(admin_id, f"📩 New Message from {message.chat.id}: {message.text}", reply_markup=keyboard)
    
    bot.send_message(message.chat.id, "📨 Your message has been sent to the admin!")

# Handle admin replies
@bot.callback_query_handler(func=lambda call: call.data.startswith("reply_"))
def admin_reply(call):
    user_id = call.data.split("_")[1]
    bot.send_message(call.message.chat.id, f"📝 Reply to user {user_id}:")
    
    @bot.message_handler(func=lambda msg: msg.chat.id == int(call.message.chat.id))
    def send_reply(msg):
        bot.send_message(user_id, f"📬 Admin: {msg.text}")
        bot.send_message(msg.chat.id, "✅ Reply sent successfully!")
        bot.message_handler(None)

# Admin panel for viewing logs
@bot.message_handler(commands=['logs'])
def show_logs(message):
    if str(message.chat.id) not in ADMIN_IDS:
        bot.send_message(message.chat.id, "❌ You are not authorized!")
        return
    
    logs = load_logs()
    log_text = "\n".join([f"{user}: {msg}" for user, msg in logs.items()])
    bot.send_message(message.chat.id, f"📜 Message Logs:\n{log_text}")

bot.polling()
