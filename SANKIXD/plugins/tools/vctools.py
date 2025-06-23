import asyncio
from typing import Optional
from random import randint
from pyrogram.types import Message, ChatPrivileges
from pyrogram import Client, filters
from pyrogram.raw.functions.channels import GetFullChannel
from pyrogram.raw.functions.messages import GetFullChat
from pyrogram.raw.types import InputGroupCall, InputPeerChannel, InputPeerChat
from SANKIXD.utils.database import *
from pyrogram.raw.functions.phone import CreateGroupCall, DiscardGroupCall
from pyrogram.errors import UserAlreadyParticipant, UserNotParticipant, ChatAdminRequired
from SANKIXD import app, Userbot
from typing import List, Union
from pyrogram import filters
from SANKIXD.core.call import SANKI
from pyrogram.types import VideoChatEnded, Message
from pytgcalls import PyTgCalls

# Import với compatibility checking
try:
    from pytgcalls.types.input_stream import AudioPiped, AudioVideoPiped
    print("✅ New stream types imported in vctools")
except ImportError:
    try:
        from pytgcalls.types import AudioPiped, AudioVideoPiped
        print("✅ Alternative stream types imported in vctools")
    except ImportError:
        AudioPiped = str
        AudioVideoPiped = str
        print("⚠️ Using string fallback in vctools")

try:
    from pytgcalls.exceptions import AlreadyJoined, NotInCall, TelegramServerError
    NoActiveGroupCall = NotInCall
    AlreadyJoinedError = AlreadyJoined
    print("✅ New exceptions imported in vctools")
except ImportError:
    try:
        from pytgcalls.exceptions import NoActiveGroupCall, TelegramServerError, AlreadyJoinedError
        print("✅ Old exceptions imported in vctools")
    except ImportError:
        NoActiveGroupCall = Exception
        TelegramServerError = Exception
        AlreadyJoinedError = Exception
        print("⚠️ Using fallback exceptions in vctools")

async def safe_join_call(assistant, chat_id, audio_path, nt_assistant=None):
    """Safe method to join call with multiple API attempts including nt-calls"""
    # Prepare audio stream
    if AudioPiped != str:
        try:
            stream = AudioPiped(audio_path)
        except:
            stream = audio_path
    else:
        stream = audio_path

    # Try different join methods with py-tgcalls
    join_methods = ["join_group_call", "join_call", "play", "start_call"]

    for method_name in join_methods:
        if hasattr(assistant, method_name):
            try:
                method = getattr(assistant, method_name)
                if method_name == "join_group_call":
                    await method(chat_id, stream)
                else:
                    await method(chat_id, stream)
                return True
            except Exception as e:
                print(f"⚠️ py-tgcalls {method_name} failed: {e}")
                continue

    # Try nt-calls as fallback
    if nt_assistant:
        try:
            from ntgcalls import NTgCalls
            nt_methods = ["join_group_call", "join_call"]

            for method_name in nt_methods:
                if hasattr(nt_assistant, method_name):
                    try:
                        method = getattr(nt_assistant, method_name)
                        await method(chat_id, stream)
                        print(f"✅ nt-calls {method_name} succeeded")
                        return True
                    except Exception as e:
                        print(f"⚠️ nt-calls {method_name} failed: {e}")
                        continue
        except ImportError:
            print("⚠️ nt-calls not available")

    return False

async def safe_leave_call(assistant, chat_id, nt_assistant=None):
    """Safe method to leave call with multiple API attempts including nt-calls"""
    leave_methods = ["leave_group_call", "leave_call", "stop", "disconnect"]

    # Try py-tgcalls methods first
    for method_name in leave_methods:
        if hasattr(assistant, method_name):
            try:
                method = getattr(assistant, method_name)
                await method(chat_id)
                return True
            except Exception as e:
                print(f"⚠️ py-tgcalls {method_name} failed: {e}")
                continue

    # Try nt-calls as fallback
    if nt_assistant:
        try:
            from ntgcalls import NTgCalls
            nt_methods = ["leave_group_call", "leave_call", "stop"]

            for method_name in nt_methods:
                if hasattr(nt_assistant, method_name):
                    try:
                        method = getattr(nt_assistant, method_name)
                        await method(chat_id)
                        print(f"✅ nt-calls {method_name} succeeded")
                        return True
                    except Exception as e:
                        print(f"⚠️ nt-calls {method_name} failed: {e}")
                        continue
        except ImportError:
            print("⚠️ nt-calls not available")

    return False

