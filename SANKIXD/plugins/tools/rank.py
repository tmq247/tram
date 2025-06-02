# Cập nhật hệ thống với múi giờ Việt Nam
from pyrogram import filters
from pymongo import MongoClient
from SANKIXD import app
import config
from pyrogram.types import *
import asyncio
from datetime import datetime, timedelta
import calendar
import pytz
from typing import Dict, List


# Múi giờ Việt Nam
VIETNAM_TZ = pytz.timezone('Asia/Ho_Chi_Minh')

def get_vietnam_time():
    """Get current time in Vietnam timezone"""
    return datetime.now(VIETNAM_TZ)

def get_vietnam_date():
    """Get current date in Vietnam timezone"""
    return get_vietnam_time().date()

def get_vietnam_time_str():
    """Get Vietnam time as formatted string"""
    return get_vietnam_time().strftime("%H:%M")

def get_vietnam_date_str():
    """Get Vietnam date as formatted string"""
    return get_vietnam_time().strftime("%d/%m/%Y")

def get_vietnam_datetime_str():
    """Get Vietnam datetime as formatted string"""
    return get_vietnam_time().strftime("%d/%m/%Y %H:%M")


# MongoDB connection với error handling
try:
    if hasattr(config, 'MONGO_DB_URI') and config.MONGO_DB_URI:
        mongo_client = MongoClient(config.MONGO_DB_URI)
        db = mongo_client["sankirank"]
        collection = db["ranking"]
        history_collection = db["ranking_history"]
        stats_collection = db["chat_stats"]
        print("✅ MongoDB connected for Vietnam timezone ranking system")
    else:
        print("⚠️ MONGO_DB_URI not configured, ranking will use memory only")
        mongo_client = None
        db = None
        collection = None
        history_collection = None
        stats_collection = None
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    mongo_client = None
    db = None
    collection = None
    history_collection = None
    stats_collection = None

# In-memory storage for current period tracking
current_data = {
    "today": {},        # chat_id -> {user_id: {"messages": count, "last_active": vietnam_datetime}}
    "week": {},         # Same structure
    "month": {},        # Same structure
    "daily_7days": {}   # chat_id -> {date_str: {user_id: count}}
}

pic = "https://telegra.ph/file/6589d5e41ccaf809453b7.jpg"


# ------------------- Helper Functions với Vietnam Time ----------------------- #

def get_vietnam_date_key():
    """Get current Vietnam date as string key"""
    return get_vietnam_time().strftime("%Y-%m-%d")

def get_vietnam_week_key():
    """Get current Vietnam week as string key"""
    vn_time = get_vietnam_time()
    year, week, _ = vn_time.isocalendar()
    return f"{year}-W{week:02d}"

def get_vietnam_month_key():
    """Get current Vietnam month as string key"""
    return get_vietnam_time().strftime("%Y-%m")

def get_vietnam_7days_keys():
    """Get list of last 7 days keys in Vietnam timezone"""
    keys = []
    for i in range(7):
        date = get_vietnam_time() - timedelta(days=i)
        keys.append(date.strftime("%Y-%m-%d"))
    return keys

def is_vietnam_midnight():
    """Check if it's midnight in Vietnam"""
    vn_time = get_vietnam_time()
    return vn_time.hour == 0 and vn_time.minute == 0

def is_vietnam_monday_midnight():
    """Check if it's Monday midnight in Vietnam"""
    vn_time = get_vietnam_time()
    return vn_time.weekday() == 0 and vn_time.hour == 0 and vn_time.minute == 0

def is_vietnam_first_day_midnight():
    """Check if it's first day of month midnight in Vietnam"""
    vn_time = get_vietnam_time()
    return vn_time.day == 1 and vn_time.hour == 0 and vn_time.minute == 0

async def save_ranking_snapshot(period_type: str, period_key: str, chat_id: int, data: Dict):
    """Save ranking snapshot to history with Vietnam timezone"""
    try:
        if history_collection is None:
            return
            
        snapshot = {
            "_id": f"{period_type}_{period_key}_{chat_id}",
            "period_type": period_type,  # 'daily', 'weekly', 'monthly'
            "period_key": period_key,
            "chat_id": chat_id,
            "timestamp": get_vietnam_time(),  # Vietnam time
            "vietnam_date": get_vietnam_date_str(),
            "vietnam_time": get_vietnam_time_str(),
            "rankings": data,
            "total_messages": sum(user_data.get("messages", 0) for user_data in data.values()),
            "active_users": len(data),
            "timezone": "Asia/Ho_Chi_Minh"
        }
        
        history_collection.replace_one(
            {"_id": snapshot["_id"]}, 
            snapshot, 
            upsert=True
        )
        print(f"✅ Saved {period_type} snapshot for chat {chat_id} at Vietnam time: {get_vietnam_datetime_str()}")
    except Exception as e:
        print(f"❌ Error saving snapshot: {e}")


