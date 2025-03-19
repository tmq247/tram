from asyncio import sleep
from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.errors import MessageDeleteForbidden, RPCError
from pyrogram.types import Message
from SANKIXD.utils.SANKI_ban import admin_filter
from SANKIXD import app


@app.on_message(filters.command("purge") & admin_filter)
async def purge(app: app, msg: Message):
    
    if msg.chat.type != ChatType.SUPERGROUP:
        await msg.reply_text(text="**Tôi không thể xóa tin nhắn trong một nhóm cơ bản để tạo ra siêu nhóm .**")
        return

    if msg.reply_to_message:
        message_ids = list(range(msg.reply_to_message.id, msg.id))

        def divide_chunks(l: list, n: int = 100):
            for i in range(0, len(l), n):
                yield l[i : i + n]

        
        m_list = list(divide_chunks(message_ids))

        try:
            for plist in m_list:
                await app.delete_messages(chat_id=msg.chat.id, message_ids=plist, revoke=True)
                
            await msg.delete()
        except MessageDeleteForbidden:
            await msg.reply_text(text="**Tôi không thể xóa tất cả tin nhắn. Các tin nhắn có thể đã quá cũ, tôi có thể không có quyền xóa, hoặc đây có thể không phải là một siêu nhóm..**")
            return
            
        except RPCError as ef:
            await msg.reply_text(text=f"**Đã xảy ra một số lỗi, báo cáo nó bằng một cách sử dụng** `/bug`<b>Lỗi:</b> <code>{ef}</code>")
        count_del_msg = len(message_ids)
        sumit = await msg.reply_text(text=f"Đã xóa <i>{count_del_msg}</i> tin nhắn")
        await sleep(3)
        await sumit.delete()
        return
    await msg.reply_text("**Trả lời một tin nhắn để bắt đầu xoá đi !**")
    return





@app.on_message(filters.command("spurge") & admin_filter)
async def spurge(app: app, msg: Message):

    if msg.chat.type != ChatType.SUPERGROUP:
        await msg.reply_text(text="**Tôi không thể xóa tin nhắn trong một nhóm cơ bản để tạo ra siêu nhóm**")
        return

    if msg.reply_to_message:
        message_ids = list(range(msg.reply_to_message.id, msg.id))

        def divide_chunks(l: list, n: int = 100):
            for i in range(0, len(l), n):
                yield l[i : i + n]

        m_list = list(divide_chunks(message_ids))

        try:
            for plist in m_list:
                await app.delete_messages(chat_id=msg.chat.id, message_ids=plist, revoke=True)
            await msg.delete()
        except MessageDeleteForbidden:
            await msg.reply_text(text="**ɪKhông thể xóa tất cả tin nhắn. Các tin nhắn có thể quá cũ, tôi có thể không có quyền xóa, hoặc đây có thể không phải là một siêu nhóm.**")
            return
            
        except RPCError as ef:
            await msg.reply_text(text=f"**Đã xảy ra một số lỗi, báo cáo nó bằng một cách sử dụng** `/bug`<b>Lỗi:</b> <code>{ef}</code>")           
            return        
    await msg.reply_text("**Trả lời một tin nhắn để bắt đầu xoá đi !**")
    return


@app.on_message(filters.command("del") & admin_filter)
async def del_msg(app: app, msg: Message):
    if msg.chat.type != ChatType.SUPERGROUP:
        await msg.reply_text(text="**Tôi không thể xóa tin nhắn trong một nhóm cơ bản để tạo ra siêu nhóm.**")
        return        
    if msg.reply_to_message:
        await msg.delete()
        await app.delete_messages(chat_id=msg.chat.id, message_ids=msg.reply_to_message.id)
    else:
        await msg.reply_text(text="**Bạn muốn xóa cái gì?.**")
        return