@app.on_message(filters.command(["vcinfo"], ["/", "!"]))
async def strcall(client, message):
    assistant = await group_assistant(SANKI, message.chat.id)
    try:
        # Try to join call
        joined = await safe_join_call(assistant, message.chat.id, "./SANKIXD/assets/call.mp3")

        if not joined:
            await message.reply("ᴛʜᴇ ᴄᴀʟʟ ɪꜱ ɴᴏᴛ ᴏᴘᴇɴ ᴀᴛ ᴀʟʟ")
            return

        text = "- Beloveds in the call 🫶 :\\n\\n"

        try:
            participants = await assistant.get_participants(message.chat.id)
            k = 0
            for participant in participants:
                info = participant
                if info.muted == False:
                    mut = "ꜱᴘᴇᴀᴋɪɴɢ 🗣 "
                else:
                    mut = "ᴍᴜᴛᴇᴅ 🔕 "
                user = await client.get_users(participant.user_id)
                k += 1
                text += f"{k} ➤ {user.mention} ➤ {mut}\\n"
            text += f"\\nɴᴜᴍʙᴇʀ ᴏꜰ ᴘᴀʀᴛɪᴄɪᴘᴀɴᴛꜱ : {len(participants)}"
        except Exception as e:
            text = f"Error getting participants: {e}"

        await message.reply(f"{text}")
        await asyncio.sleep(7)
        await safe_leave_call(assistant, message.chat.id)

    except Exception as e:
        error_msg = str(e).lower()
        if "no active" in error_msg or "notincall" in error_msg:
            await message.reply(f"ᴛʜᴇ ᴄᴀʟʟ ɪꜱ ɴᴏᴛ ᴏᴘᴇɴ ᴀᴛ ᴀʟʟ")
        elif "telegram server" in error_msg:
            await message.reply(f"ꜱᴇɴᴅ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ ᴀɢᴀɪɴ, ᴛʜᴇʀᴇ ɪꜱ ᴀ ᴘʀᴏʙʟᴇᴍ ᴡɪᴛʜ ᴛʜᴇ ᴛᴇʟᴇɢʀᴀᴍ ꜱᴇʀᴠᴇʀ ❌")
        elif "already joined" in error_msg:
            try:
                text = "ʙᴇʟᴏᴠᴇᴅꜱ ɪɴ ᴛʜᴇ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ 🫶 :\\n\\n"
                participants = await assistant.get_participants(message.chat.id)
                k = 0
                for participant in participants:
                    info = participant
                    if info.muted == False:
                        mut = "ꜱᴘᴇᴀᴋɪɴɢ 🗣"
                    else:
                        mut = "ᴍᴜᴛᴇᴅ 🔕 "
                    user = await client.get_users(participant.user_id)
                    k += 1
                    text += f"{k} ➤ {user.mention} ➤ {mut}\\n"
                text += f"\\nɴᴜᴍʙᴇʀ ᴏꜰ ᴘᴀʀᴛɪᴄɪᴘᴀɴᴛꜱ : {len(participants)}"
                await message.reply(f"{text}")
            except:
                await message.reply("Already in call but couldn't get participants")
        else:
            await message.reply(f"Error: {str(e)}")


other_filters = filters.group  & ~filters.via_bot & ~filters.forwarded
other_filters2 = (
    filters.private  & ~filters.via_bot & ~filters.forwarded
)


def command(commands: Union[str, List[str]]):
    return filters.command(commands, "")


  ################################################
async def get_group_call(
    client: Client, message: Message, err_msg: str = ""
) -> Optional[InputGroupCall]:
    assistant = await get_assistant(message.chat.id)
    chat_peer = await assistant.resolve_peer(message.chat.id)
    if isinstance(chat_peer, (InputPeerChannel, InputPeerChat)):
        if isinstance(chat_peer, InputPeerChannel):
            full_chat = (
                await assistant.invoke(GetFullChannel(channel=chat_peer))
            ).full_chat
        elif isinstance(chat_peer, InputPeerChat):
            full_chat = (
                await assistant.invoke(GetFullChat(chat_id=chat_peer.chat_id))
            ).full_chat
        if full_chat is not None:
            return full_chat.call
    await app.send_message(f"No group ᴠᴏɪᴄᴇ ᴄʜᴀᴛ Found** {err_msg}")
    return False

