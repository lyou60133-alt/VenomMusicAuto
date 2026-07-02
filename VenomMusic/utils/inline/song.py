import time
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


def song_markup(_, vidid):
    buttons = [
        [
            # Audio download बटन (अलग ऑफसेट के साथ बदलता हुआ रंग)
            InlineKeyboardButton(
                text=_["SG_B_2"],
                callback_data=f"song_helper audio|{vidid}",
                style=get_button_style(0),
            ),
            # Video download बटन (अलग ऑफसेट के साथ बदलता हुआ रंग)
            InlineKeyboardButton(
                text=_["SG_B_3"],
                callback_data=f"song_helper video|{vidid}",
                style=get_button_style(1),
            ),
        ],
        [
            # Close बटन (अलग ऑफसेट के साथ बदलता हुआ रंग)
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"], 
                callback_data="close",
                style=get_button_style(2),
            ),
        ],
    ]
    return buttons
