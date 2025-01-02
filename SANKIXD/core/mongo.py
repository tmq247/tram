from motor.motor_asyncio import AsyncIOMotorClient

from config import MONGO_DB_URI

from ..logging import LOGGER

LOGGER(__name__).info("Kết nối với cơ sở dữ liệu Mongo của bạn...")
try:
    _mongo_async_ = AsyncIOMotorClient(MONGO_DB_URI)
    mongodb = _mongo_async_.Anon
    LOGGER(__name__).info("Đã kết nối với cơ sở dữ liệu Mongo của bạn.")
except:
    LOGGER(__name__).error("Không thể kết nối với Cơ sở dữ liệu Mongo của bạn.")
    exit()
