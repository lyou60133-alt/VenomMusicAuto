from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.enums import ParseMode, ButtonStyle # Style ke liye zaroori import
from VenomMusic import app
import config

TEXT = f"""
🔒 **Privacy Policy for {app.username} !**

Your privacy is important to us. To learn more about how we collect, use, and protect your data, please review our Privacy Policy here: [Privacy Policy]({config.PRIVACY_LINK}).

If you have any questions or concerns, feel free to reach out to our [support team](https://t.me/VENOMPRATAP).
"""

@app.on_message(filters.command("privacy"))
async def privacy(client, message: Message):
    keyboard = InlineKeyboardMarkup(
        [
            [
                # Privacy Policy button ko Blue (Primary) style diya hai
                InlineKeyboardButton(
                    text="View Privacy Policy", 
                    url=config.PRIVACY_LINK if hasattr(config, 'PRIVACY_LINK') else config.SUPPORT_CHAT,
                    style=ButtonStyle.PRIMARY
                )
            ]
        ]
    )
    await message.reply_text(
        TEXT, 
        reply_markup=keyboard, 
        parse_mode=ParseMode.MARKDOWN, 
        disable_web_page_preview=True
    )
