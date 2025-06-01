# Tạo call.py universal tương thích với nhiều phiên bản
import asyncio
import os
from datetime import datetime, timedelta
from typing import Union

from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup

# Import pytgcalls với compatibility checking
try:
    from pytgcalls import PyTgCalls
    print("✅ PyTgCalls imported successfully")
except ImportError as e:
    print(f"❌ Failed to import PyTgCalls: {e}")
    raise

# Try different import paths for exceptions
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
        # Fallback to generic exceptions
        AlreadyJoined = Exception
        NotInCall = Exception  
        TelegramServerError = Exception
        print("⚠️ Using generic exceptions")

# Try different import paths for input streams
try:
    from pytgcalls.types.input_stream import AudioPiped, AudioVideoPiped
    from pytgcalls.types.input_stream.quality import HighQualityAudio, MediumQualityVideo
    print("✅ New stream types imported")
except ImportError:
    try:
        from pytgcalls.types import AudioPiped, AudioVideoPiped
        from pytgcalls.types import HighQualityAudio, MediumQualityVideo
        print("✅ Alternative stream types imported")
    except ImportError:
        try:
            from pytgcalls import AudioPiped, AudioVideoPiped, HighQualityAudio, MediumQualityVideo
            print("✅ Direct stream types imported")
        except ImportError:
            print("❌ Could not import stream types - creating fallbacks")
            # Create basic fallback classes
            class AudioPiped:
                def __init__(self, path, audio_parameters=None, additional_ffmpeg_parameters=""):
                    self.path = path
                    self.audio_parameters = audio_parameters
                    self.additional_ffmpeg_parameters = additional_ffmpeg_parameters
            
            class AudioVideoPiped:
                def __init__(self, path, audio_parameters=None, video_parameters=None, additional_ffmpeg_parameters=""):
                    self.path = path
                    self.audio_parameters = audio_parameters
                    self.video_parameters = video_parameters
                    self.additional_ffmpeg_parameters = additional_ffmpeg_parameters
            
            class HighQualityAudio:
                pass
            
            class MediumQualityVideo:
                pass

# Try to import other required types
try:
    from pytgcalls.types import Update
    from pytgcalls.types.stream import StreamAudioEnded
    print("✅ Update types imported")
