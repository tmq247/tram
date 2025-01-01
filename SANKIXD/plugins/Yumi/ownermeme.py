from pyrogram import Client, filters
import requests
from SANKIXD import app 

# Owner ID (replace with the actual owner ID)
OWNER_ID = 7877197608  # Replace with your Telegram user ID

# Define a command handler for the /meme command
@app.on_message(filters.command("memes"))
def meme_command(client, message):
    # Check if the command is sent by the owner
    if message.from_user.id != OWNER_ID:
        message.reply_text("This command is only available for the owner.")
        return

    # API endpoint for random memes
    api_url = "https://meme-api.com/gimme"
    channel_id = "SANKI_MEMES"  # Channel username without '@'

    try:
        # Make a request to the API
        response = requests.get(api_url)
        data = response.json()

        # Extract the meme image URL and title
        meme_url = data.get("url")
        title = data.get("title")

        # Mention the bot username in the caption
        caption = f"{title}\n\nRequest by {message.from_user.mention}\nBot username: @{app.get_me().username}"

        # Send the meme image to the user
        message.reply_photo(
            photo=meme_url,
            caption=caption
        )

        # Forward the same meme image to the channel
        app.send_photo(
            chat_id=f"@{channel_id}",
            photo=meme_url,
            caption=f"{title}\n\nShared via @{app.get_me().username}"
        )

    except Exception as e:
        print(f"Error fetching meme: {e}")
        message.reply_text("Sorry, I couldn't fetch a meme at the moment.")
