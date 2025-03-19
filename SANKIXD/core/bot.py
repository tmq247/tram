from pyrogram import Client, errors
from pyrogram.enums import ChatMemberStatus, ParseMode

import config

from ..logging import LOGGER


class SANKI(Client):
    def __init__(self):
        LOGGER(__name__).info(f"KHởi động Bot...")
        super().__init__(
            name="Muội Muội",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            in_memory=True,
            max_concurrent_transmissions=7,
        )

    async def start(self):
        await super().start()
        self.id = self.me.id
        self.name = self.me.first_name + " " + (self.me.last_name or "")
        self.username = self.me.username
        self.mention = self.me.mention

        try:
            await self.send_message(
                chat_id=config.LOGGER_ID,
                text=f"<u><b>» {self.mention} Bot khởi động :</b><u>\n\nID : <code>{self.id}</code>\nTên : {self.name}\nᴜsᴇʀɴᴀᴍᴇ : @{self.username}",
            )
        except (errors.ChannelInvalid, errors.PeerIdInvalid):
            LOGGER(__name__).error(
                "Bot không thể truy cập vào nhóm/kênh nhật ký. Đảm bảo rằng bạn đã thêm bot vào nhóm/kênh nhật ký của mình."
            )
            exit()
        except Exception as ex:
            LOGGER(__name__).error(
                f"Bot không truy cập được vào nhóm/kênh nhật ký.\n  Lý do : {type(ex).__name__}."
            )
            exit()

        a = await self.get_chat_member(config.LOGGER_ID, self.id)
        if a.status != ChatMemberStatus.ADMINISTRATOR:
            LOGGER(__name__).error(
                "Vui lòng thêm bot của bạn với tư cách quản trị viên trong nhóm/kênh nhật ký của bạn."
            )
            exit()
        LOGGER(__name__).info(f"Bot âm nhạc bắt đầu là {self.name}")

    async def stop(self):
        await super().stop()
