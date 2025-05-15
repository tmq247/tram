import asyncio
import os
from datetime import datetime, timedelta
from typing import Union

from pyrogram import Client
from pytgcalls import PyTgCalls, StreamType
from pytgcalls.types.input_stream import AudioPiped, AudioVideoPiped
from pytgcalls.types.input_stream.quality import HighQualityAudio, MediumQualityVideo
from pytgcalls.exceptions import AlreadyJoinedError, NoActiveGroupCall, TelegramServerError

import config
from SANKIXD import LOGGER, YouTube, app
from SANKIXD.utils.database import add_active_chat, remove_active_chat

class Call(PyTgCalls):
    def __init__(self):
        super().__init__()  # Gọi phương thức khởi tạo của PyTgCalls
        self._is_running = False  # Tránh lỗi AttributeError khi gọi start()
        self.autoend = {}  # Khai báo biến autoend trong lớp

        # Khởi tạo các session assistant
        self.userbot1 = Client(name="SANKIAss1", api_id=config.API_ID, api_hash=config.API_HASH, session_string=str(config.STRING1))
        self.one = PyTgCalls(self.userbot1, cache_duration=100)

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

    async def start(self):
        LOGGER(__name__).info("Starting PyTgCalls Client...\n")
        self._is_running = True  # Đánh dấu trạng thái đã chạy
        await self.one.start()

SANKI = Call()
