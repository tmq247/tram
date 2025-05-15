import asyncio
import os
from datetime import datetime, timedelta
from typing import Union

from pyrogram import Client
from pytgcalls import PyTgCalls, StreamType
from pytgcalls.types.input_stream import AudioPiped, AudioVideoPiped
from pytgcalls.types.input_stream.quality import HighQualityAudio, MediumQualityVideo

import config
from SANKIXD import LOGGER, YouTube, app
from SANKIXD.utils.database import add_active_chat, remove_active_chat
from SANKIXD.utils.exceptions import AssistantErr

class Call(PyTgCalls):
    def __init__(self):
        self.userbot1 = Client(
            name="SANKIAss1",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING1),
        )
        self.one = PyTgCalls(self.userbot1)

    async def stop_stream(self, chat_id: int):
        assistant = self.one
        try:
            await remove_active_chat(chat_id)
            await assistant.leave_group_call(chat_id)
        except Exception as e:
            print(f"Lỗi khi dừng stream: {e}")

    async def join_call(self, chat_id: int, link: str, video: bool = False):
        assistant = self.one
        stream = (
            AudioVideoPiped(link, audio_parameters=HighQualityAudio(), video_parameters=MediumQualityVideo())
            if video else AudioPiped(link, audio_parameters=HighQualityAudio())
        )
        await assistant.join_group_call(chat_id, stream, stream_type=StreamType().pulse_stream)
        await add_active_chat(chat_id)

    async def change_stream(self, chat_id: int, file_path: str, video: bool = False):
        assistant = self.one
        stream = (
            AudioVideoPiped(file_path, audio_parameters=HighQualityAudio(), video_parameters=MediumQualityVideo())
            if video else AudioPiped(file_path, audio_parameters=HighQualityAudio())
        )
        await assistant.change_stream(chat_id, stream)

    async def seek_stream(self, chat_id: int, file_path: str, to_seek: str, duration: str, mode: str):
        assistant = self.one
        stream = (
            AudioVideoPiped(file_path, audio_parameters=HighQualityAudio(), video_parameters=MediumQualityVideo(), additional_ffmpeg_parameters=f"-ss {to_seek} -to {duration}")
            if mode == "video"
            else AudioPiped(file_path, audio_parameters=HighQualityAudio(), additional_ffmpeg_parameters=f"-ss {to_seek} -to {duration}")
        )
        await assistant.change_stream(chat_id, stream)

SANKI = Call()