# ------------------- Message Watchers với Vietnam Time ----------------------- #

@app.on_message(filters.group, group=7)
async def vietnam_timezone_watcher(_, message):
    """Advanced message tracking for all periods with Vietnam timezone"""
    try:
        if not message.from_user:
            return
            
        chat_id = message.chat.id
        user_id = message.from_user.id
        vn_now = get_vietnam_time()  # Vietnam time
        
        # Update today's data
        if chat_id not in current_data["today"]:
            current_data["today"][chat_id] = {}
        if user_id not in current_data["today"][chat_id]:
            current_data["today"][chat_id][user_id] = {"messages": 0, "last_active": vn_now}
        current_data["today"][chat_id][user_id]["messages"] += 1
        current_data["today"][chat_id][user_id]["last_active"] = vn_now
        
        # Update week's data
        if chat_id not in current_data["week"]:
            current_data["week"][chat_id] = {}
        if user_id not in current_data["week"][chat_id]:
            current_data["week"][chat_id][user_id] = {"messages": 0, "last_active": vn_now}
        current_data["week"][chat_id][user_id]["messages"] += 1
        current_data["week"][chat_id][user_id]["last_active"] = vn_now
        
        # Update month's data
        if chat_id not in current_data["month"]:
            current_data["month"][chat_id] = {}
        if user_id not in current_data["month"][chat_id]:
            current_data["month"][chat_id][user_id] = {"messages": 0, "last_active": vn_now}
        current_data["month"][chat_id][user_id]["messages"] += 1
        current_data["month"][chat_id][user_id]["last_active"] = vn_now
        
        # Update 7-day tracking với Vietnam date
        date_key = get_vietnam_date_key()
        if chat_id not in current_data["daily_7days"]:
            current_data["daily_7days"][chat_id] = {}
        if date_key not in current_data["daily_7days"][chat_id]:
            current_data["daily_7days"][chat_id][date_key] = {}
        if user_id not in current_data["daily_7days"][chat_id][date_key]:
            current_data["daily_7days"][chat_id][date_key][user_id] = 0
        current_data["daily_7days"][chat_id][date_key][user_id] += 1
        
        # Update global stats in MongoDB với Vietnam time
        try:
            if collection is not None:
                collection.update_one(
                    {"_id": user_id}, 
                    {
                        "$inc": {"total_messages": 1},
                        "$set": {
                            "last_active": vn_now,
                            "last_active_vietnam": get_vietnam_datetime_str(),
                            "username": message.from_user.username or ""
                        }
                    }, 
                    upsert=True
                )
        except Exception as e:
            print(f"Error updating MongoDB stats: {e}")
            
    except Exception as e:
        print(f"Error in vietnam_timezone_watcher: {e}")


# ------------------- Ranking Commands với Vietnam Time ----------------------- #

