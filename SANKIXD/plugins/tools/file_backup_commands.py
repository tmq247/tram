"""
File Backup Commands - Commands để quản lý backup ranking data
"""

from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from SANKIXD import app
from SANKIXD.utils.file_ranking_storage import (
    save_ranking_to_file, create_ranking_backup, 
    get_file_storage_info, load_ranking_from_file
)
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from vietnam_timezone_ranking import current_data, get_vietnam_datetime_str
except ImportError:
    # Fallback if import fails
    current_data = {"today": {}, "week": {}, "month": {}, "daily_7days": {}}
    def get_vietnam_datetime_str():
        from datetime import datetime
        import pytz
        return datetime.now(pytz.timezone('Asia/Ho_Chi_Minh')).strftime("%d/%m/%Y %H:%M")

@app.on_message(filters.command("backup"))
async def manual_backup_command(_, message: Message):
    """Tạo backup thủ công cho ranking data"""
    try:
        # Create manual backup
        backup_name = f"manual_backup_{get_vietnam_datetime_str().replace('/', '').replace(':', '').replace(' ', '_')}.json"
        backup_path = await create_ranking_backup(current_data, backup_name)
        
        if backup_path:
            # Save current data to main file
            await save_ranking_to_file(current_data)
            
            # Get file info
            file_info = get_file_storage_info()
            
            response = f"""✅ **BACKUP HOÀN TẤT**

📅 Thời gian: {get_vietnam_datetime_str()}
📁 File backup: `{backup_name}`

**Dữ liệu đã backup:**
📊 Hôm nay: {len(current_data.get('today', {}))} chats
📈 Tuần này: {len(current_data.get('week', {}))} chats  
📉 Tháng này: {len(current_data.get('month', {}))} chats
📋 7 ngày qua: {len(current_data.get('daily_7days', {}))} chats

**Thông tin file:**"""
            
            for name, info in file_info["files"].items():
                if info["exists"]:
                    response += f"\n• {name}: {info['size']} bytes"
            
            response += f"\n\n✅ Dữ liệu được lưu tự động mỗi 30 giây"
            response += f"\n✅ Không mất dữ liệu khi restart bot"
            
            await message.reply_text(response)
        else:
            await message.reply_text("❌ Lỗi tạo backup")
            
    except Exception as e:
        await message.reply_text(f"❌ Lỗi backup: {str(e)}")

@app.on_message(filters.command("restore"))
async def restore_backup_command(_, message: Message):
    """Khôi phục dữ liệu từ backup"""
    try:
        # Load data from file
        saved_data = await load_ranking_from_file()
        
        if saved_data:
            # Count existing data
            old_counts = {
                period: len(current_data.get(period, {}))
                for period in ["today", "week", "month", "daily_7days"]
            }
            
            # Restore data
            for period in ["today", "week", "month", "daily_7days"]:
                if period in saved_data:
                    current_data[period].update(saved_data[period])
            
            # Count restored data
            new_counts = {
                period: len(current_data.get(period, {}))
                for period in ["today", "week", "month", "daily_7days"]
            }
            
            response = f"""✅ **KHÔI PHỤC HOÀN TẤT**

📅 Thời gian: {get_vietnam_datetime_str()}

**Dữ liệu trước khôi phục:**
📊 Hôm nay: {old_counts['today']} chats
📈 Tuần này: {old_counts['week']} chats
📉 Tháng này: {old_counts['month']} chats
📋 7 ngày qua: {old_counts['daily_7days']} chats

**Dữ liệu sau khôi phục:**
📊 Hôm nay: {new_counts['today']} chats
📈 Tuần này: {new_counts['week']} chats
📉 Tháng này: {new_counts['month']} chats
📋 7 ngày qua: {new_counts['daily_7days']} chats

✅ Dữ liệu đã được khôi phục từ file backup"""
            
            await message.reply_text(response)
        else:
            await message.reply_text("📭 Không tìm thấy dữ liệu backup để khôi phục")
            
    except Exception as e:
        await message.reply_text(f"❌ Lỗi khôi phục: {str(e)}")

