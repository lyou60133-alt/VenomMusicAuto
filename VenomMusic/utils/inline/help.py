import time
from typing import Union
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
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


def help_pannel(_, START: Union[bool, int] = None):
    first = [
        InlineKeyboardButton(
            text=_["CLOSE_BUTTON"], 
            callback_data="close",
            style=get_button_style(0)
        )
    ]
    second = [
        InlineKeyboardButton(text=_["BACK_PAGE"], callback_data="mbot_cb", style=get_button_style(1)),
        InlineKeyboardButton(text=_["BACK_BUTTON"], callback_data="settingsback_helper", style=get_button_style(2)),
        InlineKeyboardButton(text=_["NEXT_PAGE"], callback_data="mbot_cb", style=get_button_style(0)),
    ]
    mark = second if START else first
    
    upl = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text=_["H_B_1"], callback_data="help_callback hb1", style=get_button_style(0)),
                InlineKeyboardButton(text=_["H_B_2"], callback_data="help_callback hb2", style=get_button_style(1)),
                InlineKeyboardButton(text=_["H_B_3"], callback_data="help_callback hb3", style=get_button_style(2)),
            ],
            [
                InlineKeyboardButton(text=_["H_B_4"], callback_data="help_callback hb4", style=get_button_style(1)),
                InlineKeyboardButton(text=_["H_B_5"], callback_data="help_callback hb5", style=get_button_style(2)),
                InlineKeyboardButton(text=_["H_B_6"], callback_data="help_callback hb6", style=get_button_style(0)),
            ],
            [
                InlineKeyboardButton(text=_["H_B_7"], callback_data="help_callback hb7", style=get_button_style(2)),
                InlineKeyboardButton(text=_["H_B_8"], callback_data="help_callback hb8", style=get_button_style(0)),
                InlineKeyboardButton(text=_["H_B_9"], callback_data="help_callback hb9", style=get_button_style(1)),
            ],
            [
                InlineKeyboardButton(text=_["H_B_10"], callback_data="help_callback hb10", style=get_button_style(0)),
                InlineKeyboardButton(text=_["H_B_11"], callback_data="help_callback hb11", style=get_button_style(1)),
                InlineKeyboardButton(text=_["H_B_12"], callback_data="help_callback hb12", style=get_button_style(2)),
            ],
            [
                InlineKeyboardButton(text=_["H_B_13"], callback_data="help_callback hb13", style=get_button_style(1)),
                InlineKeyboardButton(text=_["H_B_14"], callback_data="help_callback hb14", style=get_button_style(2)),
                InlineKeyboardButton(text=_["H_B_15"], callback_data="help_callback hb15", style=get_button_style(0)),
            ],
            [
                InlineKeyboardButton(text=_["B_B_1"], callback_data="help_callback buy", style=get_button_style(1)),
            ],
            mark,
        ]
    )
    return upl


def help_back_markup(_):
    upl = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=_["BACK_BUTTON"],
                    callback_data="settings_back_helper",
                    style=get_button_style(0),
                ),
            ]
        ]
    )
    return upl


def private_help_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_4"],
                url=f"https://t.me/{app.username}?start=help",
                style=get_button_style(0),
            ),
        ],
    ]
    return buttons
