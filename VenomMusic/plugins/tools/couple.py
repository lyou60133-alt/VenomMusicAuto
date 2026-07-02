import os 
import random
from datetime import datetime 
from telegraph import upload_file
from PIL import Image, ImageDraw
from pyrogram import filters, Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.enums import ChatType, ButtonStyle # ButtonStyle import kiya

# BOT FILE NAME
from VenomMusic import app as app
from VenomMusic.mongo.couples_db import _get_image, get_couple

# Button with Style
POLICE = [
    [
        InlineKeyboardButton(
            text="๏ ᴠᴇɴᴏᴍ ᴍᴜsɪᴄ ๏",
            url=f"https://t.me/venompratapchat",
            style=ButtonStyle.SUCCESS # Green color button
        ),
    ],
]

def dt():
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M")
    dt_list = dt_string.split(" ")
    return dt_list

def dt_tom():
    now = datetime.now()
    # Behtar tarika tomorrow's date nikalne ka
    from datetime import timedelta
    tomorrow_date = now + timedelta(days=1)
    return tomorrow_date.strftime("%d/%m/%Y")

tomorrow = str(dt_tom())
today = str(dt()[0])

@app.on_message(filters.command(["couple", "couples"]))
async def ctest(_, message: Message):
    cid = message.chat.id
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text("ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs.")
    
    try:
         msg = await message.reply_text("✨ **ɢᴇɴᴇʀᴀᴛɪɴɢ ᴄᴏᴜᴘʟᴇs ɪᴍᴀɢᴇ...**")
         
         # GET LIST OF USERS
         list_of_users = []
         async for i in app.get_chat_members(message.chat.id, limit=50):
             if not i.user.is_bot:
               list_of_users.append(i.user.id)

         if len(list_of_users) < 2:
             return await msg.edit("ᴛʜɪs ɢʀᴏᴜᴘ ᴅᴏᴇsɴ'ᴛ ʜᴀᴠᴇ ᴇɴᴏᴜɢʜ ᴍᴇᴍʙᴇʀs ᴛᴏ ᴄʜᴏᴏsᴇ ᴀ ᴄᴏᴜᴘʟᴇ.")

         c1_id = random.choice(list_of_users)
         c2_id = random.choice(list_of_users)
         while c1_id == c2_id:
              c2_id = random.choice(list_of_users)

         photo1 = (await app.get_chat(c1_id)).photo
         photo2 = (await app.get_chat(c2_id)).photo
 
         u1 = await app.get_users(c1_id)
         u2 = await app.get_users(c2_id)
         
         N1 = u1.mention 
         N2 = u2.mention
         
         try:
            p1 = await app.download_media(photo1.big_file_id, file_name=f"pfp_{c1_id}.png")
         except Exception:
            p1 = "VenomMusic/assets/upic.png"
            
         try:
            p2 = await app.download_media(photo2.big_file_id, file_name=f"pfp_{c2_id}.png")
         except Exception:
            p2 = "VenomMusic/assets/upic.png"
            
         img1 = Image.open(f"{p1}")
         img2 = Image.open(f"{p2}")
         img = Image.open("VenomMusic/assets/cppic.png")

         img1 = img1.resize((437, 437))
         img2 = img2.resize((437, 437))

         mask = Image.new('L', img1.size, 0)
         draw = ImageDraw.Draw(mask) 
         draw.ellipse((0, 0) + img1.size, fill=255)

         img1.putalpha(mask)
         img2.putalpha(mask)

         img.paste(img1, (116, 160), img1)
         img.paste(img2, (789, 160), img2)

         img.save(f'test_{cid}.png')
    
         TXT = f"""
**💘 ᴛᴏᴅᴀʏ's ᴄᴏᴜᴘʟᴇ ᴏғ ᴛʜᴇ ᴅᴀʏ 💘**

{N1} + {N2} = 💚

**ɴᴇxᴛ ᴄᴏᴜᴘʟᴇs ᴡɪʟʟ ʙᴇ sᴇʟᴇᴄᴛᴇᴅ ᴏɴ {tomorrow} !!**
"""
    
         await message.reply_photo(
             photo=f"test_{cid}.png", 
             caption=TXT, 
             reply_markup=InlineKeyboardMarkup(POLICE)
         )
         await msg.delete()
         
    except Exception as e:
        print(str(e))
        await message.reply_text(f"ᴇʀʀᴏʀ: {e}")
        
    finally:
        # Cleanup files
        try:
            if os.path.exists(f"pfp_{c1_id}.png"): os.remove(f"pfp_{c1_id}.png")
            if os.path.exists(f"pfp_{c2_id}.png"): os.remove(f"pfp_{c2_id}.png")
            if os.path.exists(f"test_{cid}.png"): os.remove(f"test_{cid}.png")
        except:
            pass

__mod__ = "COUPLES"
__help__ = """
**» /couple** - Get Todays Couples Of The Group In Interactive View
"""
