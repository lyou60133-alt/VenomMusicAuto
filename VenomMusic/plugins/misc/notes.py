import random
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from pyrogram.enums import ChatMemberStatus

from VenomMusic import app
from config import BOT_USERNAME
from VenomMusic.utils.venom_ban import admin_filter
from VenomMusic.mongo.notesdb import *
from VenomMusic.utils.notes_func import GetNoteMessage, exceNoteMessageSender, privateNote_and_admin_checker
from VenomMusic.utils.yumidb import user_admin

# --- HELPERS ---
PRIVATE_NOTES_TRUE = ['on', 'true', 'yes', 'y']
PRIVATE_NOTES_FALSE = ['off', 'false', 'no', 'n']

@app.on_message(filters.command("save") & admin_filter)
@user_admin
async def _save(client, message):
    chat_id = message.chat.id
    chat_title = message.chat.title
    
    if message.reply_to_message:
        if len(message.command) < 2:
            return await message.reply_text("Usage: Reply to a message with `/save [notename]`")
        note_name = message.command[1].lower()
    else:
        if len(message.command) < 3:
            return await message.reply_text("Usage: `/save [notename] [content]`")
        note_name = message.command[1].lower()

    content, text, data_type = GetNoteMessage(message)
    await SaveNote(chat_id, note_name, content, text, data_type)
    await message.reply_text(f"✅ Saved note `#{note_name}` in **{chat_title}**.")

@app.on_message(filters.command("get") & filters.group)
async def _getnote(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: `/get [notename]`")
    
    chat_id = message.chat.id
    note_name = message.command[1].lower()
    
    if not await isNoteExist(chat_id, note_name):
        return await message.reply_text("❌ This note doesn't exist.")
    
    await send_note(message, note_name)

@app.on_message(filters.regex(pattern=(r"^#[^\s]+")) & filters.group)
async def regex_get_note(client, message):
    # FIX: Check if message.text exists to avoid NoneType.split() error
    if not message.text:
        return
        
    chat_id = message.chat.id
    # Extract note name after '#'
    note_name = message.text.split()[0].replace('#', '').lower()
    
    if await isNoteExist(chat_id, note_name):
        await send_note(message, note_name)

@app.on_message(filters.command("privatenotes") & filters.group)
@user_admin
async def PrivateNote(client, message):
    chat_id = message.chat.id
    if len(message.command) >= 2:
        input_val = message.command[1].lower()
        if input_val in PRIVATE_NOTES_TRUE:
            await set_private_note(chat_id, True)
            await message.reply("🔒 Private notes enabled. I will now send notes in PM.")
        elif input_val in PRIVATE_NOTES_FALSE:
            await set_private_note(chat_id, False)
            await message.reply("🔓 Private notes disabled. I will send notes in the group.")
        else:
            await message.reply(f"Invalid value: `{input_val}`. Use yes/no/on/off.")
    else:
        is_on = await is_pnote_on(chat_id)
        status = "Enabled (PM)" if is_on else "Disabled (Group)"
        await message.reply(f"Current Private Notes status: **{status}**")

@app.on_message(filters.command("clear") & admin_filter)
@user_admin
async def Clear_Note(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: `/clear [notename]`")
    
    chat_id = message.chat.id 
    note_name = message.command[1].lower()

    if await isNoteExist(chat_id, note_name):
        await ClearNote(chat_id, note_name)
        await message.reply_text(f"🗑 Deleted note `#{note_name}`.")
    else:
        await message.reply_text("Note not found.")

@app.on_message(filters.command("clearall") & admin_filter)
async def ClearAll_Note(client, message):
    chat_id = message.chat.id 
    user = await client.get_chat_member(chat_id, message.from_user.id)
    
    if user.status != ChatMemberStatus.OWNER:
        return await message.reply_text("Only the Group Owner can clear all notes!") 

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Confirm Delete All", callback_data=f"clearallnotes_clear_{message.from_user.id}_{chat_id}")],
        [InlineKeyboardButton("Cancel", callback_data=f"clearallnotes_cancel_{message.from_user.id}")]
    ])
    await message.reply(f"⚠️ Are you sure you want to delete **ALL** notes in this chat?", reply_markup=keyboard)

@app.on_callback_query(filters.regex("^clearallnotes_"))
async def ClearAllCallback(client, callback_query: CallbackQuery):
    data = callback_query.data.split('_')
    action = data[1]
    owner_id = int(data[2])
    
    if callback_query.from_user.id != owner_id:
        return await callback_query.answer("This is not for you!", show_alert=True)

    if action == 'clear':
        chat_id = int(data[3])
        await ClearAllNotes(chat_id)
        await callback_query.edit_message_text("✅ All notes have been deleted.")
    else:
        await callback_query.edit_message_text("❌ Action cancelled.")

@app.on_message(filters.command(['notes', 'saved']) & filters.group)
async def Notes(client, message):
    chat_id = message.chat.id
    notes_list = await NoteList(chat_id)
    
    if not notes_list:
        return await message.reply_text(f"No notes saved in **{message.chat.title}**.")
    
    msg = f"📝 **Notes in {message.chat.title}:**\n\n"
    for note in notes_list:
        msg += f" • `#{note}`\n"
    
    msg += "\nRetrieve with `/get name` or `#name`"
    await message.reply_text(msg)

# --- SEND NOTE LOGIC ---
async def send_note(message: Message, note_name: str):
    chat_id = message.chat.id  
    content, text, data_type = await GetNote(chat_id, note_name)
    privateNote, allow = await privateNote_and_admin_checker(message, text)   
    
    if not allow:
        return

    # Check if Private Notes setting is ON for the chat
    pnote_status = await is_pnote_on(chat_id)
    
    if pnote_status or privateNote:
        await PrivateNoteButton(message, chat_id, note_name)
    else:
        await exceNoteMessageSender(message, note_name)

async def PrivateNoteButton(message, chat_id, note_name):
    btn = InlineKeyboardMarkup([[
        InlineKeyboardButton("View Note 📝", url=f"https://t.me/{BOT_USERNAME}?start=note_{chat_id}_{note_name}")
    ]])
    await message.reply(f"Click the button below to view the note `#{note_name}` in private chat.", reply_markup=btn)
