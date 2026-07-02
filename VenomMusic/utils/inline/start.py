import time
import config
from pyrogram.types import InlineKeyboardButton
from pyrogram.enums import ButtonStyle
from VenomMusic import app


def get_button_style(offset=0):
    """हर सेकंड स्टाइल बदलने के लिए % 3 का इस्तेमाल किया है"""
    cycle = (int(time.time()) + offset) % 3
    if cycle == 0:
        return ButtonStyle.PRIMARY   # नीला
    elif cycle == 1:
        return ButtonStyle.SUCCESS   # हरा
    else:
        return ButtonStyle.DANGER    # लाल


def start_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_1"], 
                url=f"https://t.me/{app.username}?startgroup=true",
                style=get_button_style(0),
            ),
            InlineKeyboardButton(
                text=_["S_B_2"], 
                url=config.SUPPORT_CHAT,
                style=get_button_style(1),
            ),
        ],
    ]
    return buttons


def private_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_3"],
                url=f"https://t.me/{app.username}?startgroup=true",
                style=get_button_style(0),
            )
        ],
        [
            InlineKeyboardButton(
                text=_["S_B_5"], 
                user_id=config.OWNER_ID,
                style=get_button_style(1),
            ),
            InlineKeyboardButton(
                text=_["S_B_6"], 
                url=config.SUPPORT_CHANNEL,
                style=get_button_style(2),
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["S_B_2"], 
                url=config.SUPPORT_CHAT,
                style=get_button_style(0),
            ),
            InlineKeyboardButton(
                text="🌐 ʜᴏsᴛɪɴɢ 🌐", 
                url="https://t.me/VenomHosting",
                style=get_button_style(1),
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["S_B_4"], 
                callback_data="settings_back_helper", 
                style=get_button_style(2),
            ),
        ],
    ]
    return buttons
