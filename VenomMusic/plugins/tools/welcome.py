import asyncio
from logging import getLogger
import os
import random
import time
from typing import Optional, Union

from pyrogram import Client, enums, filters
from pyrogram.enums import ChatMemberStatus, ParseMode
from pyrogram.errors import RPCError
from pyrogram.types import ChatMemberUpdated, InlineKeyboardButton, InlineKeyboardMarkup

from VenomMusic import app
from VenomMusic.misc import SUDOERS
from VenomMusic.mongo.afkdb import PROCESS
from VenomMusic.utils.database import add_served_chat, get_assistant, is_active_chat
from VenomMusic.utils.venom_ban import admin_filter
from pyrogram.enums import ButtonStyle

LOGGER = getLogger(__name__)

# ❗ APNI WELCOME VIDEO KI TELEGRAM LINK YAHAN PASTE KAREIN ❗
WELCOME_VIDEO_URL = "https://files.catbox.moe/9iom66.mp4" 


def get_button_style(offset=0):
    """हर सेकंड स्टाइल बदलने के लिए % 3 का इस्तेमाल किया है"""
    cycle = (int(time.time()) + offset) % 3
    if cycle == 0:
        return ButtonStyle.PRIMARY   # नीला
    elif cycle == 1:
        return ButtonStyle.SUCCESS   # हरा
    else:
        return ButtonStyle.DANGER    # लाल


# --------------------------------------------------------------------------------- #
class WelDatabase:
    def __init__(self):
        self.data = {}

    async def find_one(self, chat_id):
        return chat_id in self.data

    async def add_wlcm(self, chat_id):
        if chat_id not in self.data:
            self.data[chat_id] = {"state": "on"}  # Default state is "on"

    async def rm_wlcm(self, chat_id):
        if chat_id in self.data:
            del self.data[chat_id]

wlcm = WelDatabase()

class temp:
    ME = None
    CURRENT = 2
    CANCEL = False
    MELCOW = {}
    U_NAME = None
    B_NAME = None


@app.on_message(filters.command("welcome") & ~filters.private)
async def auto_state(_, message):
    usage = "**υsᴧɢє:**\n**⦿ /welcome [on|off]**"
    if len(message.command) == 1:
        return await message.reply_text(usage)

    chat_id = message.chat.id
    user = await app.get_chat_member(chat_id, message.from_user.id)
    if user.status in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER):
        A = await wlcm.find_one(chat_id)
        state = message.text.split(None, 1)[1].strip().lower()
        if state == "off":
            if A:
                await message.reply_text("**ᴡєʟᴄᴏϻє ηᴏᴛɪϝɪᴄᴧᴛɪᴏη ᴧʟʀєᴧ─ᴅʏ ᴅɪsᴧʙʟєᴅ !**")
            else:
                await wlcm.add_wlcm(chat_id)
                await message.reply_text(f"**ᴅɪsᴧʙʟєᴅ ᴡєʟᴄᴏϻє ɪη** {message.chat.title}")
        elif state == "on":
            if not A:
                await message.reply_text("**єηᴧʙʟєᴅ ᴡєʟᴄᴏϻє ηᴏᴛɪϝɪᴄᴧᴛɪᴏη.**")
            else:
                await wlcm.rm_wlcm(chat_id)
                await message.reply_text(f"**єηᴧʙʟєᴅ ᴡєʟᴄᴏϻє ɪη** {message.chat.title}")
        else:
            await message.reply_text(usage)
    else:
        await message.reply("**sᴏʀʀʏ ᴏηʟʏ ᴧᴅϻɪηs ᴄᴧη єηᴧʙʟє ᴡєʟᴄᴏϻє!**")


@app.on_chat_member_updated(filters.group, group=-3)
async def greet_new_member(_, member: ChatMemberUpdated):
    chat_id = member.chat.id
    group_name = member.chat.title  # Group ka naam nikalne ke liye
    count = await app.get_chat_members_count(chat_id)
    A = await wlcm.find_one(chat_id)
    if A:
        return

    if member.new_chat_member and not member.old_chat_member and member.new_chat_member.status != "kicked":
        user = member.new_chat_member.user

        try:
            button_text = "✙ ᴋɪᴅηᴧᴘ ϻє ✙"
            add_link = f"https://t.me/{app.username}?startgroup=true"

            # 📝 Aapka bataya hua custom text format + Group name configuration:
            caption_text = f"""
**⎊─────☵ ᴡєʟᴄᴏϻє ᴛᴏ ☵─────⎊**
📋 **ɢʀᴏυᴘ ⧽** {group_name}
**▬▭▬▭▬▭▬▭▬▭▬▭▬▭▬**
☉ **ηᴧϻє ⧽** {user.mention}
☉ **ɪᴅ ⧽** `{user.id}`
☉ **υ_ηᴧϻє ⧽** @{user.username if user.username else 'None'}
☉ **ᴛᴏᴛᴧʟ ϻєϻʙєʀs ⧽** {count}
**▬▭▬▭▬▭▬▭▬▭▬▭▬▭▬**
**⎉──────▢✭ 侖 ✭▢──────⎉**
"""

            # 🎬 Video ke sath aapka custom text caption bhejega aur ye permanent rahega
            await app.send_video(
                chat_id,
                video=WELCOME_VIDEO_URL,
                caption=caption_text,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(text=button_text, url=add_link, style=get_button_style(0))],
                ])
            )

        except Exception as e:
            LOGGER.error(e)
