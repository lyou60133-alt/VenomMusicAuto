from pyrogram import filters
from pyrogram.types import Message

from VenomMusic import app
from VenomMusic.utils.database import autoplay_off, autoplay_on
from VenomMusic.utils.decorators import AdminRightsCheck
from VenomMusic.utils.inline import close_markup
from config import BANNED_USERS


@app.on_message(filters.command(["autoplay"]) & filters.group & ~BANNED_USERS)
@AdminRightsCheck
async def autoplay_toggle(cli, message: Message, _, chat_id):
    usage = _["admin_41"]
    if len(message.command) != 2:
        return await message.reply_text(usage)
    state = message.text.split(None, 1)[1].strip().lower()
    if state in ("enable", "on"):
        await autoplay_on(chat_id)
        return await message.reply_text(
            text=_["admin_42"].format(message.from_user.mention),
            reply_markup=close_markup(_),
        )
    elif state in ("disable", "off"):
        await autoplay_off(chat_id)
        return await message.reply_text(
            text=_["admin_43"].format(message.from_user.mention),
            reply_markup=close_markup(_),
        )
    else:
        return await message.reply_text(usage)
