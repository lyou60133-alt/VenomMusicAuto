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


def stats_buttons(_, status):
    # जो यूजर्स सुडो नहीं हैं उनके लिए डायनामिक बटन
    not_sudo = [
        InlineKeyboardButton(
            text=_["SA_B_1"],
            callback_data="TopOverall",
            style=get_button_style(0),
        )
    ]
    # सुडो यूजर्स के लिए रंग-बिरंगा कॉम्बो
    sudo = [
        InlineKeyboardButton(
            text=_["SA_B_2"],
            callback_data="bot_stats_sudo",
            style=get_button_style(0),
        ),
        InlineKeyboardButton(
            text=_["SA_B_3"],
            callback_data="TopOverall",
            style=get_button_style(1),
        ),
    ]
    upl = InlineKeyboardMarkup(
        [
            sudo if status else not_sudo,
            [
                # Close बटन (अलग ऑफसेट के साथ बदलता हुआ रंग)
                InlineKeyboardButton(
                    text=_["CLOSE_BUTTON"],
                    callback_data="close",
                    style=get_button_style(2),
                ),
            ],
        ]
    )
    return upl


def back_stats_buttons(_):
    upl = InlineKeyboardMarkup(
        [
            [
                # Back और Close बटन्स के लिए अलग-अलग ऑफसेट
                InlineKeyboardButton(
                    text=_["BACK_BUTTON"],
                    callback_data="stats_back",
                    style=get_button_style(0),
                ),
                InlineKeyboardButton(
                    text=_["CLOSE_BUTTON"],
                    callback_data="close",
                    style=get_button_style(1),
                ),
            ],
        ]
    )
    return upl
