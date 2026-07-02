from VenomMusic import app
from VenomMusic.utils.database import get_assistant
from pyrogram import filters
from pyrogram.types import Message

@app.on_message(filters.command(["leavevc", "leave"], ["/", "!", "."]))
async def leave_vc(_, message: Message):
    chat_id = message.chat.id
    assistant = await get_assistant(chat_id)
    
    if assistant:
        try:
            await assistant.leave_voice_call(chat_id)
            await message.reply("✅ Left voice chat successfully!")
        except Exception as e:
            await message.reply(f"❌ Error: {e}")
    else:
        await message.reply("❌ Assistant not found!")
