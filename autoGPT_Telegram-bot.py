# Import and run Flask to keep Render alive
from keep_alive import keep_alive
keep_alive()

import os
import pickle
import openai
import telebot
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get keys from environment
openai.api_key = os.getenv("openai_key")
telegram_key = os.getenv("telegram_key")

# Validate Telegram key format
if not telegram_key or ":" not in telegram_key:
    raise ValueError("TELEGRAM API KEY is missing or invalid (should contain ':')")

bot = telebot.TeleBot(telegram_key)

# OpenAI response generation
def Generate_Response(prompt):
    try:
        completion = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=150
        )
        message = completion.choices[0].text.lstrip()
        return message
    except Exception as e:
        print("OpenAI Error:", e)
        return "OpenAI server encountered a real-time problem. Please try again later."

# Handle voice messages
@bot.message_handler(content_types=['voice'])
def voice_processing(message):
    bot.reply_to(message, "Sorry, I can't handle voice messages yet. I'm still learning!")

# Handle all other text messages
@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    username = message.from_user.username or str(message.from_user.id)
    history_file = f'prompt_history/{username}'

    try:
        prompt_history = pickle.load(open(history_file, 'rb'))
    except:
        prompt_history = ""

    user_input = message.text
    temp = prompt_history + "\nUser: " + user_input
    response = Generate_Response(temp)

    if response:
        response = response.replace("Ai: ", "").lstrip()
        bot.reply_to(message, response)
        prompt_history += f'\nUser: {user_input}\nAi: {response}'

    # Save updated history
    os.makedirs('prompt_history', exist_ok=True)
    with open(history_file, "wb") as f:
        pickle.dump(prompt_history, f)

# Start the bot
print("Bot is running...")
bot.infinity_polling()