@app.on_message(filters.command("fileinfo"))
async def file_info_command(_, message: Message):
    """Hiển thị thông tin file backup"""
    try:
        file_info = get_file_storage_info()
        
        response = f"""📁 **THÔNG TIN FILE BACKUP**

📅 Thời gian: {file_info['vietnam_time']}
📂 Thư mục: `{file_info['data_directory']}`

**Trạng thái files:**"""
        
        for name, info in file_info["files"].items():
            if info["exists"]:
                response += f"\n✅ **{name}**"
                response += f"\n   📦 Kích thước: {info['size']} bytes"
                response += f"\n   🕐 Cập nhật: {info['modified']}"
            else:
                response += f"\n❌ **{name}**: Không tồn tại"
        
        response += f"\n\n**Dữ liệu hiện tại:**"
        response += f"\n📊 Hôm nay: {len(current_data.get('today', {}))} chats"
        response += f"\n📈 Tuần này: {len(current_data.get('week', {}))} chats"
        response += f"\n📉 Tháng này: {len(current_data.get('month', {}))} chats"
        response += f"\n📋 7 ngày qua: {len(current_data.get('daily_7days', {}))} chats"
        
        response += f"\n\n🔄 Auto-save: Mỗi 30 giây"
        response += f"\n💾 Backup strategy: File JSON + MongoDB (khi có)"
        
        buttons = [
            [InlineKeyboardButton("🔄 Backup ngay", callback_data="manual_backup")],
            [InlineKeyboardButton("📥 Khôi phục", callback_data="restore_backup")]
        ]
        
        await message.reply_text(
            response, 
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        
    except Exception as e:
        await message.reply_text(f"❌ Lỗi hiển thị thông tin: {str(e)}")

@app.on_callback_query(filters.regex("manual_backup"))
async def manual_backup_callback(_, callback_query):
    """Callback cho backup thủ công"""
    try:
        # Create backup
        backup_name = f"callback_backup_{get_vietnam_datetime_str().replace('/', '').replace(':', '').replace(' ', '_')}.json"
        backup_path = await create_ranking_backup(current_data, backup_name)
        
        if backup_path:
            await save_ranking_to_file(current_data)
            await callback_query.answer("✅ Backup thành công!")
            
            await callback_query.edit_message_text(
                f"✅ **BACKUP HOÀN TẤT**\n\n"
                f"📅 {get_vietnam_datetime_str()}\n"
                f"📁 `{backup_name}`\n\n"
                f"📊 Đã backup {len(current_data.get('today', {}))} chats hôm nay\n"
                f"📈 Đã backup {len(current_data.get('week', {}))} chats tuần này\n"
                f"📉 Đã backup {len(current_data.get('month', {}))} chats tháng này"
            )
        else:
            await callback_query.answer("❌ Lỗi tạo backup!")
            
    except Exception as e:
        await callback_query.answer(f"❌ Lỗi: {str(e)}")

@app.on_callback_query(filters.regex("restore_backup"))
async def restore_backup_callback(_, callback_query):
    """Callback cho khôi phục backup"""
    try:
        saved_data = await load_ranking_from_file()
        
        if saved_data:
            # Restore data
            for period in ["today", "week", "month", "daily_7days"]:
                if period in saved_data:
                    current_data[period].update(saved_data[period])
            
            await callback_query.answer("✅ Khôi phục thành công!")
            
            await callback_query.edit_message_text(
                f"✅ **KHÔI PHỤC HOÀN TẤT**\n\n"
                f"📅 {get_vietnam_datetime_str()}\n\n"
                f"📊 Hôm nay: {len(current_data.get('today', {}))} chats\n"
                f"📈 Tuần này: {len(current_data.get('week', {}))} chats\n"
                f"📉 Tháng này: {len(current_data.get('month', {}))} chats\n"
                f"📋 7 ngày qua: {len(current_data.get('daily_7days', {}))} chats\n\n"
                f"✅ Dữ liệu đã được khôi phục từ file"
            )
        else:
            await callback_query.answer("❌ Không có dữ liệu backup!")
            
    except Exception as e:
        await callback_query.answer(f"❌ Lỗi: {str(e)}")

print("✅ File backup commands loaded")
