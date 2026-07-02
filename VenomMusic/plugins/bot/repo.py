from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ButtonStyle # Style ke liye zaroori import
from VenomMusic import app
from config import BOT_USERNAME
from VenomMusic.utils.errors import capture_err
import httpx 

start_txt = """**
✪ ωεℓᴄσмє fσʀ νεηοм ʀєρσѕ ✪

 ➲ ᴀʟʟ ʀᴇᴘᴏ ᴇᴀsɪʟʏ ᴅᴇᴘʟᴏʏ ᴏɴ ʜᴇʀᴏᴋᴜ ᴡɪᴛʜᴏᴜᴛ ᴀɴʏ ᴇʀʀᴏʀ ✰
 
 ➲ ɴᴏ ʜᴇʀᴏᴋᴜ ʙᴀɴ ɪssᴜᴇ ✰
 
 ➲ ɴᴏ ɪᴅ ʙᴀɴ ɪssᴜᴇ ✰
 
 ➲ ᴜɴʟɪᴍɪᴛᴇᴅ ᴅʏɴᴏs ✰
 
 ➲ ʀᴜɴ 24x7 ʟᴀɢ ғʀᴇᴇ ᴡɪᴛʜᴏᴜᴛ sᴛᴏᴘ ✰
 
 ► ɪғ ʏᴏᴜ ғᴀᴄᴇ ᴀɴʏ ᴘʀᴏʙʟᴇᴍ ᴛʜᴇɴ sᴇɴᴅ ss
**"""

@app.on_message(filters.command("repo"))
async def start(_, msg):
    buttons = [
        [ 
            # Add me button ko Green (Success) highlight kiya hai
            InlineKeyboardButton(
                "◉ ᴀᴅᴅ ᴍᴇ ◉", 
                url=f"https://t.me/Venomumusicbot?startgroup=true",
                style=ButtonStyle.SUCCESS
            )
        ],
        [
            # Support aur Owner ke liye Blue (Primary)
            InlineKeyboardButton(
                "◉ sᴜᴘᴘᴏʀᴛ ◉", 
                url="https://t.me/venompratapchat",
                style=ButtonStyle.PRIMARY
            ),
            InlineKeyboardButton(
                "◉ ᴏᴡɴᴇʀ ◉", 
                url="https://t.me/VenomPratap",
                style=ButtonStyle.PRIMARY
            ),
        ],
        [
            # Updates ke liye Green (Success)
            InlineKeyboardButton(
                "◉ ᴜᴘᴅᴀᴛᴇs ◉", 
                url="https://t.me/venomvipbots",
                style=ButtonStyle.SUCCESS
            ),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await msg.reply_photo(
        photo="https://envs.sh/10o.jpg",
        caption=start_txt,
        reply_markup=reply_markup
    )
 
# --------------

@app.on_message(filters.command("repo", prefixes="#"))
@capture_err
async def repo(_, message):
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.github.com/repos/Infamous-Hydra/YaeMiko/contributors")
    
    if response.status_code == 200:
        users = response.json()
        list_of_users = ""
        count = 1
        for user in users:
            list_of_users += f"{count}. [{user['login']}]({user['html_url']})\n"
            count += 1

        text = f"""[𝖱𝖤𝖯𝖮 𝖫𝖨𝖭𝖪](https://github.com/Infamous-Hydra/YaeMiko) | [𝖦𝖱𝖮𝖴𝖯](https://t.me/venompratapchat)
| 𝖢𝖮𝖭𝖳𝖱𝖨𝖡𝖴𝖳𝖮𝖱𝖲 |
----------------
{list_of_users}"""
        await app.send_message(message.chat.id, text=text, disable_web_page_preview=True)
    else:
        await app.send_message(message.chat.id, text="Failed to fetch contributors.")
