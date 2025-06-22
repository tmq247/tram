
import asyncio
import os
import re
import time
from datetime import datetime, timedelta
from typing import Union, Optional

from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup
from pytgcalls import PyTgCalls

# Import ntgcalls for fallback
try:
    from ntgcalls import NTgCalls
    from ntgcalls.exceptions import TelegramServerError as NTTelegramServerError
    from ntgcalls.exceptions import ConnectionNotFound
    NT_CALLS_AVAILABLE = True
    print("✅ nt-calls imported successfully")
except ImportError:
    NT_CALLS_AVAILABLE = False
    print("⚠️ nt-calls not available")

# Handle pytgcalls imports for different versions
try:
    from pytgcalls.exceptions import AlreadyJoinedError, NoActiveGroupCall, TelegramServerError
    print("✅ Using py-tgcalls legacy exceptions")
except ImportError:
    try:
        from pytgcalls.exceptions import AlreadyJoined, NotInCall, TelegramServerError
        NoActiveGroupCall = NotInCall
        AlreadyJoinedError = AlreadyJoined
        print("✅ Using py-tgcalls 2.2.1+ exceptions")
    except ImportError:
        # Fallback to generic exceptions
        NoActiveGroupCall = Exception
        AlreadyJoinedError = Exception
        TelegramServerError = Exception
        print("⚠️ Using fallback exceptions")

from pytgcalls.types import Update

# Handle stream types imports
try:
    from pytgcalls.types import (
        AudioQuality,
        ChatUpdate,
        MediaStream,
        UpdatedGroupCallParticipant,
        VideoQuality,
        stream,
        GroupCallConfig,
        CallConfig,
    )
    MODERN_STREAM_TYPES = True
    print("✅ Using modern stream types")
except ImportError:
    try:
        from pytgcalls.types.input_stream import AudioPiped, AudioVideoPiped
        from pytgcalls.types.input_stream.quality import HighQualityAudio, MediumQualityVideo
        MODERN_STREAM_TYPES = False
        print("✅ Using legacy stream types")
    except ImportError:
        from pytgcalls.types import AudioPiped, AudioVideoPiped, HighQualityAudio, MediumQualityVideo
        MODERN_STREAM_TYPES = False
        print("✅ Using fallback stream types")

try:
    from pytgcalls.types.stream import StreamAudioEnded
except ImportError:
    try:
        from pytgcalls.types import StreamAudioEnded
    except ImportError:
        StreamAudioEnded = type('StreamAudioEnded', (), {})

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


def _format_bytes(size: int) -> str:
    """Format a size in bytes into a human-readable format."""
    if size < 1024:
        return f"{size} B"
    for unit in ["KB", "MB", "GB", "TB"]:
        size /= 1024
        if size < 1024:
            return f"{size:.1f} {unit}"
    return f"{size:.1f} PB"


def _format_time(seconds: float) -> str:
    """Format a time in seconds into a human-readable format."""
    if seconds < 60:
        return f"{int(seconds)}s"
    minutes, seconds = divmod(seconds, 60)
    if minutes < 60:
        return f"{int(minutes)}m {int(seconds)}s"
    hours, minutes = divmod(minutes, 60)
    return f"{int(hours)}h {int(minutes)}m"


def _create_progress_bar(percentage: int, length: int = 10) -> str:
    """Generate a textual progress bar representation."""
    filled = round(length * percentage / 100)
    return "⬢" * filled + "⬡" * (length - filled)


