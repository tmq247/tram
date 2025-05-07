from pyrogram import filters
from pymongo import MongoClient
from SANKIXD import app
from config import MONGO_DB_URI
from datetime import datetime, timedelta
from pyrogram.types import *


mongo_client = MongoClient(MONGO_DB_URI)
db = mongo_client["sankirank"]
collection = db["ranking"]

user_data = {}

today = {}

pic = "https://telegra.ph/file/6589d5e41ccaf809453b7.jpg"


# ------------------- watcher ----------------------- #

def update_message_count(user_id, chat_id):
    """ Cập nhật số lượng tin nhắn theo tuần/tháng trong MongoDB cho từng nhóm """
    now = datetime.now()
    
    user_data = collection.find_one({"user_id": user_id, "chat_id": chat_id})

    if user_data:
        collection.update_one(
            {"user_id": user_id, "chat_id": chat_id},
            {"$inc": {"weekly_count": 1, "monthly_count": 1}, "$set": {"last_updated": now}}
        )
    else:
        collection.insert_one(
            {"user_id": user_id, "chat_id": chat_id, "weekly_count": 1, "monthly_count": 1, "last_updated": now}
        )

@app.on_message(filters.group & ~filters.bot)
def track_messages(client, message):
    """ Theo dõi tin nhắn mới trong bất kỳ nhóm nào và cập nhật thống kê vào MongoDB """
    update_message_count(message.from_user.id, message.chat.id)

@app.on_message(filters.command("top", prefixes=["/", "!"]) & filters.group)
async def send_top10(client, message):
    """ Gửi danh sách top 10 người nhắn nhiều nhất khi có lệnh /top10 trong nhóm hiện tại """
    chat_id = message.chat.id
    now = datetime.now()

    top_weekly = collection.find({"chat_id": chat_id}).sort("weekly_count", -1).limit(10)
    top_monthly = collection.find({"chat_id": chat_id}).sort("monthly_count", -1).limit(10)

    message_text = "🏆 **Top 10 người nhắn nhiều nhất:**\n\n"
    message_text += "**📅 Trong tuần:**\n" + "\n".join([f"- [{user['user_id']}](tg://user?id={user['user_id']}): {user['weekly_count']} tin nhắn" for user in top_weekly])
    message_text += "\n\n**🗓 Trong tháng:**\n" + "\n".join([f"- [{user['user_id']}](tg://user?id={user['user_id']}): {user['monthly_count']} tin nhắn" for user in top_monthly])

    await app.send_message(message.chat.id, message_text, disable_web_page_preview=True)
