
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
                                if left >= 20:
                                    break
                                if not await is_active_chat(chat_id):
                                    try:
                                        await client.leave_chat(chat_id)
                                        left += 1
                                        print(f"✅ Left inactive chat: {chat_id}")
                                    except Exception as e:
                                        print(f"⚠️ Failed to leave chat {chat_id}: {e}")
                                        continue
                except Exception as e:
                    print(f"Error in auto_leave for assistant {num}: {e}")
                    pass


asyncio.create_task(auto_leave())


async def auto_end():
    while True:
        await asyncio.sleep(5)
        if not await is_autoend():
            continue
            
        # Tạo copy của keys để tránh RuntimeError
        chat_ids_to_check = list(autoend.keys())
        
        for chat_id in chat_ids_to_check:
            timer = autoend.get(chat_id)
            if not timer:
                continue
                
            if datetime.now() > timer:
                if not await is_active_chat(chat_id):
                    # Xóa chat khỏi autoend nếu không active
                    if chat_id in autoend:
                        del autoend[chat_id]
                    continue
                
                # Xóa chat khỏi autoend trước khi thực hiện các action
                if chat_id in autoend:
                    del autoend[chat_id]
                
                print(f"🕐 Auto ending chat {chat_id}")
                
                try:
                    # Method 1: Sử dụng leave_group_call của py-tgcalls 2.2.1
                    from SANKIXD.core.userbot import assistants
                    from SANKIXD.utils.database import group_assistant
                    
                    # Lấy assistant cho chat này
                    assistant = await group_assistant(SANKI, chat_id)
                    
                    # Dừng stream trước
                    await SANKI.stop_stream(chat_id)
                    await asyncio.sleep(1)
                    
                    # Thử leave group call với py-tgcalls 2.2.1
                    if hasattr(SANKI, 'leave_group_call'):
                        try:
                            await SANKI.leave_group_call(chat_id)
                            print(f"✅ Left group call using leave_group_call: {chat_id}")
                        except Exception as e:
                            print(f"⚠️ leave_group_call failed: {e}")
                            
                            # Fallback: Thử với pytgcalls client trực tiếp
                            try:
                                if hasattr(assistant, 'leave_group_call'):
                                    await assistant.leave_group_call(chat_id)
                                    print(f"✅ Left using assistant.leave_group_call: {chat_id}")
                                elif hasattr(assistant, 'call'):
                                    await assistant.call.leave_group_call(chat_id)
                                    print(f"✅ Left using assistant.call.leave_group_call: {chat_id}")
                            except Exception as e2:
                                print(f"⚠️ Assistant leave failed: {e2}")
                    
                    # Method 2: Force disconnect bằng cách restart pytgcalls cho chat đó
                    elif hasattr(SANKI, 'pytgcalls'):
                        try:
                            await SANKI.pytgcalls.leave_group_call(chat_id)
                            print(f"✅ Left using pytgcalls.leave_group_call: {chat_id}")
                        except Exception as e:
                            print(f"⚠️ pytgcalls leave failed: {e}")
                    
                except Exception as e:
                    print(f"❌ Error leaving voice chat {chat_id}: {e}")
                    continue
                
                try:
                    await app.send_message(
                        chat_id,
                        "» ʙᴏᴛ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ʟᴇғᴛ ᴠɪᴅᴇᴏᴄʜᴀᴛ ʙᴇᴄᴀᴜsᴇ ɴᴏ ᴏɴᴇ ᴡᴀs ʟɪsᴛᴇɴɪɴɢ ᴏɴ ᴠɪᴅᴇᴏᴄʜᴀᴛ.",
                    )
                    print(f"✅ Sent auto-end message to {chat_id}")
                except Exception as e:
                    print(f"⚠️ Failed to send message to {chat_id}: {e}")
                    continue


asyncio.create_task(auto_end())
