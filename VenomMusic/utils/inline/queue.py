import time
from typing import Union
from VenomMusic import app
from pyrogram.enums import ButtonStyle
from VenomMusic.utils.formatters import time_to_seconds
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_button_style(offset=0):
    """हर सेकंड स्टाइल बदलने के लिए % 3 का इस्तेमाल किया है"""
    cycle = (int(time.time()) + offset) % 3
    if cycle == 0:
        return ButtonStyle.PRIMARY   # नीला
    elif cycle == 1:
        return ButtonStyle.SUCCESS   # हरा
    else:
        return ButtonStyle.DANGER    # लाल


def queue_markup(
    _,
    DURATION,
    CPLAY,
    videoid,
    played: Union[bool, int] = None,
    dur: Union[bool, int] = None,
):
    not_dur = [
        [
            InlineKeyboardButton(
                text=_["QU_B_1"],
                callback_data=f"GetQueued {CPLAY}|{videoid}",
                style=get_button_style(0),
            ),
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data="close",
                style=get_button_style(1),
            ),
        ]
    ]
    dur_layout = [
        [
            InlineKeyboardButton(
                text=_["QU_B_2"].format(played, dur),
                callback_data="GetTimer",
                style=get_button_style(0),
            )
        ],
        [
            InlineKeyboardButton(
                text=_["QU_B_1"],
                callback_data=f"GetQueued {CPLAY}|{videoid}",
                style=get_button_style(1),
            ),
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data="close",
                style=get_button_style(2),
            ),
        ],
    ]
    # यहाँ पुराने वेरिएबल नाम 'dur' को लेआउट लिस्ट से अलग रखने के लिए 'dur_layout' किया है
    upl = InlineKeyboardMarkup(not_dur if DURATION == "Unknown" else dur_layout)
    return upl


def queue_back_markup(_, CPLAY):
    upl = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=_["BACK_BUTTON"],
                    callback_data=f"queue_back_timer {CPLAY}",
                    style=get_button_style(0),
                ),
                InlineKeyboardButton(
                    text=_["CLOSE_BUTTON"],
                    callback_data="close",
                    style=get_button_style(1),
                ),
            ]
        ]
    )
    return upl


def aq_markup(_, chat_id):
    buttons = [
        [
            InlineKeyboardButton(
                text="",
                callback_data=f"ADMIN Resume|{chat_id}",
                icon_custom_emoji_id=5409222721869459068,
                style=get_button_style(0),
            ),
            InlineKeyboardButton(
                text="",
                callback_data=f"ADMIN Pause|{chat_id}",
                icon_custom_emoji_id=5409042015415448331,
                style=get_button_style(1),
            ),
            InlineKeyboardButton(
                text="‣‣I",
                callback_data=f"ADMIN Skip|{chat_id}",
                style=get_button_style(2),
            ),
            InlineKeyboardButton(
                text="",
                callback_data=f"ADMIN Stop|{chat_id}",
                icon_custom_emoji_id=5408832111773757273,
                style=get_button_style(0),
            ),
        ],
        [
            InlineKeyboardButton(
                text=" ᴄʟᴏsᴇ ", 
                callback_data="close", 
                style=get_button_style(1), 
                icon_custom_emoji_id=5408832111773757273
            )
        ],
    ]
    return buttons
