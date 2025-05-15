import asyncio
import os
from datetime import datetime, timedelta
from typing import Union

from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup
from pytgcalls import PyTgCalls
from pytgcalls.types import Update
from pytgcalls.types.input_stream import AudioPiped, AudioVideoPiped
from pytgcalls.types.input_stream.quality import HighQualityAudio, MediumQualityVideo
from pytgcalls.types.stream import StreamAudioEnded

import config
from SANKIXD import LOGGER, YouTube, app
from SANKIXD.utils.database import add_active_chat, remove_active_chat

class Call:
    def __init__(self):
        self.autoend = {}  # Định nghĩa autoend để tránh lỗi ImportError

        # Khởi tạo các session assistant
        self.userbot1 = Client(
            name="SANKIAss1",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING1),
        )

        self.one = PyTgCalls(self.userbot1)  # Cung cấp 'app'

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
        await assistant.join_group_call(chat_id, stream, stream_type="pulse")
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
        await self.one.start()

    def decorators(self):
        async def stream_services_handler(_, chat_id: int):
            await self.stop_stream(chat_id)

        async def stream_end_handler(client, update):
            if isinstance(update, StreamAudioEnded):
                await self.change_stream(client, update.chat_id)

        self.one.on_kicked()(stream_services_handler)
        self.one.on_closed_voice_chat()(stream_services_handler)
        self.one.on_left()(stream_services_handler)
        self.one.on_stream_end()(stream_end_handler)

SANKI = Call()
SANKI.decorators()  # Kích hoạt sự kiện xử lý
