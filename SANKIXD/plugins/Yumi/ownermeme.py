from pyrogram import Client, filters
import requests
from SANKIXD import app
import time
from threading import Thread

# Owner ID (replace with your actual Telegram user ID)
OWNER_ID = 6337933296  # Replace with your Telegram user ID

# Channel username
CHANNEL_USERNAME = "@muoimuoimusicbot
# Global variables for controlling auto-upload
auto_upload = False
uploaded_memes = set()  # To track already uploaded memes

def fetch_meme():
    """Lấy meme từ API."""
    api_url = "https://meme-api.com/gimme"
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            meme_url = data.get("url")
            title = data.get("title")
            return meme_url, title
        else:
            return None, None
    except Exception as e:
        print(f"Lỗi khi tìm nạp meme: {e}")
        return None, None

def auto_upload_memes():
    """Tự động tải meme lên kênh mỗi giờ."""
    global auto_upload
    while auto_upload:
        meme_url, title = fetch_meme()
        if meme_url and meme_url not in uploaded_memes:
            try:
                # Send meme to the channel
                app.send_photo(
                    chat_id=CHANNEL_USERNAME,
                    photo=meme_url,
                    caption=f"{title}\n\nĐược chia sẻ qua @{app.get_me().username}"
                )
                uploaded_memes.add(meme_url)  # Mark meme as uploaded
                print(f"Meme đã tải: {meme_url}")
            except Exception as e:
                print(f"Error uploading meme: {e}")
        else:
            print("Không tìm thấy meme mới hoặc meme trùng lặp.")
        time.sleep(3600)  # Wait for 1 hour

# Command: /meme on
@app.on_message(filters.command("memes") & filters.user(OWNER_ID))
def meme_control(client, message):
    global auto_upload

    # Parse the argument (on/off)
    command_arg = message.text.split(maxsplit=1)[1].lower() if len(message.text.split()) > 1 else None

    if command_arg == "on":
        if not auto_upload:
            auto_upload = True
            message.reply_text("Đã bắt đầu tải meme tự động lên!")
            # Start the auto-uploading thread
            Thread(target=auto_upload_memes).start()
        else:
            message.reply_text("Quá trình tải lên meme tự động đang chạy.")
    elif command_arg == "off":
        if auto_upload:
            auto_upload = False
            message.reply_text("Đã dừng tải meme tự động lên!")
        else:
            message.reply_text("Việc tải lên meme tự động đã bị dừng.")
    else:
        message.reply_text("Cách dùng: /memes on|off")

# Command: /meme (manual meme fetch)
@app.on_message(filters.command("meme") & ~filters.user(OWNER_ID))
def meme_command(client, message):
    # API endpoint for random memes
    meme_url, title = fetch_meme()

    if meme_url:
        caption = f"{title}\n\nYêu cầu bởi {message.from_user.mention}\nBot username: @{app.get_me().username}"
        try:
            # Send the meme to the user
            message.reply_photo(
                photo=meme_url,
                caption=caption
            )
        except Exception as e:
            print(f"Lỗi gửi meme: {e}")
            message.reply_text("Xin lỗi, hiện tại tôi không thể tìm thấy meme.")
    else:
        message.reply_text("Xin lỗi, hiện tại tôi không thể tìm thấy meme.")
