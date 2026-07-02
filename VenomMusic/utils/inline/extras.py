import time
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ButtonStyle


def get_button_style(offset=0):
    """हर सेकंड स्टाइल बदलने के लिए % 3 का इस्तेमाल किया है"""
    cycle = (int(time.time()) + offset) % 3
    if cycle == 0:
        return ButtonStyle.PRIMARY   # नीला
    elif cycle == 1:
        return ButtonStyle.SUCCESS   # हरा
    else:
        return ButtonStyle.DANGER    # लाल


def botplaylist_markup(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_9"], 
                url=SUPPORT_CHAT,
                style=get_button_style(0), # सपोर्ट चैट बटन का बदलता रंग
            ),
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"], 
                callback_data="close",
                style=get_button_style(1), # क्लोज बटन का बदलता रंग
            ),
        ],
    ]
    return buttons


def close_markup(_):
    upl = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=_["CLOSE_BUTTON"],
                    callback_data="close",
                    style=get_button_style(0), # सिंगल क्लोज बटन का बदलता रंग
                ),
            ]
        ]
    )
    return upl


def supp_markup(_):
    upl = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=_["S_B_9"],
                    url=SUPPORT_CHAT,
                    style=get_button_style(0), # केवल सपोर्ट बटन का बदलता रंग
                ),
            ]
        ]
    )
    return upl