@app.on_message(filters.command(["today", "topngay"]))
async def vietnam_today_ranking(_, message):
    """Show today's ranking with Vietnam timezone"""
    try:
        chat_id = message.chat.id
        today_data = current_data["today"].get(chat_id, {})
        
        if not today_data:
            await message.reply_text("📭 **Hôm nay chưa có tin nhắn nào trong chat này.**")
            return
        
        # Sort users by message count
        sorted_users = sorted(
            today_data.items(), 
            key=lambda x: x[1]["messages"], 
            reverse=True
        )[:10]
        
        vn_date_str = get_vietnam_date_str()
        vn_time_str = get_vietnam_time_str()
        response = f"**📅 BXH HÔM NAY**\n**{vn_date_str}** • 🕐 {vn_time_str}\n\n"
        
        rank_emojis = ["🥇", "🥈", "🥉"] + ["🏅"] * 7
        
        for idx, (user_id, user_data) in enumerate(sorted_users):
            try:
                user = await app.get_users(user_id)
                user_name = user.first_name[:15] if user.first_name else "Unknown"
            except:
                user_name = "Unknown"
            
            emoji = rank_emojis[idx] if idx < len(rank_emojis) else "🏅"
            # Convert last_active to Vietnam time string
            if isinstance(user_data["last_active"], datetime):
                if user_data["last_active"].tzinfo is None:
                    # If no timezone, assume it's Vietnam time
                    last_active = user_data["last_active"].strftime("%H:%M")
                else:
                    # Convert to Vietnam time
                    vn_time = user_data["last_active"].astimezone(VIETNAM_TZ)
                    last_active = vn_time.strftime("%H:%M")
            else:
                last_active = "N/A"
                
            response += f"{emoji} **{idx+1}.** {user_name}\n"
            response += f"   💬 `{user_data['messages']}` tin nhắn • 🕐 {last_active}\n\n"
        
        buttons = [
            [InlineKeyboardButton("📊 Tuần này", callback_data="week_ranking")],
            [InlineKeyboardButton("📈 Tháng này", callback_data="month_ranking")],
            [InlineKeyboardButton("📋 7 ngày qua", callback_data="week_history")]
        ]
        
        await message.reply_photo(
            photo=pic, 
            caption=response, 
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        
    except Exception as e:
        await message.reply_text(f"❌ **Lỗi:** {str(e)}")


@app.on_message(filters.command(["week", "toptuan"]))
async def vietnam_week_ranking(_, message):
    """Show this week's ranking with Vietnam timezone"""
    try:
        chat_id = message.chat.id
        week_data = current_data["week"].get(chat_id, {})
        
        if not week_data:
            await message.reply_text("📭 **Tuần này chưa có tin nhắn nào trong chat này.**")
            return
        
        sorted_users = sorted(
            week_data.items(), 
            key=lambda x: x[1]["messages"], 
            reverse=True
        )[:10]
        
        week_key = get_vietnam_week_key()
        vn_time_str = get_vietnam_time_str()
        response = f"**📊 BXH TUẦN NÀY**\n**{week_key}** • 🕐 {vn_time_str}\n\n"
        
        rank_emojis = ["🥇", "🥈", "🥉"] + ["🏅"] * 7
        
        for idx, (user_id, user_data) in enumerate(sorted_users):
            try:
                user = await app.get_users(user_id)
                user_name = user.first_name[:15] if user.first_name else "Unknown"
            except:
                user_name = "Unknown"
            
            emoji = rank_emojis[idx] if idx < len(rank_emojis) else "🏅"
            # Convert to Vietnam time
            if isinstance(user_data["last_active"], datetime):
                if user_data["last_active"].tzinfo is None:
                    last_active = user_data["last_active"].strftime("%d/%m %H:%M")
                else:
                    vn_time = user_data["last_active"].astimezone(VIETNAM_TZ)
                    last_active = vn_time.strftime("%d/%m %H:%M")
            else:
                last_active = "N/A"
                
            response += f"{emoji} **{idx+1}.** {user_name}\n"
            response += f"   💬 `{user_data['messages']}` tin nhắn • 🕐 {last_active}\n\n"
        
        buttons = [
            [InlineKeyboardButton("📅 Hôm nay", callback_data="today_ranking")],
            [InlineKeyboardButton("📈 Tháng này", callback_data="month_ranking")]
        ]
        
        await message.reply_photo(
            photo=pic, 
            caption=response, 
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        
    except Exception as e:
        await message.reply_text(f"❌ **Lỗi:** {str(e)}")


@app.on_message(filters.command(["month", "topthang"]))  
async def vietnam_month_ranking(_, message):
    """Show this month's ranking with Vietnam timezone"""
    try:
        chat_id = message.chat.id
        month_data = current_data["month"].get(chat_id, {})
        
        if not month_data:
            await message.reply_text("📭 **Tháng này chưa có tin nhắn nào trong chat này.**")
            return
        
        sorted_users = sorted(
            month_data.items(), 
            key=lambda x: x[1]["messages"], 
            reverse=True
        )[:10]
        
        # Get Vietnam month name in Vietnamese
        vn_time = get_vietnam_time()
        month_names = {
            1: "Tháng 1", 2: "Tháng 2", 3: "Tháng 3", 4: "Tháng 4",
            5: "Tháng 5", 6: "Tháng 6", 7: "Tháng 7", 8: "Tháng 8",
            9: "Tháng 9", 10: "Tháng 10", 11: "Tháng 11", 12: "Tháng 12"
        }
        month_name = f"{month_names[vn_time.month]} {vn_time.year}"
        vn_time_str = get_vietnam_time_str()
        
        response = f"**📈 BXH THÁNG NÀY**\n**{month_name}** • 🕐 {vn_time_str}\n\n"
        
        rank_emojis = ["🥇", "🥈", "🥉"] + ["🏅"] * 7
        
        for idx, (user_id, user_data) in enumerate(sorted_users):
            try:
                user = await app.get_users(user_id)
                user_name = user.first_name[:15] if user.first_name else "Unknown"
            except:
                user_name = "Unknown"
            
            emoji = rank_emojis[idx] if idx < len(rank_emojis) else "🏅"
            # Convert to Vietnam time
            if isinstance(user_data["last_active"], datetime):
                if user_data["last_active"].tzinfo is None:
                    last_active = user_data["last_active"].strftime("%d/%m %H:%M")
                else:
                    vn_time = user_data["last_active"].astimezone(VIETNAM_TZ)
                    last_active = vn_time.strftime("%d/%m %H:%M")
            else:
                last_active = "N/A"
                
            response += f"{emoji} **{idx+1}.** {user_name}\n"
            response += f"   💬 `{user_data['messages']}` tin nhắn • 🕐 {last_active}\n\n"
        
        buttons = [
            [InlineKeyboardButton("📅 Hôm nay", callback_data="today_ranking")],
            [InlineKeyboardButton("📊 Tuần này", callback_data="week_ranking")]
        ]
        
        await message.reply_photo(
            photo=pic, 
            caption=response, 
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        
    except Exception as e:
        await message.reply_text(f"❌ **Lỗi:** {str(e)}")


@app.on_message(filters.command("7ngay"))
async def vietnam_seven_days_ranking(_, message):
    """Show 7 days detailed history with Vietnam timezone"""
    try:
        chat_id = message.chat.id
        seven_days_data = current_data["daily_7days"].get(chat_id, {})
        
        if not seven_days_data:
            await message.reply_text("📭 **Không có dữ liệu 7 ngày.**")
            return
        
        vn_time_str = get_vietnam_time_str()
        response = f"**📋 CHI TIẾT 7 NGÀY QUA**\n🕐 {vn_time_str}\n\n"
        
        # Vietnamese day names
        day_names_vn = {
            0: "T2", 1: "T3", 2: "T4", 3: "T5", 4: "T6", 5: "T7", 6: "CN"
        }
        
        for i, date_key in enumerate(get_vietnam_7days_keys()):
            day_data = seven_days_data.get(date_key, {})
            if not day_data:
                continue
                
            # Get top 3 for each day
            sorted_day_users = sorted(
                day_data.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:3]
            
            # Convert to Vietnam date
            date_obj = datetime.strptime(date_key, "%Y-%m-%d")
            vn_date_obj = VIETNAM_TZ.localize(date_obj)
            day_name = day_names_vn[vn_date_obj.weekday()]
            day_str = vn_date_obj.strftime(f"{day_name} %d/%m")
            total_msgs = sum(day_data.values())
            
            response += f"**{day_str}** • `{total_msgs}` tin nhắn\n"
            
            for idx, (user_id, msg_count) in enumerate(sorted_day_users):
                try:
                    user = await app.get_users(user_id)
                    user_name = user.first_name[:12] if user.first_name else "Unknown"
                except:
                    user_name = "Unknown"
                
                medal = ["🥇", "🥈", "🥉"][idx] if idx < 3 else "🏅"
                response += f"  {medal} {user_name} (`{msg_count}`)\n"
            response += "\n"
        
        buttons = [
            [InlineKeyboardButton("📅 Hôm nay", callback_data="today_ranking")],
            [InlineKeyboardButton("📋 Lịch sử chat", callback_data="chat_history")]
        ]
        
        await message.reply_text(response, reply_markup=InlineKeyboardMarkup(buttons))
        
    except Exception as e:
        await message.reply_text(f"❌  **Lỗi:** {str(e)}")

#@app.on_message(filters.command("7ngay"))
async def vietnam_seven_days_ranking1(_, message):
    """Show 7 days detailed history with Vietnam timezone"""
    try:
        chat_id = query.message.chat.id
        seven_days_data = current_data["daily_7days"].get(chat_id, {})
        
        if not seven_days_data:
            await query.message.reply_text("📭 **Không có dữ liệu 7 ngày.**")
            return
        
        vn_time_str = get_vietnam_time_str()
        response = f"**📋 CHI TIẾT 7 NGÀY QUA**\n🕐 {vn_time_str}\n\n"
        
        # Vietnamese day names
        day_names_vn = {
            0: "T2", 1: "T3", 2: "T4", 3: "T5", 4: "T6", 5: "T7", 6: "CN"
        }
        
        for i, date_key in enumerate(get_vietnam_7days_keys()):
            day_data = seven_days_data.get(date_key, {})
            if not day_data:
                continue
                
            # Get top 3 for each day
            sorted_day_users = sorted(
                day_data.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:3]
            
            # Convert to Vietnam date
            date_obj = datetime.strptime(date_key, "%Y-%m-%d")
            vn_date_obj = VIETNAM_TZ.localize(date_obj)
            day_name = day_names_vn[vn_date_obj.weekday()]
            day_str = vn_date_obj.strftime(f"{day_name} %d/%m")
            total_msgs = sum(day_data.values())
            
            response += f"**{day_str}** • `{total_msgs}` tin nhắn\n"
            
            for idx, (user_id, msg_count) in enumerate(sorted_day_users):
                try:
                    user = await app.get_users(user_id)
                    user_name = user.first_name[:12] if user.first_name else "Unknown"
                except:
                    user_name = "Unknown"
                
                medal = ["🥇", "🥈", "🥉"][idx] if idx < 3 else "🏅"
                response += f"  {medal} {user_name} (`{msg_count}`)\n"
            response += "\n"
        
        buttons = [
            [InlineKeyboardButton("📅 Hôm nay", callback_data="today_ranking")],
            [InlineKeyboardButton("📋 Lịch sử chat", callback_data="chat_history")]
        ]
        
        await message.reply_text(response, reply_markup=InlineKeyboardMarkup(buttons))
        
    except Exception as e:
        await query.message.reply_text(f"❌  **Lỗi:** {str(e)}")

@app.on_message(filters.command(["time", "vietnam", "vntime"]))
async def vietnam_time_info(_, message):
    """Show current Vietnam time information"""
    try:
        vn_time = get_vietnam_time()
        
        # Vietnamese day names
        day_names_vn = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ nhật"]
        day_name = day_names_vn[vn_time.weekday()]
        
        # Month names in Vietnamese
        month_names = {
            1: "Tháng 1", 2: "Tháng 2", 3: "Tháng 3", 4: "Tháng 4",
            5: "Tháng 5", 6: "Tháng 6", 7: "Tháng 7", 8: "Tháng 8",
            9: "Tháng 9", 10: "Tháng 10", 11: "Tháng 11", 12: "Tháng 12"
        }
        
        response = f"""**🇻🇳 THỜI GIAN VIỆT NAM**

**📅 Ngày:** {day_name}, {vn_time.day} {month_names[vn_time.month]} {vn_time.year}
**🕐 Giờ:** {vn_time.strftime("%H:%M:%S")}
**🌏 Múi giờ:** UTC+7 (Asia/Ho_Chi_Minh)

**📊 Thông tin chu kỳ:**
• Tuần: {get_vietnam_week_key()}
• Tháng: {get_vietnam_month_key()}
• Ngày: {get_vietnam_date_key()}

**⏰ Bot hoạt động theo giờ Việt Nam**
• Reset hàng ngày: 00:00 VN
• Reset hàng tuần: Thứ 2, 00:00 VN  
• Reset hàng tháng: Ngày 1, 00:00 VN """
        
        await message.reply_text(response)
        
    except Exception as e:
        await message.reply_text(f"❌ **Lỗi:** {str(e)}")


# ------------------- Auto Reset Functions với Vietnam Time ----------------------- #

async def vietnam_daily_reset():
    """Reset daily stats and save snapshot - Vietnam timezone"""
    try:
        print(f"🔄 Starting daily reset at Vietnam time: {get_vietnam_datetime_str()}")
        date_key = get_vietnam_date_key()
        
        # Save today's data to history
        for chat_id, user_data in current_data["today"].items():
            if user_data:  # Only save if there's data
                await save_ranking_snapshot("daily", date_key, chat_id, user_data)
        
        # Clear today's data
        current_data["today"].clear()
        
        # Clean old 7-day data (keep only last 7 days)
        seven_days_keys = set(get_vietnam_7days_keys())
        for chat_id in current_data["daily_7days"]:
            dates_to_remove = []
            for date_key in current_data["daily_7days"][chat_id]:
                if date_key not in seven_days_keys:
                    dates_to_remove.append(date_key)
            for date_key in dates_to_remove:
                del current_data["daily_7days"][chat_id][date_key]
        
        print(f"✅ Daily reset completed at Vietnam time: {get_vietnam_datetime_str()}")
        
    except Exception as e:
        print(f"❌ Error in Vietnam daily reset: {e}")


async def vietnam_weekly_reset():
    """Reset weekly stats and save snapshot - Vietnam timezone"""
    try:
        print(f"🔄 Starting weekly reset at Vietnam time: {get_vietnam_datetime_str()}")
        week_key = get_vietnam_week_key()
        
        # Save this week's data to history
        for chat_id, user_data in current_data["week"].items():
            if user_data:  # Only save if there's data
                await save_ranking_snapshot("weekly", week_key, chat_id, user_data)
        
        # Clear week's data
        current_data["week"].clear()
        print(f"✅ Weekly reset completed at Vietnam time: {get_vietnam_datetime_str()}")
        
    except Exception as e:
        print(f"❌ Error in Vietnam weekly reset: {e}")


async def vietnam_monthly_reset():
    """Reset monthly stats and save snapshot - Vietnam timezone"""
    try:
        print(f"🔄 Starting monthly reset at Vietnam time: {get_vietnam_datetime_str()}")
        month_key = get_vietnam_month_key()
        
        # Save this month's data to history
        for chat_id, user_data in current_data["month"].items():
            if user_data:  # Only save if there's data
                await save_ranking_snapshot("monthly", month_key, chat_id, user_data)
        
        # Clear month's data
        current_data["month"].clear()
        print(f"✅ Monthly reset completed at Vietnam time: {get_vietnam_datetime_str()}")
        
    except Exception as e:
        print(f"❌ Error in Vietnam monthly reset: {e}")


# ------------------- Vietnam Timezone Scheduler ----------------------- #

async def vietnam_scheduler():
    """Main scheduler for auto resets - Vietnam timezone"""
    print(f"🕐 Vietnam timezone scheduler started at {get_vietnam_datetime_str()}")
    
    while True:
        try:
            # Check every 30 seconds for Vietnam midnight
            if is_vietnam_midnight():
                await vietnam_daily_reset()
                
                # Check for weekly reset (Monday midnight Vietnam time)
                if is_vietnam_monday_midnight():
                    await vietnam_weekly_reset()
                
                # Check for monthly reset (1st day of month Vietnam time)
                if is_vietnam_first_day_midnight():
                    await vietnam_monthly_reset()
                
                # Sleep for 60 seconds to avoid multiple triggers
                await asyncio.sleep(60)
            
            # Sleep for 30 seconds before next check
            await asyncio.sleep(30)
            
        except Exception as e:
            print(f"❌ Error in Vietnam scheduler: {e}")
            await asyncio.sleep(60)


# ------------------- Callback Handlers ----------------------- #

@app.on_callback_query(filters.regex("today_ranking"))
async def cb_vietnam_today_ranking(_, query):
    """Callback for today's ranking"""
    message = query.message
    await vietnam_today_ranking(_, message)


@app.on_callback_query(filters.regex("week_ranking"))
async def cb_vietnam_week_ranking(_, query):
    """Callback for week's ranking"""
    message = query.message
    await vietnam_week_ranking(_, message)


@app.on_callback_query(filters.regex("month_ranking"))
async def cb_vietnam_month_ranking(_, query):
    """Callback for month's ranking"""
    message = query.message
    await vietnam_month_ranking(_, message)


@app.on_callback_query(filters.regex("week_history"))
async def cb_vietnam_week_history(_, query):
    """Callback for 7 days history"""
    message = query.message
    await vietnam_seven_days_ranking(_, query)


# Initialize file-based storage as backup
async def init_file_backup_system():
    """Initialize file backup system for ranking data"""
    try:
        from SANKIXD.utils.file_ranking_storage import load_ranking_from_file, start_file_auto_save
        
        # Load existing data from file
        saved_data = await load_ranking_from_file()
        if saved_data:
            # Merge saved data with current data
            for period in ["today", "week", "month", "daily_7days"]:
                if period in saved_data:
                    current_data[period].update(saved_data[period])
            print(f"✅ Restored ranking data from file backup")
        
        # Start auto-save to file
        start_file_auto_save(current_data)
        
    except Exception as e:
        print(f"⚠️ File backup system error: {e}")

# Initialize file backup system
asyncio.create_task(init_file_backup_system())

# Start Vietnam timezone scheduler
asyncio.create_task(vietnam_scheduler())

print(f"✅ Vietnam timezone ranking system loaded at {get_vietnam_datetime_str()}")
