import math
import time
from pyrogram.types import InlineKeyboardButton
from pyrogram.enums import ButtonStyle
from VenomMusic import app
import config
from config import SUPPORT_CHAT, SUPPORT_CHANNEL
from VenomMusic.utils.formatters import time_to_seconds


def get_button_style(offset=0):
    """Get button style that changes EVERY SECOND with an offset for variety"""
    # हर सेकंड स्टाइल बदलने के लिए % 3 का इस्तेमाल किया है
    cycle = (int(time.time()) + offset) % 3
    if cycle == 0:
        return ButtonStyle.PRIMARY   # नीला
    elif cycle == 1:
        return ButtonStyle.SUCCESS   # हरा
    else:
        return ButtonStyle.DANGER    # लाल

def track_markup(_, videoid, user_id, channel, fplay):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
                style=get_button_style(0), # नीला / बदलता हुआ
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
                style=get_button_style(1), # हरा / बदलता हुआ
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
                style=get_button_style(2), # लाल / बदलता हुआ
            )
        ],
    ]
    return buttons


def stream_markup_timer(_, chat_id, played, dur):
    played_sec = time_to_seconds(played)
    duration_sec = time_to_seconds(dur)

    remaining_sec = duration_sec - played_sec
    if remaining_sec < 0:
        remaining_sec = 0

    rem_min = remaining_sec // 60
    rem_sec = remaining_sec % 60
    remaining = f"{rem_min:02d}:{rem_sec:02d}"

    percentage = (played_sec / duration_sec) * 100 if duration_sec else 0
    umm = math.floor(percentage)

    if 0 < umm <= 10:
        bar = "⚪─────────"
    elif 10 < umm < 20:
        bar = "━⚪────────"
    elif 20 <= umm < 30:
        bar = "━━⚪───────"
    elif 30 <= umm < 40:
        bar = "━━━⚪──────"
    elif 40 <= umm < 50:
        bar = "━━━━⚪─────"
    elif 50 <= umm < 60:
        bar = "━━━━━⚪────"
    elif 60 <= umm < 70:
        bar = "━━━━━━⚪───"
    elif 70 <= umm < 80:
        bar = "━━━━━━━⚪──"
    elif 80 <= umm < 95:
        bar = "━━━━━━━━⚪─"
    else:
        bar = "━━━━━━━━━⚪"

    buttons = [
        [
            InlineKeyboardButton(
                text=f"{played} {bar} {dur}",
                callback_data="GetTimer",
                style=get_button_style(0),
                icon_custom_emoji_id=5204046146955153467
            )
        ],    
    
        [
            InlineKeyboardButton(
                text="",
                callback_data=f"ADMIN Resume|{chat_id}",
                icon_custom_emoji_id=5409222721869459068,
                style=get_button_style(1), 
            ),

            InlineKeyboardButton(
                text="",
                callback_data=f"ADMIN Pause|{chat_id}",
                icon_custom_emoji_id=5409042015415448331,
                style=get_button_style(2), 
            ),

            InlineKeyboardButton(
                text="‣‣I",
                callback_data=f"ADMIN Skip|{chat_id}",
                style=get_button_style(0), 
            ),

            InlineKeyboardButton(
                text="",
                callback_data=f"ADMIN Stop|{chat_id}",
                icon_custom_emoji_id=5408832111773757273,
                style=get_button_style(1), 
            ),
        ],
        [
            InlineKeyboardButton(
                text="ᴜᴘᴅᴀᴛᴇs",
                url=SUPPORT_CHANNEL,
                style=get_button_style(2),
                icon_custom_emoji_id=6008220984346152956,
            ),

            InlineKeyboardButton(
                text="sᴜᴘᴘᴏʀᴛ",
                url=SUPPORT_CHAT,
                style=get_button_style(0),
                icon_custom_emoji_id=5456623351042694411,
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


def stream_markup(_, chat_id):
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


def playlist_markup(_, videoid, user_id, ptype, channel, fplay):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"VenomPlaylists {videoid}|{user_id}|{ptype}|a|{channel}|{fplay}",
                style=get_button_style(0),
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"VenomPlaylists {videoid}|{user_id}|{ptype}|v|{channel}|{fplay}",
                style=get_button_style(1),
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
                style=get_button_style(2),
            ),
        ],
    ]
    return buttons


def livestream_markup(_, videoid, user_id, mode, channel, fplay):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_3"],
                callback_data=f"LiveStream {videoid}|{user_id}|{mode}|{channel}|{fplay}",
                style=get_button_style(0),
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
                style=get_button_style(1),
            ),
        ],
    ]
    return buttons


def slider_markup(_, videoid, user_id, query, query_type, channel, fplay):
    query = f"{query[:20]}"
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
                style=get_button_style(0),
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
                style=get_button_style(1),
            ),
        ],
        [
            InlineKeyboardButton(
                text="◁",
                callback_data=f"slider B|{query_type}|{query}|{user_id}|{channel}|{fplay}",
                style=get_button_style(2),
            ),
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {query}|{user_id}",
                style=get_button_style(0),
            ),
            InlineKeyboardButton(
                text="▷",
                callback_data=f"slider F|{query_type}|{query}|{user_id}|{channel}|{fplay}",
                style=get_button_style(1),
            ),
        ],
    ]
    return buttons
