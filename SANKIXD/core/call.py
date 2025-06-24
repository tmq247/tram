import asyncio
import os
from datetime import datetime, timedelta
from typing import Union

from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup
from pytgcalls import PyTgCalls

# Import với compatibility checking
try:
    from pytgcalls.exceptions import AlreadyJoined, NotInCall, TelegramServerError
    print("✅ New exceptions imported")
except ImportError:
    try:
        from pytgcalls.exceptions import AlreadyJoinedError as AlreadyJoined
        from pytgcalls.exceptions import NoActiveGroupCall as NotInCall
        from pytgcalls.exceptions import TelegramServerError
        print("✅ Old exceptions imported")
    except ImportError:
        AlreadyJoined = Exception
        NotInCall = Exception  
        TelegramServerError = Exception
        print("⚠️ Using generic exceptions")

# Import stream types dengan fallback
try:
    from pytgcalls.types.input_stream import AudioPiped, AudioVideoPiped
    from pytgcalls.types.input_stream.quality import HighQualityAudio, MediumQualityVideo
    print("✅ New stream types imported")
except ImportError:
    try:
        from pytgcalls.types import AudioPiped, AudioVideoPiped, HighQualityAudio, MediumQualityVideo
        print("✅ Alternative stream types imported")
    except ImportError:
        print("⚠️ Creating fallback stream types")
        # Fallback: sử dụng string path trực tiếp
        AudioPiped = str
        AudioVideoPiped = str
        HighQualityAudio = lambda: None
        MediumQualityVideo = lambda: None

# Import other types
try:
    from pytgcalls.types import Update
    from pytgcalls.types.stream import StreamAudioEnded
    print("✅ Update types imported")
except ImportError:
    Update = object
    StreamAudioEnded = object
    print("⚠️ Using fallback update types")

import config
from SANKIXD import LOGGER, YouTube, app
from SANKIXD.misc import db
from SANKIXD.utils.database import (
    add_active_chat,
    add_active_video_chat,
    get_lang,
    get_loop,
    group_assistant,
    is_autoend,
    music_on,
    remove_active_chat,
    remove_active_video_chat,
    set_loop,
)
from SANKIXD.utils.exceptions import AssistantErr
from SANKIXD.utils.formatters import check_duration, seconds_to_min, speed_converter
from SANKIXD.utils.inline.play import stream_markup
from SANKIXD.utils.stream.autoclear import auto_clean
from SANKIXD.utils.thumbnails import get_thumb
from strings import get_string

autoend = {}
counter = {}


async def _clear_(chat_id):
    db[chat_id] = []
    await remove_active_video_chat(chat_id)
    await remove_active_chat(chat_id)


