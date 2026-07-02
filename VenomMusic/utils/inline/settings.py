import time
from typing import Union
from pyrogram.types import InlineKeyboardButton
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


def setting_markup(_):
    buttons = [
        [
            InlineKeyboardButton(text=_["ST_B_1"], callback_data="AU", style=get_button_style(0)),
            InlineKeyboardButton(text=_["ST_B_3"], callback_data="LG", style=get_button_style(1)),
        ],
        [
            InlineKeyboardButton(text=_["ST_B_2"], callback_data="PM", style=get_button_style(2)),
        ],
        [
            InlineKeyboardButton(text=_["ST_B_4"], callback_data="VM", style=get_button_style(0)),
        ],
        [
            InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close", style=get_button_style(1)),
        ],
    ]
    return buttons


def vote_mode_markup(_, current, mode: Union[bool, str] = None):
    buttons = [
        [
            InlineKeyboardButton(text="Vᴏᴛɪɴɢ ᴍᴏᴅᴇ ➜", callback_data="VOTEANSWER", style=get_button_style(0)),
            InlineKeyboardButton(
                text=_["ST_B_5"] if mode == True else _["ST_B_6"],
                callback_data="VOMODECHANGE",
                style=get_button_style(1),
            ),
        ],
        [
            InlineKeyboardButton(text="-2", callback_data="FERRARIUDTI M", style=get_button_style(2)),
            InlineKeyboardButton(
                text=f"ᴄᴜʀʀᴇɴᴛ : {current}",
                callback_data="ANSWERVOMODE",
                style=get_button_style(0),
            ),
            InlineKeyboardButton(text="+2", callback_data="FERRARIUDTI A", style=get_button_style(1)),
        ],
        [
            InlineKeyboardButton(text=_["BACK_BUTTON"], callback_data="settings_helper", style=get_button_style(2)),
            InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close", style=get_button_style(0)),
        ],
    ]
    return buttons


def auth_users_markup(_, status: Union[bool, str] = None):
    buttons = [
        [
            InlineKeyboardButton(text=_["ST_B_7"], callback_data="AUTHANSWER", style=get_button_style(0)),
            InlineKeyboardButton(
                text=_["ST_B_8"] if status == True else _["ST_B_9"],
                callback_data="AUTH",
                style=get_button_style(1),
            ),
        ],
        [
            InlineKeyboardButton(text=_["ST_B_1"], callback_data="AUTHLIST", style=get_button_style(2)),
        ],
        [
            InlineKeyboardButton(text=_["BACK_BUTTON"], callback_data="settings_helper", style=get_button_style(0)),
            InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close", style=get_button_style(1)),
        ],
    ]
    return buttons


def playmode_users_markup(
    _,
    Direct: Union[bool, str] = None,
    Group: Union[bool, str] = None,
    Playtype: Union[bool, str] = None,
):
    buttons = [
        [
            InlineKeyboardButton(text=_["ST_B_10"], callback_data="SEARCHANSWER", style=get_button_style(0)),
            InlineKeyboardButton(
                text=_["ST_B_11"] if Direct == True else _["ST_B_12"],
                callback_data="MODECHANGE",
                style=get_button_style(1),
            ),
        ],
        [
            InlineKeyboardButton(text=_["ST_B_13"], callback_data="AUTHANSWER", style=get_button_style(2)),
            InlineKeyboardButton(
                text=_["ST_B_8"] if Group == True else _["ST_B_9"],
                callback_data="CHANNELMODECHANGE",
                style=get_button_style(0),
            ),
        ],
        [
            InlineKeyboardButton(text=_["ST_B_14"], callback_data="PLAYTYPEANSWER", style=get_button_style(1)),
            InlineKeyboardButton(
                text=_["ST_B_8"] if Playtype == True else _["ST_B_9"],
                callback_data="PLAYTYPECHANGE",
                style=get_button_style(2),
            ),
        ],
        [
            InlineKeyboardButton(text=_["BACK_BUTTON"], callback_data="settings_helper", style=get_button_style(0)),
            InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close", style=get_button_style(1)),
        ],
    ]
    return buttons
