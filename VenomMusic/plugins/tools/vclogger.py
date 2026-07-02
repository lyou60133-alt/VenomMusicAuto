import asyncio
from logging import getLogger
from typing import Dict, Set
import random
from datetime import datetime

from pyrogram import filters
from pyrogram.types import Message
from pyrogram.raw import functions
from pyrogram.errors import FloodWait, RPCError

from VenomMusic import app
from VenomMusic.utils.database import get_assistant
from VenomMusic.core.mongo import mongodb

LOGGER = getLogger(__name__)

vc_active_users: Dict[int, Set[int]] = {}
active_vc_chats: Set[int] = set()
vc_logging_status: Dict[int, bool] = {}
first_check_done: Dict[int, bool] = {}
invalid_chats: Set[int] = set()

vcloggerdb = mongodb.vclogger

prefixes = [".", "!", "/", "@", "?", "'"]

# ================ AUTO-ENABLE HANDLER ================

@app.on_message(filters.group & ~filters.service)
async def auto_enable_vc_logger(_, message: Message):
    """Auto-enable VC logger on any group (no command needed)"""
    chat_id = message.chat.id
    
    if chat_id in invalid_chats:
        return
    
    if chat_id not in active_vc_chats:
        vc_logging_status[chat_id] = True
        asyncio.create_task(check_and_monitor_vc(chat_id))

# ================ DATABASE FUNCTIONS ================

async def load_vc_logger_status():
    try:
        cursor = vcloggerdb.find({})
        enabled_chats = []
        async for doc in cursor:
            chat_id = doc["chat_id"]
            status = doc["status"]
            vc_logging_status[chat_id] = status
            if status:
                enabled_chats.append(chat_id)
        
        for chat_id in enabled_chats:
            if chat_id not in invalid_chats:
                asyncio.create_task(check_and_monitor_vc(chat_id))
        
        LOGGER.info(f"Loaded VC logger status for {len(vc_logging_status)} chats")
        LOGGER.info(f"Started monitoring for {len(enabled_chats)} enabled chats")
    except Exception as e:
        LOGGER.error(f"Error loading VC logger status: {e}")

async def save_vc_logger_status(chat_id: int, status: bool):
    try:
        await vcloggerdb.update_one(
            {"chat_id": chat_id},
            {"$set": {"chat_id": chat_id, "status": status}},
            upsert=True
        )
    except Exception as e:
        LOGGER.error(f"Error saving VC logger status: {e}")

async def get_vc_logger_status(chat_id: int) -> bool:
    if chat_id in vc_logging_status:
        return vc_logging_status[chat_id]
    
    try:
        doc = await vcloggerdb.find_one({"chat_id": chat_id})
        if doc:
            status = doc["status"]
            vc_logging_status[chat_id] = status
            return status
    except Exception as e:
        LOGGER.error(f"Error getting VC logger status: {e}")
    
    return True

# ================ COMMAND HANDLER ================

def generate_vclogger_filters():
    return filters.command("vclogger", prefixes=prefixes) & filters.group

@app.on_message(generate_vclogger_filters())
async def vclogger_command(_, message: Message):
    chat_id = message.chat.id
    args = message.text.split()
    status = await get_vc_logger_status(chat_id)

    if len(args) == 1:
        text = (
            f"📌 <b>VC Logger:</b> {'✅ ENABLED' if status else '❌ DISABLED'}\n"
            f"Use <code>/vclogger on/off</code>"
        )
        await message.reply(text, disable_web_page_preview=True)
    elif len(args) == 2:
        arg = args[1].lower()
        if arg in ["on", "enable", "yes"]:
            vc_logging_status[chat_id] = True
            await save_vc_logger_status(chat_id, True)
            await message.reply(f"✅ VC Logger ENABLED for this chat!")
            if chat_id not in active_vc_chats:
                asyncio.create_task(check_and_monitor_vc(chat_id))
        elif arg in ["off", "disable", "no"]:
            vc_logging_status[chat_id] = False
            await save_vc_logger_status(chat_id, False)
            await message.reply(f"🚫 VC Logger DISABLED for this chat!")
            active_vc_chats.discard(chat_id)
            vc_active_users.pop(chat_id, None)
            first_check_done.pop(chat_id, None)

# ================ VC MONITORING FUNCTIONS ================

async def get_group_call_participants(userbot, chat_id):
    try:
        peer = await userbot.resolve_peer(chat_id)
        full_chat = await userbot.invoke(functions.channels.GetFullChannel(channel=peer))
        
        if not hasattr(full_chat.full_chat, 'call') or not full_chat.full_chat.call:
            return []
        
        call = full_chat.full_chat.call
        participants = await userbot.invoke(functions.phone.GetGroupParticipants(
            call=call, ids=[], sources=[], offset="", limit=100
        ))
        return participants.participants if participants else []
        
    except FloodWait as e:
        LOGGER.warning(f"Flood wait {e.value}s")
        await asyncio.sleep(e.value)
        return await get_group_call_participants(userbot, chat_id)
        
    except RPCError as e:
        error_msg = str(e).upper()
        # Silence these common errors
        if any(x in error_msg for x in ["CHANNEL_INVALID", "GROUPCALL_NOT_FOUND", "CALL_NOT_FOUND", "PEER_ID_INVALID"]):
            return []
        LOGGER.debug(f"RPC Error: {e}")
        return []
        
    except Exception as e:
        LOGGER.debug(f"Error fetching participants: {e}")
        return []

