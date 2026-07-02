import random
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from config import LOGGER_ID as LOG_GROUP_ID
from VenomMusic import app 
from pyrogram.errors import RPCError, ChatAdminRequired # Added ChatAdminRequired
from typing import Union, Optional
import asyncio, os

photo = [
    "https://telegra.ph/file/1949480f01355b4e87d26.jpg",
    "https://telegra.ph/file/3ef2cc0ad2bc548bafb30.jpg",
    "https://telegra.ph/file/a7d663cd2de689b811729.jpg",
    "https://telegra.ph/file/6f19dc23847f5b005e922.jpg",
    "https://telegra.ph/file/2973150dd62fd27a3a6ba.jpg",
]

@app.on_message(filters.new_chat_members, group=2)
async def join_watcher(_, message):    
    chat = message.chat
    
    # Try-Except block to handle permission issues
    try:
        link = await app.export_chat_invite_link(chat.id)
    except ChatAdminRequired:
        link = "No Permission (Invite Link)"
    except Exception:
        link = "Private/Error"

    for member in message.new_chat_members:
        if member.id == (await app.get_me()).id: # Dynamically get bot ID
            count = await app.get_chat_members_count(chat.id)
            username = f"@{chat.username}" if chat.username else "Private Group"
            added_by = message.from_user.mention if message.from_user else "Unknown User"
            
            msg = (
                f"📝 **ᴍᴜsɪᴄ ʙᴏᴛ ᴀᴅᴅᴇᴅ ɪɴ ᴀ ɴᴇᴡ ɢʀᴏᴜᴘ**\n"
                f"____________________________________\n\n"
                f"📌 **ᴄʜᴀᴛ ɴᴀᴍᴇ:** {chat.title}\n"
                f"🍂 **ᴄʜᴀᴛ ɪᴅ:** `{chat.id}`\n"
                f"🔐 **ᴄʜᴀᴛ ᴜsᴇʀɴᴀᴍᴇ:** {username}\n"
                f"🛰 **ᴄʜᴀᴛ ʟɪɴᴋ:** [ᴄʟɪᴄᴋ]({link})\n"
                f"📈 **ɢʀᴏᴜᴘ ᴍᴇᴍʙᴇʀs:** {count}\n"
                f"🤔 **ᴀᴅᴅᴇᴅ ʙʏ:** {added_by}"
            )
            
            # Inline Keyboard setup
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("sᴇᴇ ɢʀᴏᴜᴘ 👀", url=f"{link}")]
            ]) if "http" in str(link) else None

            await app.send_photo(
                LOG_GROUP_ID, 
                photo=random.choice(photo), 
                caption=msg, 
                reply_markup=keyboard
            )

@app.on_message(filters.left_chat_member)
async def on_left_chat_member(_, message: Message):
    me = await app.get_me()
    if me.id == message.left_chat_member.id:
        remove_by = message.from_user.mention if message.from_user else "Unknown User"
        title = message.chat.title
        username = f"@{message.chat.username}" if message.chat.username else "Private Chat"
        chat_id = message.chat.id
        
        left = (
            f"✫ **<u>#ʟᴇғᴛ_ɢʀᴏᴜᴘ</u>** ✫\n\n"
            f"**ᴄʜᴀᴛ ᴛɪᴛʟᴇ :** {title}\n"
            f"**ᴄʜᴀᴛ ɪᴅ :** `{chat_id}`\n"
            f"**ʀᴇᴍᴏᴠᴇᴅ ʙʏ :** {remove_by}\n"
            f"**ʙᴏᴛ :** @{me.username}"
        )
        await app.send_photo(LOG_GROUP_ID, photo=random.choice(photo), caption=left)
