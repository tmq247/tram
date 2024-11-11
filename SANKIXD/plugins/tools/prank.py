import os
import random
import time
from pyrogram import Client, filters
from threading import Timer
from SANKIXD import app

# Environment variables for sensitive data
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client("prank_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Fake Alerts and Messages
fake_alerts = [
    "Warning: Unauthorized login detected! Your account is under observation.",
    "Alert: New login from an unknown device detected. Please verify your identity.",
    "Security Notice: Your account is being accessed from an unusual location. Verify your account immediately.",
    "Error: Multiple failed login attempts detected. Locking your account for security purposes."
]

random_facts = [
    "Did you know? The Eiffel Tower can grow taller during the summer due to thermal expansion.",
    "Fun fact: Honey never spoils! Archaeologists have found pots of honey in ancient tombs that are still edible.",
    "Random Fact: The longest time between two twins being born is 87 days!",
    "Did you know? A group of flamingos is called a 'flamboyance'."
]

jokes = [
    "Why don't skeletons fight each other? They don't have the guts.",
    "I told my wife she was drawing her eyebrows too high. She looked surprised.",
    "Why don’t oysters donate to charity? Because they are shellfish!"
]

# Send random alert or joke/fact
def send_fake_alert(client, message):
    user_id = message.from_user.id
    # Randomly choose to send an alert, fact, or joke
    response_type = random.choice(['alert', 'fact', 'joke'])
    
    if response_type == 'alert':
        alert_message = random.choice(fake_alerts)
        client.send_message(user_id, alert_message)
    elif response_type == 'fact':
        fact_message = random.choice(random_facts)
        client.send_message(user_id, fact_message)
    else:
        joke_message = random.choice(jokes)
        client.send_message(user_id, joke_message)

# Handle /prank command
@app.on_message(filters.command("prank") & filters.private)
def prank(client, message):
    user_id = message.from_user.id
    message.reply_text("Prank started! I'm going to send you some random alerts and messages. Stay tuned...")

    # Random delay before sending each message
    delay = random.randint(3, 10)  # Delay between 3 to 10 seconds
    Timer(delay, send_fake_alert, [client, message]).start()

# Handle /stop command to end prank
@app.on_message(filters.command("stop") & filters.private)
def stop_prank(client, message):
    user_id = message.from_user.id
    message.reply_text("Prank stopped! No more messages coming your way.")