class Call(PyTgCalls):
    def __init__(self):
        self.userbot1 = Client(
            name="SANKIAss1",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING1),
        )
        self.one = PyTgCalls(
            self.userbot1,
            cache_duration=100,
        )
        self.userbot2 = Client(
            name="SANKIAss2",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING2),
        )
        self.two = PyTgCalls(
            self.userbot2,
            cache_duration=100,
        )
        self.userbot3 = Client(
            name="SANKIAss3",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING3),
        )
        self.three = PyTgCalls(
            self.userbot3,
            cache_duration=100,
        )
        self.userbot4 = Client(
            name="SANKIAss4",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING4),
        )
        self.four = PyTgCalls(
            self.userbot4,
            cache_duration=100,
        )
        self.userbot5 = Client(
            name="SANKIAss5",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING5),
        )
        self.five = PyTgCalls(
            self.userbot5,
            cache_duration=100,
        )

    async def call_py_method(self, assistant, method_name, *args, **kwargs):
       # \"\"\"Universal method caller with fallbacks\"\"\"
        methods_to_try = [
            method_name,
            method_name.replace('_', ''),
            f"play_{method_name}",
            f"start_{method_name}",
            f"join_{method_name}",
        ]
        
        for method in methods_to_try:
            if hasattr(assistant, method):
                try:
                    return await getattr(assistant, method)(*args, **kwargs)
                except Exception as e:
                    continue
        
        # Nếu không tìm thấy method nào, thử fallback
        print(f"⚠️ Method {method_name} not found, using fallback")
        return None

    async def pause_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        try:
            await self.call_py_method(assistant, "pause_stream", chat_id)
        except:
            await self.call_py_method(assistant, "pause", chat_id)

    async def resume_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        try:
            await self.call_py_method(assistant, "resume_stream", chat_id)
        except:
            await self.call_py_method(assistant, "resume", chat_id)

    async def stop_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        try:
            await _clear_(chat_id)
            # Thử các method có thể có
            for method in ["leave_group_call", "leave_call", "stop", "disconnect"]:
                if hasattr(assistant, method):
                    await getattr(assistant, method)(chat_id)
                    break
        except:
            pass

    async def stop_stream_force(self, chat_id: int):
        """Force stop với tất cả client cho pytgcalls 2.2.1"""
        print(f"🔨 Force stopping stream in chat {chat_id}")
        
        # Clear data ngay lập tức
        try:
            await _clear_(chat_id)
        except:
            pass
        
        left_successfully = False
        
        # Thử với từng client theo thứ tự
        for i, client in enumerate([self.one, self.two, self.three, self.four, self.five], 1):
            if client and not left_successfully:
                try:
                    # Thử các method leave cho pytgcalls 2.2.1
                    for method in ["leave_group_call", "leave_call", "stop_stream", "stop", "disconnect"]:
                        if hasattr(client, method):
                            try:
                                await getattr(client, method)(chat_id)
                                left_successfully = True
                                print(f"✅ Successfully left chat {chat_id} using client {i} method {method}")
                                break
                            except Exception as e:
                                print(f"⚠️ Client {i} method {method} failed: {e}")
                                continue
                    
                    if left_successfully:
                        break
                        
                except Exception as e:
                    print(f"❌ Client {i} error: {e}")
                    continue
        
        # Cleanup cuối cùng
        try:
            if chat_id in autoend:
                del autoend[chat_id]
            if chat_id in counter:
                del counter[chat_id]
            await remove_active_chat(chat_id)
            await remove_active_video_chat(chat_id)
        except:
            pass
        
        if left_successfully:
            print(f"✅ Force stop completed for chat {chat_id}")
        else:
            print(f"⚠️ Force stop may not have fully completed for chat {chat_id}")
        
        return left_successfully

    def prepare_stream(self, path, is_video=False, additional_params=""):
      #  \"\"\"Prepare stream based on available types\"\"\"
        try:
            if is_video:
                if AudioVideoPiped != str:
                    return AudioVideoPiped(
                        path,
                        audio_parameters=HighQualityAudio(),
                        video_parameters=MediumQualityVideo(),
                        additional_ffmpeg_parameters=additional_params,
                    )
                else:
                    return path  # Fallback to path string
            else:
                if AudioPiped != str:
                    return AudioPiped(
                        path,
                        audio_parameters=HighQualityAudio(),
                        additional_ffmpeg_parameters=additional_params,
                    )
                else:
                    return path  # Fallback to path string
        except:
            return path

    async def join_call(
        self,
        chat_id: int,
        original_chat_id: int,
        link,
        video: Union[bool, str] = None,
        image: Union[bool, str] = None,
    ):
        assistant = await group_assistant(self, chat_id)
        language = await get_lang(chat_id)
        _ = get_string(language)
        
        stream = self.prepare_stream(link, is_video=bool(video))
        
        try:
            # Thử các method join có thể có
            join_methods = [
                "join_group_call",
                "join_call", 
                "play",
                "start_call",
                "start"
            ]
            
            joined = False
            for method_name in join_methods:
                if hasattr(assistant, method_name):
                    try:
                        method = getattr(assistant, method_name)
                        await method(chat_id, stream)
                        joined = True
                        break
                    except Exception as e:
                        print(f"⚠️ {method_name} failed: {e}")
                        continue
            
            if not joined:
                raise AssistantErr("Could not join call - no working method found")
                
        except Exception as e:
            error_msg = str(e).lower()
            if "no active" in error_msg or "notincall" in error_msg:
                raise AssistantErr(_["call_8"])
            elif "already joined" in error_msg or "alreadyjoined" in error_msg:
                raise AssistantErr(_["call_9"])
            elif "telegram server" in error_msg:
                raise AssistantErr(_["call_10"])
            else:
                raise AssistantErr(f"Error joining call: {str(e)}")
            
        await add_active_chat(chat_id)
        await music_on(chat_id)
        if video:
            await add_active_video_chat(chat_id)
        if await is_autoend():
            counter[chat_id] = {}
            try:
                users = len(await assistant.get_participants(chat_id))
                if users == 1:
                    autoend[chat_id] = datetime.now() + timedelta(minutes=1)
            except:
                pass

    async def skip_stream(
        self,
        chat_id: int,
        link: str,
        video: Union[bool, str] = None,
        image: Union[bool, str] = None,
    ):
        assistant = await group_assistant(self, chat_id)
        stream = self.prepare_stream(link, is_video=bool(video))
        
        # Thử các method change stream
        for method_name in ["change_stream", "play", "switch"]:
            if hasattr(assistant, method_name):
                try:
                    await getattr(assistant, method_name)(chat_id, stream)
                    break
                except:
                    continue

    async def seek_stream(self, chat_id, file_path, to_seek, duration, mode):
        assistant = await group_assistant(self, chat_id)
        additional_params = f"-ss {to_seek} -to {duration}"
        stream = self.prepare_stream(file_path, is_video=(mode == "video"), additional_params=additional_params)
        
        for method_name in ["change_stream", "play", "switch"]:
            if hasattr(assistant, method_name):
                try:
                    await getattr(assistant, method_name)(chat_id, stream)
                    break
                except:
                    continue

    async def stream_call(self, link):
        assistant = await group_assistant(self, config.LOGGER_ID)
        stream = self.prepare_stream(link, is_video=True)
        
        try:
            # Join briefly then leave
            for method_name in ["join_group_call", "join_call", "play"]:
                if hasattr(assistant, method_name):
                    await getattr(assistant, method_name)(config.LOGGER_ID, stream)
                    break
            
            await asyncio.sleep(0.2)
            
            for method_name in ["leave_group_call", "leave_call", "stop"]:
                if hasattr(assistant, method_name):
                    await getattr(assistant, method_name)(config.LOGGER_ID)
                    break
        except:
            pass

    async def speedup_stream(self, chat_id: int, file_path, speed, playing):
        assistant = await group_assistant(self, chat_id)
        if str(speed) != str("1.0"):
            base = os.path.basename(file_path)
            chatdir = os.path.join(os.getcwd(), "playback", str(speed))
            if not os.path.isdir(chatdir):
                os.makedirs(chatdir)
            out = os.path.join(chatdir, base)
            if not os.path.isfile(out):
                speed_map = {
                    "0.5": 2.0,
                    "0.75": 1.35,
                    "1.5": 0.68,
                    "2.0": 0.5
                }
                vs = speed_map.get(str(speed), 1.0)
                
                proc = await asyncio.create_subprocess_shell(
                    cmd=(
                        "ffmpeg "
                        "-i "
                        f"{file_path} "
                        "-filter:v "
                        f"setpts={vs}*PTS "
                        "-filter:a "
                        f"atempo={speed} "
                        f"{out}"
                    ),
                    stdin=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                await proc.communicate()
        else:
            out = file_path
            
        dur = await asyncio.get_event_loop().run_in_executor(None, check_duration, out)
        dur = int(dur)
        played, con_seconds = speed_converter(playing[0]["played"], speed)
        duration = seconds_to_min(dur)
        
        additional_params = f"-ss {played} -to {duration}"
        stream = self.prepare_stream(out, is_video=(playing[0]["streamtype"] == "video"), additional_params=additional_params)
            
        if str(db[chat_id][0]["file"]) == str(file_path):
            for method_name in ["change_stream", "play", "switch"]:
                if hasattr(assistant, method_name):
                    try:
                        await getattr(assistant, method_name)(chat_id, stream)
                        break
                    except:
                        continue
        else:
            raise AssistantErr("Umm")
            
        if str(db[chat_id][0]["file"]) == str(file_path):
            exis = (playing[0]).get("old_dur")
            if not exis:
                db[chat_id][0]["old_dur"] = db[chat_id][0]["dur"]
                db[chat_id][0]["old_second"] = db[chat_id][0]["seconds"]
            db[chat_id][0]["played"] = con_seconds
            db[chat_id][0]["dur"] = duration
            db[chat_id][0]["seconds"] = dur
            db[chat_id][0]["speed_path"] = out
            db[chat_id][0]["speed"] = speed

    async def force_stop_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        try:
            check = db.get(chat_id)
            check.pop(0)
        except:
            pass
        await remove_active_video_chat(chat_id)
        await remove_active_chat(chat_id)
        try:
            for method_name in ["leave_group_call", "leave_call", "stop"]:
                if hasattr(assistant, method_name):
                    await getattr(assistant, method_name)(chat_id)
                    break
        except:
            pass

    async def _reliable_leave_call(self, client, chat_id):
        """Hàm thoát cuộc gọi đáng tin cậy với pytgcalls 2.2.1"""
        left_successfully = False
        
        # Thử các method leave theo thứ tự ưu tiên
        leave_methods = [
            "leave_group_call",  # Method chính của pytgcalls 2.2.1
            "leave_call",
            "stop_stream", 
            "stop",
            "disconnect"
        ]
        
        for method_name in leave_methods:
            if hasattr(client, method_name):
                try:
                    method = getattr(client, method_name)
                    await method(chat_id)
                    left_successfully = True
                    print(f"✅ Successfully left chat {chat_id} using {method_name}")
                    break
                except Exception as e:
                    print(f"⚠️ Failed to leave chat {chat_id} with {method_name}: {e}")
                    continue
        
        # Nếu tất cả method đều thất bại, thử với tất cả client có sẵn
        if not left_successfully:
            print(f"🔄 Trying with all available clients for chat {chat_id}")
            for client_instance in [self.one, self.two, self.three, self.four, self.five]:
                if client_instance and not left_successfully:
                    for method_name in leave_methods:
                        if hasattr(client_instance, method_name):
                            try:
                                method = getattr(client_instance, method_name)
                                await method(chat_id)
                                left_successfully = True
                                print(f"✅ Left chat {chat_id} using backup client with {method_name}")
                                break
                            except:
                                continue
                    if left_successfully:
                        break
        
        if not left_successfully:
            print(f"❌ Could not leave chat {chat_id} with any method")
        
        return left_successfully

    async def force_next_song(self, chat_id):
        """Force chuyển sang bài tiếp theo trong queue ngay lập tức"""
        try:
            check = db.get(chat_id)
            if not check or len(check) == 0:
                print(f"🚪 No songs to play for chat {chat_id}")
                return False
                
            assistant = await group_assistant(self, chat_id)
            if not assistant:
                print(f"❌ No assistant available for chat {chat_id}")
                return False
                
            # Trigger change_stream để chuyển bài
            await self.change_stream(assistant, chat_id)
            print(f"✅ Forced next song for chat {chat_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error forcing next song for chat {chat_id}: {e}")
            return False

    async def change_stream(self, client, chat_id):
        check = db.get(chat_id)
        popped = None
        loop = await get_loop(chat_id)
        
        print(f"🔄 Change stream called for chat {chat_id}, queue length: {len(check) if check else 0}")
        
        # Nếu không có queue, thoát ngay lập tức
        if not check or len(check) == 0:
            print(f"🚪 No songs in queue for chat {chat_id}, leaving...")
            await _clear_(chat_id)
            await self._reliable_leave_call(client, chat_id)
            return
            
        try:
            # Luôn luôn pop bài đầu tiên (bài vừa kết thúc) nếu không có loop
            if loop == 0:
                if len(check) > 0:
                    popped = check.pop(0)
                    print(f"🎵 Removed finished song from queue, remaining: {len(check)}")
            else:
                # Nếu có loop, giảm counter
                loop = loop - 1
                await set_loop(chat_id, loop)
                print(f"🔁 Loop mode, remaining loops: {loop}")
            
            # Cleanup bài vừa pop
            if popped:
                await auto_clean(popped)
            
            # Kiểm tra lại queue sau khi pop
            if not check or len(check) == 0:
                print(f"🚪 Queue empty after processing for chat {chat_id}, leaving...")
                await _clear_(chat_id)
                await self._reliable_leave_call(client, chat_id)
                return
                
        except Exception as e:
            print(f"❌ Error in change_stream processing: {e}")
            # Kiểm tra queue sau lỗi
            check = db.get(chat_id)
            if not check or len(check) == 0:
                print(f"🚪 Queue empty after error for chat {chat_id}, leaving...")
                await _clear_(chat_id)
                await self._reliable_leave_call(client, chat_id)
                return
        else:
            # Nếu có queue, tiếp tục play bài tiếp theo
            queued = check[0]["file"]
            language = await get_lang(chat_id)
            _ = get_string(language)
            title = (check[0]["title"]).title()
            user = check[0]["by"]
            original_chat_id = check[0]["chat_id"]
            streamtype = check[0]["streamtype"]
            videoid = check[0]["vidid"]
            db[chat_id][0]["played"] = 0
            exis = (check[0]).get("old_dur")
            if exis:
                db[chat_id][0]["dur"] = exis
                db[chat_id][0]["seconds"] = check[0]["old_second"]
                db[chat_id][0]["speed_path"] = None
                db[chat_id][0]["speed"] = 1.0
            video = True if str(streamtype) == "video" else False
            
            print(f"🎵 Playing next song: {title} for chat {chat_id}")
            
            if "live_" in queued:
                n, link = await YouTube.video(videoid, True)
                if n == 0:
                    return await app.send_message(original_chat_id, text=_["call_6"])
                
                stream = self.prepare_stream(link, is_video=video)
                    
                try:
                    success = False
                    for method_name in ["change_stream", "play", "switch"]:
                        if hasattr(client, method_name):
                            try:
                                await getattr(client, method_name)(chat_id, stream)
                                print(f"✅ Successfully changed to next song using {method_name}")
                                success = True
                                break
                            except Exception as e:
                                print(f"⚠️ Failed with {method_name}: {e}")
                                continue
                    
                    if not success:
                        print(f"❌ Failed to change stream for chat {chat_id}")
                        return await app.send_message(original_chat_id, text=_["call_6"])
                        
                except Exception as e:
                    print(f"❌ Exception in stream change: {e}")
                    return await app.send_message(original_chat_id, text=_["call_6"])
                    
                img = await get_thumb(videoid)
                button = stream_markup(_, chat_id)
                run = await app.send_photo(
                    chat_id=original_chat_id,
                    photo=img,
                    caption=_["stream_1"].format(
                        f"https://t.me/{app.username}?start=info_{videoid}",
                        title[:23],
                        check[0]["dur"],
                        user,
                    ),
                    reply_markup=InlineKeyboardMarkup(button),
                )
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "tg"
                
            elif "vid_" in queued:
                mystic = await app.send_message(original_chat_id, _["call_7"])
                try:
                    file_path, direct = await YouTube.download(
                        videoid,
                        mystic,
                        videoid=True,
                        video=True if str(streamtype) == "video" else False,
                    )
                except:
                    return await mystic.edit_text(_["call_6"], disable_web_page_preview=True)
                    
                stream = self.prepare_stream(file_path, is_video=video)
                    
                try:
                    for method_name in ["change_stream", "play", "switch"]:
                        if hasattr(client, method_name):
                            await getattr(client, method_name)(chat_id, stream)
                            break
                except:
                    return await app.send_message(original_chat_id, text=_["call_6"])
                    
                img = await get_thumb(videoid)
                button = stream_markup(_, chat_id)
                await mystic.delete()
                run = await app.send_photo(
                    chat_id=original_chat_id,
                    photo=img,
                    caption=_["stream_1"].format(
                        f"https://t.me/{app.username}?start=info_{videoid}",
                        title[:23],
                        check[0]["dur"],
                        user,
                    ),
                    reply_markup=InlineKeyboardMarkup(button),
                )
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "stream"
                
            elif "index_" in queued:
                stream = self.prepare_stream(videoid, is_video=(str(streamtype) == "video"))
                    
                try:
                    for method_name in ["change_stream", "play", "switch"]:
                        if hasattr(client, method_name):
                            await getattr(client, method_name)(chat_id, stream)
                            break
                except:
                    return await app.send_message(original_chat_id, text=_["call_6"])
                    
                button = stream_markup(_, chat_id)
                run = await app.send_photo(
                    chat_id=original_chat_id,
                    photo=config.STREAM_IMG_URL,
                    caption=_["stream_2"].format(user),
                    reply_markup=InlineKeyboardMarkup(button),
                )
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "tg"
                
            else:
                stream = self.prepare_stream(queued, is_video=video)
                    
                try:
                    for method_name in ["change_stream", "play", "switch"]:
                        if hasattr(client, method_name):
                            await getattr(client, method_name)(chat_id, stream)
                            break
                except:
                    return await app.send_message(original_chat_id, text=_["call_6"])
                    
                if videoid == "telegram":
                    button = stream_markup(_, chat_id)
                    run = await app.send_photo(
                        chat_id=original_chat_id,
                        photo=config.TELEGRAM_AUDIO_URL if str(streamtype) == "audio" else config.TELEGRAM_VIDEO_URL,
                        caption=_["stream_1"].format(config.SUPPORT_CHAT, title[:23], check[0]["dur"], user),
                        reply_markup=InlineKeyboardMarkup(button),
                    )
                    db[chat_id][0]["mystic"] = run
                    db[chat_id][0]["markup"] = "tg"
                elif videoid == "soundcloud":
                    button = stream_markup(_, chat_id)
                    run = await app.send_photo(
                        chat_id=original_chat_id,
                        photo=config.SOUNCLOUD_IMG_URL,
                        caption=_["stream_1"].format(config.SUPPORT_CHAT, title[:23], check[0]["dur"], user),
                        reply_markup=InlineKeyboardMarkup(button),
                    )
                    db[chat_id][0]["mystic"] = run
                    db[chat_id][0]["markup"] = "tg"
                else:
                    img = await get_thumb(videoid)
                    button = stream_markup(_, chat_id)
                    run = await app.send_photo(
                        chat_id=original_chat_id,
                        photo=img,
                        caption=_["stream_1"].format(
                            f"https://t.me/{app.username}?start=info_{videoid}",
                            title[:23],
                            check[0]["dur"],
                            user,
                        ),
                        reply_markup=InlineKeyboardMarkup(button),
                    )
                    db[chat_id][0]["mystic"] = run
                    db[chat_id][0]["markup"] = "stream"

    async def ping(self):
        pings = []
        try:
            for client in [self.one, self.two, self.three, self.four, self.five]:
                if client and hasattr(client, 'ping'):
                    pings.append(await client.ping)
            return str(round(sum(pings) / len(pings), 3)) if pings else "0"
        except:
            return "0"

    async def start(self):
        LOGGER(__name__).info("Starting PyTgCalls Client...\\n")
        try:
            for i, client in enumerate([self.one, self.two, self.three, self.four, self.five], 1):
                if client:
                    try:
                        await client.start()
                        LOGGER(__name__).info(f"Started client {i}")
                    except Exception as e:
                        LOGGER(__name__).error(f"Error starting client {i}: {e}")
        except Exception as e:
            LOGGER(__name__).error(f"Error starting PyTgCalls: {e}")

    async def decorators(self):
        try:
            # Simplified decorators với error handling
            clients = [self.one, self.two, self.three, self.four, self.five]
            
            for client in clients:
                if client:
                    try:
                        # Try to set decorators if methods exist
                        if hasattr(client, 'on_kicked'):
                            @client.on_kicked()
                            async def on_kicked_handler(_, chat_id: int):
                                await self.stop_stream(chat_id)
                        
                        if hasattr(client, 'on_closed_voice_chat'):
                            @client.on_closed_voice_chat()
                            async def on_closed_handler(_, chat_id: int):
                                await self.stop_stream(chat_id)
                        
                        if hasattr(client, 'on_left'):
                            @client.on_left()
                            async def on_left_handler(_, chat_id: int):
                                await self.stop_stream(chat_id)
                        
                        if hasattr(client, 'on_stream_end'):
                            @client.on_stream_end()
                            async def on_stream_end_handler(client_instance, update):
                                try:
                                    if hasattr(update, 'chat_id'):
                                        chat_id = update.chat_id
                                        print(f"🎵 Stream ended in chat {chat_id}")
                                        
                                        # Kiểm tra queue trước khi xử lý
                                        check = db.get(chat_id)
                                        if not check or len(check) == 0:
                                            print(f"🚪 No more songs in queue for chat {chat_id}, auto-leaving...")
                                            await _clear_(chat_id)
                                            await self._reliable_leave_call(client_instance, chat_id)
                                        else:
                                            print(f"🎵 Queue has {len(check)} songs, playing next...")
                                            # Đảm bảo chuyển bài ngay lập tức
                                            try:
                                                await self.change_stream(client_instance, chat_id)
                                            except Exception as stream_error:
                                                print(f"❌ Error changing stream: {stream_error}")
                                                # Thử lại với force method
                                                try:
                                                    await self.force_next_song(chat_id)
                                                except:
                                                    print(f"❌ Force next song also failed for chat {chat_id}")
                                except Exception as e:
                                    print(f"❌ Error in stream end handler: {e}")
                                    # Fallback: cố gắng thoát nếu có lỗi
                                    try:
                                        chat_id = getattr(update, 'chat_id', None)
                                        if chat_id:
                                            await self._reliable_leave_call(client_instance, chat_id)
                                    except:
                                        pass
                    except Exception as e:
                        LOGGER(__name__).error(f"Error setting decorators for client: {e}")
                        
        except Exception as e:
            LOGGER(__name__).error(f"Error setting decorators: {e}")


SANKI = Call()