def extract_number(text: str) -> float | None:
    """Extract number from text using regex."""
    match = re.search(r"[-+]?\d*\.?\d+", text)
    return float(match.group()) if match else None


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
            cache_duration=200,
        )
        
        # Initialize nt-calls clients as fallback
        if NT_CALLS_AVAILABLE:
            try:
                self.nt_one = NTgCalls()
                print("✅ nt-calls client 1 initialized")
            except Exception as e:
                print(f"⚠️ nt-calls client 1 failed: {e}")
                self.nt_one = None
        else:
            self.nt_one = None
            
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
        
        if NT_CALLS_AVAILABLE:
            try:
                self.nt_two = NTgCalls()
                print("✅ nt-calls client 2 initialized")
            except Exception as e:
                print(f"⚠️ nt-calls client 2 failed: {e}")
                self.nt_two = None
        else:
            self.nt_two = None
            
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
        
        if NT_CALLS_AVAILABLE:
            try:
                self.nt_three = NTgCalls()
                print("✅ nt-calls client 3 initialized")
            except Exception as e:
                print(f"⚠️ nt-calls client 3 failed: {e}")
                self.nt_three = None
        else:
            self.nt_three = None
            
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
        
        if NT_CALLS_AVAILABLE:
            try:
                self.nt_four = NTgCalls()
                print("✅ nt-calls client 4 initialized")
            except Exception as e:
                print(f"⚠️ nt-calls client 4 failed: {e}")
                self.nt_four = None
        else:
            self.nt_four = None
            
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
        
        if NT_CALLS_AVAILABLE:
            try:
                self.nt_five = NTgCalls()
                print("✅ nt-calls client 5 initialized")
            except Exception as e:
                print(f"⚠️ nt-calls client 5 failed: {e}")
                self.nt_five = None
        else:
            self.nt_five = None

    def _create_stream(self, link: str, video: bool = False, ffmpeg_params: str = None):
        """Create appropriate stream object based on available types"""
        if MODERN_STREAM_TYPES:
            return MediaStream(
                audio_path=link,
                media_path=link if video else None,
                audio_parameters=AudioQuality.HIGH if video else AudioQuality.STUDIO,
                video_parameters=VideoQuality.FHD_1080p if video else VideoQuality.SD_360p,
                audio_flags=MediaStream.Flags.REQUIRED,
                video_flags=(
                    MediaStream.Flags.AUTO_DETECT if video else MediaStream.Flags.IGNORE
                ),
                ffmpeg_parameters=ffmpeg_params,
            )
        else:
            # Legacy stream types
            if video:
                return AudioVideoPiped(
                    link,
                    audio_parameters=HighQualityAudio(),
                    video_parameters=MediumQualityVideo(),
                    additional_ffmpeg_parameters=ffmpeg_params,
                )
            else:
                return AudioPiped(
                    link,
                    audio_parameters=HighQualityAudio(),
                    additional_ffmpeg_parameters=ffmpeg_params,
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
                pass
        else:
            out = file_path
        dur = await asyncio.get_event_loop().run_in_executor(None, check_duration, out)
        dur = int(dur)
        played, con_seconds = speed_converter(playing[0]["played"], speed)
        duration = seconds_to_min(dur)
        
        stream = self._create_stream(
            out, 
            video=playing[0]["streamtype"] == "video",
            ffmpeg_params=f"-ss {played} -to {duration}"
        )
        
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

    async def skip_stream(
        self,
        chat_id: int,
        link: str,
        video: Union[bool, str] = None,
        image: Union[bool, str] = None,
    ):
        assistant = await group_assistant(self, chat_id)
        stream = self._create_stream(link, video=bool(video))
        await assistant.change_stream(chat_id, stream)

    async def seek_stream(self, chat_id, file_path, to_seek, duration, mode):
        assistant = await group_assistant(self, chat_id)
        stream = self._create_stream(
            file_path,
            video=mode == "video",
            ffmpeg_params=f"-ss {to_seek} -to {duration}"
        )
        await assistant.change_stream(chat_id, stream)

    async def stream_call(self, link):
        assistant = await group_assistant(self, config.LOGGER_ID)
        stream = self._create_stream(link, video=True)
        
        if MODERN_STREAM_TYPES:
            call_config = GroupCallConfig(auto_start=False) if config.LOGGER_ID < 0 else CallConfig(timeout=50)
            await assistant.play(config.LOGGER_ID, stream, call_config)
        else:
            await assistant.join_group_call(config.LOGGER_ID, stream)
        
        await asyncio.sleep(0.2)
        await assistant.leave_group_call(config.LOGGER_ID)

    async def safe_join_call(self, assistant, chat_id, link, nt_assistant=None):
        """Safe method to join call with multiple API attempts including nt-calls"""
        try:
            # Try with regular pytgcalls first
            stream = self._create_stream(link)
            await assistant.join_group_call(chat_id, stream)
            return True
        except (NoActiveGroupCall, Exception) as e:
            print(f"pytgcalls failed: {e}")
            if NT_CALLS_AVAILABLE and nt_assistant:
                try:
                    await nt_assistant.start(assistant._client)
                    await nt_assistant.join_call(chat_id, link)
                    print("✅ ntgcalls fallback successful")
                    return True
                except Exception as nt_e:
                    print(f"⚠️ ntgcalls fallback failed: {nt_e}")
            return False

    async def safe_leave_call(self, assistant, chat_id, nt_assistant=None):
        """Safe method to leave call with multiple API attempts including nt-calls"""
        leave_methods = ["leave_group_call", "leave_call", "disconnect"]
        
        # Try different leave methods with py-tgcalls
        for method_name in leave_methods:
            if hasattr(assistant, method_name):
                try:
                    method = getattr(assistant, method_name)
                    await method(chat_id)
                    print(f"✅ py-tgcalls {method_name} succeeded")
                    return True
                except Exception as e:
                    print(f"⚠️ py-tgcalls {method_name} failed: {e}")
                    continue

        # Try nt-calls as fallback
        if nt_assistant:
            try:
                nt_methods = ["leave_group_call", "leave_call"]
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
        
        stream = self._create_stream(link, video=bool(video))
        
        try:
            if MODERN_STREAM_TYPES:
                call_config = GroupCallConfig(auto_start=False) if chat_id < 0 else CallConfig(timeout=50)
                await assistant.play(chat_id, stream, call_config)
            else:
                await assistant.join_group_call(chat_id, stream)
        except NoActiveGroupCall:
            # Try nt-calls as fallback
            if NT_CALLS_AVAILABLE:
                try:
                    nt_assistant = getattr(self, f"nt_{assistant._client.session_name.lower().replace('sankiass', '')}", None)
                    if nt_assistant:
                        await nt_assistant.start(assistant._client)
                        await nt_assistant.join_call(chat_id, link)
                        print("✅ nt-calls fallback succeeded")
                    else:
                        raise AssistantErr(_["call_8"])
                except Exception as e:
                    print(f"⚠️ nt-calls fallback failed: {e}")
                    raise AssistantErr(_["call_8"])
            else:
                raise AssistantErr(_["call_8"])
        except AlreadyJoinedError:
            raise AssistantErr(_["call_9"])
        except TelegramServerError:
            raise AssistantErr(_["call_10"])
        
        await add_active_chat(chat_id)
        await music_on(chat_id)
        if video:
            await add_active_video_chat(chat_id)
        if await is_autoend():
            counter[chat_id] = {}
            users = len(await assistant.get_participants(chat_id))
            if users == 1:
                autoend[chat_id] = datetime.now() + timedelta(minutes=1)

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
                    return await app.send_message(
                        original_chat_id,
                        text=_["call_6"],
                    )
                stream = self._create_stream(link, video=video)
                try:
                    await client.change_stream(chat_id, stream)
                except Exception:
                    return await app.send_message(
                        original_chat_id,
                        text=_["call_6"],
                    )
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
                    return await mystic.edit_text(
                        _["call_6"], disable_web_page_preview=True
                    )
                stream = self._create_stream(file_path, video=video)
                try:
                    await client.change_stream(chat_id, stream)
                except:
                    return await app.send_message(
                        original_chat_id,
                        text=_["call_6"],
                    )
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
                stream = self._create_stream(videoid, video=str(streamtype) == "video")
                try:
                    await client.change_stream(chat_id, stream)
                except:
                    return await app.send_message(
                        original_chat_id,
                        text=_["call_6"],
                    )
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
                stream = self._create_stream(queued, video=video)
                try:
                    await client.change_stream(chat_id, stream)
                except:
                    return await app.send_message(
                        original_chat_id,
                        text=_["call_6"],
                    )
                if videoid == "telegram":
                    button = stream_markup(_, chat_id)
                    run = await app.send_photo(
                        chat_id=original_chat_id,
                        photo=config.TELEGRAM_AUDIO_URL
                        if str(streamtype) == "audio"
                        else config.TELEGRAM_VIDEO_URL,
                        caption=_["stream_1"].format(
                            config.SUPPORT_CHAT, title[:23], check[0]["dur"], user
                        ),
                        reply_markup=InlineKeyboardMarkup(button),
                    )
                    db[chat_id][0]["mystic"] = run
                    db[chat_id][0]["markup"] = "tg"
                elif videoid == "soundcloud":
                    button = stream_markup(_, chat_id)
                    run = await app.send_photo(
                        chat_id=original_chat_id,
                        photo=config.SOUNCLOUD_IMG_URL,
                        caption=_["stream_1"].format(
                            config.SUPPORT_CHAT, title[:23], check[0]["dur"], user
                        ),
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
        return str(round(sum(pings) / len(pings), 3))

    async def start(self):
        LOGGER(__name__).info("Starting PyTgCalls Client...\n")
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

    async def decorators(self):
        # Updated event handlers for py-tgcalls 2.2.1+
        clients = []
        if config.STRING1:
            clients.append(self.one)
        if config.STRING2:
            clients.append(self.two)
        if config.STRING3:
            clients.append(self.three)
        if config.STRING4:
            clients.append(self.four)
        if config.STRING5:
            clients.append(self.five)

        async def stream_services_handler(_, chat_id: int):
            await self.stop_stream(chat_id)

        async def stream_end_handler1(client, update: Update):
            if not isinstance(update, StreamAudioEnded):
                return
            await self.change_stream(client, update.chat_id)

        # Register event handlers with proper method names
        for client in clients:
            if hasattr(client, 'on_kicked'):
                client.on_kicked()(stream_services_handler)
            elif hasattr(client, 'on_participant_kicked'):
                client.on_participant_kicked()(stream_services_handler)
            
            if hasattr(client, 'on_closed_voice_chat'):
                client.on_closed_voice_chat()(stream_services_handler)
            elif hasattr(client, 'on_call_ended'):
                client.on_call_ended()(stream_services_handler)
            
            if hasattr(client, 'on_left'):
                client.on_left()(stream_services_handler)
            elif hasattr(client, 'on_participant_left'):
                client.on_participant_left()(stream_services_handler)
            
            if hasattr(client, 'on_stream_end'):
                client.on_stream_end()(stream_end_handler1)
            elif hasattr(client, 'on_stream_ended'):
                client.on_stream_ended()(stream_end_handler1)
            
        print("✅ Event handlers registered successfully")


SANKI = Call()
