from pyrogram import filters
from pyrogram.types import Message

from SANKIXD import app
from SANKIXD.misc import SUDOERS
from SANKIXD.utils.database import autoend_off, autoend_on


@app.on_message(filters.command("autoend") & SUDOERS)
async def auto_end_stream(_, message: Message):
    usage = "<b>ᴇxᴀᴍᴘʟᴇ :</b>\n\n/autoend [ᴇɴᴀʙʟᴇ | ᴅɪsᴀʙʟᴇ]"
    if len(message.command) != 2:
        return await message.reply_text(usage)
    state = message.text.split(None, 1)[1].strip().lower()
    if state == "enable":
        await autoend_on()
        await message.reply_text(
            "» Tự động kết thúc phát trực tuyến đã được bật.Trợ lý sẽ tự động rời khỏi video chat sau vài phút khi không có ai đang lắng nghe.."
        )
    elif state == "disable":
        await autoend_off()
        await message.reply_text("»Tự động kết thúc đã bị vô hiệu hóa.")
    else:
        await message.reply_text(usage)
