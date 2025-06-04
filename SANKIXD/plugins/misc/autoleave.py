
import asyncio
from datetime import datetime

from pyrogram.enums import ChatType

import config
from SANKIXD import app
from SANKIXD.core.call import SANKI, autoend
from SANKIXD.utils.database import get_client, is_active_chat, is_autoend


async def auto_leave():
    if config.AUTO_LEAVING_ASSISTANT == str(True):
        while True:
            await asyncio.sleep(config.AUTO_LEAVE_ASSISTANT_TIME)
            from SANKIXD.core.userbot import assistants

            for num in assistants:
                client = await get_client(num)
                left = 0
                try:
                    async for i in client.iter_dialogs():
                        chat_type = i.chat.type
                        if chat_type in [
                            "supergroup",
                            "group",
                            "channel",
                        ]:
                            chat_id = i.chat.id
                            if (
                                chat_id != config.LOGGER_ID
                                and i.chat.id != -1001919135283
                                and i.chat.id != -1001841879487
                            ):
                                if left == 20:
                                    continue
                                if not await is_active_chat(chat_id):
                                    try:
                                        await client.leave_chat(
                                            chat_id
                                        )
                                        left += 1
                                    except:
                                        continue
                except:
                    pass


asyncio.create_task(auto_leave())


async def auto_end():
    while True:
        await asyncio.sleep(5)
        if not await is_autoend():
            continue
        # Sử dụng list() để tránh lỗi "dictionary changed size during iteration"
        for chat_id in list(autoend.keys()):
            timer = autoend.get(chat_id)
            if not timer:
                continue
            if datetime.now() > timer:
                if not await is_active_chat(chat_id):
                    if chat_id in autoend:
                        del autoend[chat_id]
                    continue
                
                # Xóa chat_id khỏi autoend trước khi thực hiện cleanup
                if chat_id in autoend:
                    del autoend[chat_id]
                
                try:
                    # Clear queue trước khi stop stream
                    from SANKIXD.misc import db
                    try:
                        # Xóa queue của chat
                        db[chat_id] = []
                    except:
                        pass
                    
                    # Clear current playing song
                    try:
                        from SANKIXD.core.call import queues
                        if chat_id in queues:
                            queues[chat_id].clear()
                    except:
                        pass
                    
                    # Stop stream và leave voice chat
                    await SANKI.stop_stream(chat_id)
                    await asyncio.sleep(1)
                    
                    # Force leave voice chat
                    try:
                        from SANKIXD.utils.database import group_assistant
                        assistant = await group_assistant(SANKI, chat_id)
                        if assistant:
                            # Thử leave group call
                            try:
                                await assistant.leave_group_call(chat_id)
                            except:
                                try:
                                    await assistant.leave_call(chat_id)
                                except:
                                    pass
                    except:
                        pass
                    
                except Exception as e:
                    print(f"Error in auto_end cleanup: {e}")
                    continue
                
                try:
                    await app.send_message(
                        chat_id,
                        "» ʙᴏᴛ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ʟᴇғᴛ ᴠɪᴅᴇᴏᴄʜᴀᴛ ʙᴇᴄᴀᴜsᴇ ɴᴏ ᴏɴᴇ ᴡᴀs ʟɪsᴛᴇɴɪɴɢ ᴏɴ ᴠɪᴅᴇᴏᴄʜᴀᴛ.",
                    )
                except Exception as e:
                    print(f"Error sending auto-end message: {e}")
                    continue


asyncio.create_task(auto_end())