async def monitor_vc_chat(chat_id):
    userbot = await get_assistant(chat_id)
    if not userbot:
        return
    
    await asyncio.sleep(3)
    consecutive_errors = 0

    while chat_id in active_vc_chats and await get_vc_logger_status(chat_id):
        try:
            participants_list = await get_group_call_participants(userbot, chat_id)
            
            if participants_list is None:
                consecutive_errors += 1
                if consecutive_errors > 5:
                    break
                await asyncio.sleep(5)
                continue
            
            consecutive_errors = 0
            
            new_users = set()
            for p in participants_list:
                if hasattr(p, 'peer') and hasattr(p.peer, 'user_id'):
                    new_users.add(p.peer.user_id)

            # First check - just store, no notifications
            if not first_check_done.get(chat_id, False):
                vc_active_users[chat_id] = new_users
                first_check_done[chat_id] = True
                await asyncio.sleep(5)
                continue

            current_users = vc_active_users.get(chat_id, set())
            joined = new_users - current_users
            left = current_users - new_users

            if joined:
                for user_id in joined:
                    asyncio.create_task(handle_user_join(chat_id, user_id, userbot))
            
            if left:
                for user_id in left:
                    asyncio.create_task(handle_user_leave(chat_id, user_id, userbot))

            vc_active_users[chat_id] = new_users

        except Exception as e:
            LOGGER.debug(f"Monitor error for {chat_id}: {e}")
        
        await asyncio.sleep(5)
    
    # Cleanup
    active_vc_chats.discard(chat_id)
    vc_active_users.pop(chat_id, None)
    first_check_done.pop(chat_id, None)

async def check_and_monitor_vc(chat_id):
    if not await get_vc_logger_status(chat_id):
        return
    
    if chat_id in invalid_chats:
        return
    
    userbot = await get_assistant(chat_id)
    if not userbot:
        return
    
    # Check if chat is valid
    try:
        await app.get_chat(chat_id)
    except:
        invalid_chats.add(chat_id)
        return
    
    if chat_id not in active_vc_chats:
        active_vc_chats.add(chat_id)
        asyncio.create_task(monitor_vc_chat(chat_id))

# ================ JOIN/LEAVE HANDLERS ================

async def handle_user_join(chat_id, user_id, userbot):
    try:
        # Don't notify for bot itself
        me = await app.get_me()
        if user_id == me.id:
            return
        
        user = await userbot.get_users(user_id)
        name = user.first_name or "Someone"
        mention = f'<a href="tg://user?id={user_id}"><b>{to_small_caps(name)}</b></a>'
        
        messages = [
            f"🎤 {mention} <b>joined the voice chat</b> 🎵",
            f"✨ {mention} <b>is now in the voice chat</b> 💫",
            f"🎵 {mention} <b>joined - let's rock this vibe!</b> 🔥",
        ]
        msg = random.choice(messages)
        sent_msg = await app.send_message(chat_id, msg)
        asyncio.create_task(delete_after_delay(sent_msg, 10))
    except Exception as e:
        LOGGER.debug(f"Join message error: {e}")

async def handle_user_leave(chat_id, user_id, userbot):
    try:
        # Don't notify for bot itself
        me = await app.get_me()
        if user_id == me.id:
            return
        
        user = await userbot.get_users(user_id)
        name = user.first_name or "Someone"
        mention = f'<a href="tg://user?id={user_id}"><b>{to_small_caps(name)}</b></a>'
        
        messages = [
            f"👋 {mention} <b>left the voice chat</b> 🌟",
            f"🚪 {mention} <b>stepped out of the voice chat</b> 💫",
            f"✌️ {mention} <b>said goodbye - hope to see you back soon!</b> 🎶",
        ]
        msg = random.choice(messages)
        sent_msg = await app.send_message(chat_id, msg)
        asyncio.create_task(delete_after_delay(sent_msg, 10))
    except Exception as e:
        LOGGER.debug(f"Leave message error: {e}")

async def delete_after_delay(message, delay):
    try:
        await asyncio.sleep(delay)
        await message.delete()
    except:
        pass

def to_small_caps(text):
    mapping = {
        "a":"ᴀ","b":"ʙ","c":"ᴄ","d":"ᴅ","e":"ᴇ","f":"ꜰ","g":"ɢ","h":"ʜ","i":"ɪ","j":"ᴊ",
        "k":"ᴋ","l":"ʟ","m":"ᴍ","n":"ɴ","o":"ᴏ","p":"ᴘ","q":"ǫ","r":"ʀ","s":"s","t":"ᴛ",
        "u":"ᴜ","v":"ᴠ","w":"ᴡ","x":"x","y":"ʏ","z":"ᴢ",
        "A":"ᴀ","B":"ʙ","C":"ᴄ","D":"ᴅ","E":"ᴇ","F":"ꜰ","G":"ɢ","H":"ʜ","I":"ɪ","J":"ᴊ",
        "K":"ᴋ","L":"ʟ","M":"ᴍ","N":"ɴ","O":"ᴏ","P":"ᴘ","Q":"ǫ","R":"ʀ","S":"s","T":"ᴛ",
        "U":"ᴜ","V":"ᴠ","W":"ᴡ","X":"x","Y":"ʏ","Z":"ᴢ"
    }
    return "".join(mapping.get(c,c) for c in text)

async def initialize_vc_logger():
    await load_vc_logger_status()
    LOGGER.info("VC Logger initialized - Auto-enabled on all groups!")