@app.on_message(filters.command(["vcstart","startvc"], ["/", "!"]))
async def start_group_call(c: Client, m: Message):
    chat_id = m.chat.id
    assistant = await get_assistant(chat_id)
    ass = await assistant.get_me()
    assid = ass.id
    if assistant is None:
        await app.send_message(chat_id, "ᴇʀʀᴏʀ ᴡɪᴛʜ ᴀꜱꜱɪꜱᴛᴀɴᴛ")
        return
    msg = await app.send_message(chat_id, "ꜱᴛᴀʀᴛɪɴɢ ᴛʜᴇ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ..")
    try:

    # Nếu chưa có trong storage, thử lấy thông tin chat để lưu vào storage
        try:
    # Thử resolve_peer từ cache
            peer = await assistant.resolve_peer(chat_id)
        except (KeyError, ValueError):
            try:
        # Lấy thông tin chat từ server
                await assistant.get_chat(chat_id)
                # Thử lại sau khi đã cache
                peer = await assistant.resolve_peer(chat_id)
            except Exception as e:
        # Xử lý fallback nếu vẫn lỗi
                from pyrogram.raw import types
        
                if str(chat_id).startswith("-100"):
            # Xử lý supergroup/channel
                real_id = int(str(chat_id)[4:])
                peer = types.InputPeerChannel(
                channel_id=real_id,
                access_hash=0  # Pyrogram sẽ tự điền
            )
                else:
            # Xử lý chat thường
                peer = types.InputPeerChat(chat_id=chat_id)
        await assistant.invoke(
            CreateGroupCall(
                peer=InputPeerChannel(
                    channel_id=peer.channel_id,
                    access_hash=peer.access_hash,
                ),
                random_id=assistant.rnd_id() // 9000000000,
            )
        )
        await msg.edit_text("ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ꜱᴛᴀʀᴛᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ⚡️~!")
    except ChatAdminRequired:
        try:    
            await app.promote_chat_member(chat_id, assid, privileges=ChatPrivileges(
                #can_manage_chat=False,
                #can_delete_messages=False,
                can_manage_video_chats=True,
                #can_restrict_members=False,
                #can_change_info=False,
                #can_invite_users=False,
                #can_pin_messages=False,
                #can_promote_members=False,
            ),
        )
            await assistant.get_chats(chat_id)
            peer = await assistant.resolve_peer(chat_id)
            await assistant.invoke(
            CreateGroupCall(
                peer=InputPeerChannel(
                    channel_id=peer.channel_id,
                    access_hash=peer.access_hash,
                ),
                random_id=assistant.rnd_id() // 9000000000,
            )
        )
            await app.promote_chat_member(chat_id, assid, privileges=ChatPrivileges(
            #can_manage_chat=False,
            #can_delete_messages=False,
            can_manage_video_chats=False,
            #can_restrict_members=False,
            #can_change_info=False,
            #can_invite_users=False,
            #can_pin_messages=False,
            #can_promote_members=False,
            ),
        )                              
            await msg.edit_text("ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ꜱᴛᴀʀᴛᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ⚡️~!")
        except:
            await msg.edit_text("ɢɪᴠᴇ ᴛʜᴇ ʙᴏᴛ ᴀʟʟ ᴘᴇʀᴍɪꜱꜱɪᴏɴꜱ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ ⚡")

@app.on_message(filters.command(["vcend","endvc"], ["/", "!"]))
async def stop_group_call(c: Client, m: Message):
    chat_id = m.chat.id
    assistant = await get_assistant(chat_id)
    ass = await assistant.get_me()
    assid = ass.id
    if assistant is None:
        await app.send_message(chat_id, "ᴇʀʀᴏʀ ᴡɪᴛʜ ᴀꜱꜱɪꜱᴛᴀɴᴛ")
        return
    msg = await app.send_message(chat_id, "ᴄʟᴏꜱɪɴɢ ᴛʜᴇ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ..")
    try:
        if not (
           group_call := (
               await get_group_call(assistant, m, err_msg=", ɢʀᴏᴜᴘ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴀʟʀᴇᴀᴅʏ ᴇɴᴅᴇᴅ")
           )
        ):  
           return
        await assistant.invoke(DiscardGroupCall(call=group_call))
        await msg.edit_text("ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴄʟᴏꜱᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ⚡️~!")
    except Exception as e:
      if "GROUPCALL_FORBIDDEN" in str(e):
       try:    
         await app.promote_chat_member(chat_id, assid, privileges=ChatPrivileges(
                #can_manage_chat=False,
                #can_delete_messages=False,
                can_manage_video_chats=True,
                #can_restrict_members=False,
                #can_change_info=False,
                #can_invite_users=False,
                #can_pin_messages=False,
                #can_promote_members=False,
             ),
         )
         if not (
           group_call := (
               await get_group_call(assistant, m, err_msg=", ɢʀᴏᴜᴘ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴀʟʀᴇᴀᴅʏ ᴇɴᴅᴇᴅ")
           )
         ):  
           return
         await assistant.invoke(DiscardGroupCall(call=group_call))
         await app.promote_chat_member(chat_id, assid, privileges=ChatPrivileges(
            #can_manage_chat=False,
            #can_delete_messages=False,
            can_manage_video_chats=False,
            #can_restrict_members=False,
            #can_change_info=False,
            #can_invite_users=False,
            #can_pin_messages=False,
            #can_promote_members=False,
            ),
         )                              
         await msg.edit_text("ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴄʟᴏꜱᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ⚡️~!")
       except:
         await msg.edit_text("ɢɪᴠᴇ ᴛʜᴇ ʙᴏᴛ ᴀʟʟ ᴘᴇʀᴍɪꜱꜱɪᴏɴꜱ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ")