except ImportError:
    try:
        from pytgcalls import Update, StreamAudioEnded
        print("✅ Alternative update types imported") 
    except ImportError:
        print("⚠️ Could not import update types - using fallbacks")
        Update = object
        StreamAudioEnded = object

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

    async def pause_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.pause_stream(chat_id)

    async def resume_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.resume_stream(chat_id)

    async def stop_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        try:
            await _clear_(chat_id)
            await assistant.leave_group_call(chat_id)
        except:
            pass

    async def stop_stream_force(self, chat_id: int):
        try:
            if config.STRING1:
                await self.one.leave_group_call(chat_id)
        except:
            pass
        try:
            if config.STRING2:
                await self.two.leave_group_call(chat_id)
        except:
            pass
        try:
            if config.STRING3:
                await self.three.leave_group_call(chat_id)
        except:
            pass
        try:
            if config.STRING4:
                await self.four.leave_group_call(chat_id)
        except:
            pass
        try:
            if config.STRING5:
                await self.five.leave_group_call(chat_id)
        except:
            pass
        try:
            await _clear_(chat_id)
        except:
            pass

    def create_audio_stream(self, path, additional_params=""):
        """Helper method to create audio stream with compatibility"""
        try:
            return AudioPiped(
                path,
                audio_parameters=HighQualityAudio(),
                additional_ffmpeg_parameters=additional_params,
            )
        except Exception as e:
            print(f"⚠️ Fallback audio stream creation: {e}")
            # Try simpler creation
            try:
                return AudioPiped(path)
            except:
                return path

    def create_video_stream(self, path, additional_params=""):
        """Helper method to create video stream with compatibility"""
        try:
            return AudioVideoPiped(
                path,
                audio_parameters=HighQualityAudio(),
                video_parameters=MediumQualityVideo(),
                additional_ffmpeg_parameters=additional_params,
            )
        except Exception as e:
            print(f"⚠️ Fallback video stream creation: {e}")
            # Try simpler creation
            try:
                return AudioVideoPiped(path)
            except:
                return path

    async def skip_stream(
        self,
        chat_id: int,
        link: str,
        video: Union[bool, str] = None,
        image: Union[bool, str] = None,
    ):
        assistant = await group_assistant(self, chat_id)
        if video:
            stream = self.create_video_stream(link)
        else:
            stream = self.create_audio_stream(link)
        await assistant.change_stream(chat_id, stream)

    async def seek_stream(self, chat_id, file_path, to_seek, duration, mode):
        assistant = await group_assistant(self, chat_id)
        additional_params = f"-ss {to_seek} -to {duration}"
        
        if mode == "video":
            stream = self.create_video_stream(file_path, additional_params)
        else:
            stream = self.create_audio_stream(file_path, additional_params)
        
        await assistant.change_stream(chat_id, stream)

    async def stream_call(self, link):
        assistant = await group_assistant(self, config.LOGGER_ID)
        stream = self.create_video_stream(link)
        await assistant.join_group_call(config.LOGGER_ID, stream)
        await asyncio.sleep(0.2)
        await assistant.leave_group_call(config.LOGGER_ID)

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
        
        if video:
            stream = self.create_video_stream(link)
        else:
            stream = self.create_audio_stream(link)
        
        try:
            await assistant.join_group_call(chat_id, stream)
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

    async def speedup_stream(self, chat_id: int, file_path, speed, playing):
        assistant = await group_assistant(self, chat_id)
        if str(speed) != str("1.0"):
            base = os.path.basename(file_path)
            chatdir = os.path.join(os.getcwd(), "playback", str(speed))
            if not os.path.isdir(chatdir):
                os.makedirs(chatdir)
            out = os.path.join(chatdir, base)
            if not os.path.isfile(out):
                if str(speed) == str("0.5"):
                    vs = 2.0
                if str(speed) == str("0.75"):
                    vs = 1.35
                if str(speed) == str("1.5"):
                    vs = 0.68
                if str(speed) == str("2.0"):
                    vs = 0.5
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
        if playing[0]["streamtype"] == "video":
            stream = self.create_video_stream(out, additional_params)
        else:
            stream = self.create_audio_stream(out, additional_params)
            
        if str(db[chat_id][0]["file"]) == str(file_path):
            await assistant.change_stream(chat_id, stream)
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
            await assistant.leave_group_call(chat_id)
        except:
            pass

    async def change_stream(self, client, chat_id):
        check = db.get(chat_id)
        popped = None
        loop = await get_loop(chat_id)
        try:
            if loop == 0:
                popped = check.pop(0)
            else:
                loop = loop - 1
                await set_loop(chat_id, loop)
            await auto_clean(popped)
            if not check:
                await _clear_(chat_id)
                return await client.leave_group_call(chat_id)
        except:
            try:
                await _clear_(chat_id)
                return await client.leave_group_call(chat_id)
            except:
                return
        else:
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
            
            if "live_" in queued:
                n, link = await YouTube.video(videoid, True)
                if n == 0:
                    return await app.send_message(original_chat_id, text=_["call_6"])
                
                if video:
                    stream = self.create_video_stream(link)
                else:
                    stream = self.create_audio_stream(link)
                    
                try:
                    await client.change_stream(chat_id, stream)
                except Exception:
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
                    
                if video:
                    stream = self.create_video_stream(file_path)
                else:
                    stream = self.create_audio_stream(file_path)
                    
                try:
                    await client.change_stream(chat_id, stream)
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
                if str(streamtype) == "video":
                    stream = self.create_video_stream(videoid)
                else:
                    stream = self.create_audio_stream(videoid)
                    
                try:
                    await client.change_stream(chat_id, stream)
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
                if video:
                    stream = self.create_video_stream(queued)
                else:
                    stream = self.create_audio_stream(queued)
                    
                try:
                    await client.change_stream(chat_id, stream)
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
            if config.STRING1:
                pings.append(await self.one.ping)
            if config.STRING2:
                pings.append(await self.two.ping)
            if config.STRING3:
                pings.append(await self.three.ping)
            if config.STRING4:
                pings.append(await self.four.ping)
            if config.STRING5:
                pings.append(await self.five.ping)
            return str(round(sum(pings) / len(pings), 3)) if pings else "0"
        except:
            return "0"

    async def start(self):
        LOGGER(__name__).info("Starting PyTgCalls Client...\\n")
        try:
            if config.STRING1:
                await self.one.start()
            if config.STRING2:
                await self.two.start()
            if config.STRING3:
                await self.three.start()
            if config.STRING4:
                await self.four.start()
            if config.STRING5:
                await self.five.start()
        except Exception as e:
            LOGGER(__name__).error(f"Error starting PyTgCalls: {e}")

    async def decorators(self):
        try:
            @self.one.on_kicked()
            @self.two.on_kicked()
            @self.three.on_kicked()
            @self.four.on_kicked()
            @self.five.on_kicked()
            @self.one.on_closed_voice_chat()
            @self.two.on_closed_voice_chat()
            @self.three.on_closed_voice_chat()
            @self.four.on_closed_voice_chat()
            @self.five.on_closed_voice_chat()
            @self.one.on_left()
            @self.two.on_left()
            @self.three.on_left()
            @self.four.on_left()
            @self.five.on_left()
            async def stream_services_handler(_, chat_id: int):
                await self.stop_stream(chat_id)

            @self.one.on_stream_end()
            @self.two.on_stream_end()
            @self.three.on_stream_end()
            @self.four.on_stream_end()
            @self.five.on_stream_end()
            async def stream_end_handler1(client, update):
                try:
                    if hasattr(update, 'chat_id'):
                        await self.change_stream(client, update.chat_id)
                except:
                    pass
        except Exception as e:
            LOGGER(__name__).error(f"Error setting decorators: {e}")


SANKI = Call()
