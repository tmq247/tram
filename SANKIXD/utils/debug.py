from pyrogram.errors import PeerIdInvalid
import traceback

async def trace_peer_usage(client, chat_id, method="UNKNOWN"):
    try:
        print(f"[TRACE] Đang kiểm tra {method} với chat_id: {chat_id}")
        await client.send_chat_action(chat_id, "typing")
    except PeerIdInvalid:
        print(f"❌ Peer ID không hợp lệ: {chat_id} khi gọi {method}")
        traceback.print_stack(limit=5)
    except Exception as e:
        print(f"⚠️ Lỗi khác tại {method}: {e}")
