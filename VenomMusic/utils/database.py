import random
import os
import json
from typing import Dict, List, Union

import config
from motor.motor_asyncio import AsyncIOMotorClient
from VenomMusic import userbot
from VenomMusic.core.mongo import mongodb
from VenomMusic.misc import db 

authdb = mongodb.adminauth
cleandb = mongodb.cleanmode
queriesdb = mongodb.queries
chatsdb = mongodb.chats
authuserdb = mongodb.authuser
autoenddb = mongodb.autoend
assdb = mongodb.assistants
blacklist_chatdb = mongodb.blacklistChat
blockeddb = mongodb.blockedusers
chatsdb = mongodb.chats
channeldb = mongodb.cplaymode
countdb = mongodb.upcount
gbansdb = mongodb.gban
langdb = mongodb.language
onoffdb = mongodb.onoffper
playmodedb = mongodb.playmode
playtypedb = mongodb.playtypedb
skipdb = mongodb.skipmode
sudoersdb = mongodb.sudoers
usersdb = mongodb.tgusersdb
ignoredb = mongodb.ignorelist 
chattopdb = mongodb.chattopdb 
userdb = mongodb.userdb      
autoplaydb = mongodb.autoplay

# Shifting to memory
active = []
activevideo = []
assistantdict = {}
autoend = {}
count = {}
channelconnect = {}
langm = {}
loop = {}
maintenance = []
nonadmin = {}
pause = {}
playmode = {}
playtype = {}
skipmode = {}
autoplaymode = {}
autoplay_history = {}

# --- FIXED FUNCTIONS ---

async def get_ignored_users() -> list:
    users = []
    async for user in ignoredb.find():
        users.append(user["user_id"])
    return users

async def delete_old_message(chat_id: int):
    try:
        if chat_id in db:
            if "mystic" in db[chat_id][0]:
                await db[chat_id][0]["mystic"].delete()
    except Exception:
        pass

async def get_banned_count() -> int:
    try:
        users = blockeddb.find({"user_id": {"$gt": 0}})
        users_list = await users.to_list(length=100000)
        return len(users_list)
    except Exception:
        return 0

# --- RANKING & TOP FUNCTIONS ---

async def get_particulars(chat_id: int) -> Dict[str, int]:
    ids = await chattopdb.find_one({"chat_id": chat_id})
    return ids["vidid"] if ids else {}

async def get_particular_top(chat_id: int, name: str):
    ids = await get_particulars(chat_id)
    return ids.get(name)

async def update_particular_top(chat_id: int, name: str, vidid: dict):
    ids = await get_particulars(chat_id)
    ids[name] = vidid
    await chattopdb.update_one(
        {"chat_id": chat_id}, {"$set": {"vidid": ids}}, upsert=True
    )

async def get_userss(chat_id: int) -> Dict[str, int]:
    ids = await userdb.find_one({"chat_id": chat_id})
    return ids["vidid"] if ids else {}

async def get_user_top(chat_id: int, name: str):
    ids = await get_userss(chat_id)
    return ids.get(name)

async def update_user_top(chat_id: int, name: str, vidid: dict):
    ids = await get_userss(chat_id)
    ids[name] = vidid
    await userdb.update_one({"chat_id": chat_id}, {"$set": {"vidid": ids}}, upsert=True)

async def get_topp_users() -> dict:
    results = {}
    async for chat in userdb.find({"chat_id": {"$gt": 0}}):
        user_id = chat["chat_id"]
        total = sum(v["spot"] for v in chat.get("vidid", {}).values() if v.get("spot", 0) > 0)
        results[user_id] = total
    return results

# --- CORE FUNCTIONS ---

async def get_assistant_number(chat_id: int) -> str:
    assistant = assistantdict.get(chat_id)
    return assistant

async def get_client(assistant: int):
    if int(assistant) == 1:
        return userbot.one
    elif int(assistant) == 2:
        return userbot.two
    elif int(assistant) == 3:
        return userbot.three
    elif int(assistant) == 4:
        return userbot.four
    elif int(assistant) == 5:
        return userbot.five

async def set_assistant_new(chat_id, number):
    number = int(number)
    await assdb.update_one(
        {"chat_id": chat_id},
        {"$set": {"assistant": number}},
        upsert=True,
    )

async def set_assistant(chat_id):
    from VenomMusic.core.userbot import assistants
    ran_assistant = random.choice(assistants)
    assistantdict[chat_id] = ran_assistant
    await assdb.update_one(
        {"chat_id": chat_id},
        {"$set": {"assistant": ran_assistant}},
        upsert=True,
    )
    userbot = await get_client(ran_assistant)
    return userbot

async def get_assistant(chat_id: int) -> str:
    from VenomMusic.core.userbot import assistants
    assistant = assistantdict.get(chat_id)
    if not assistant:
        dbassistant = await assdb.find_one({"chat_id": chat_id})
        if not dbassistant:
            userbot = await set_assistant(chat_id)
            return userbot
        else:
            got_assis = dbassistant["assistant"]
            if got_assis in assistants:
                assistantdict[chat_id] = got_assis
                userbot = await get_client(got_assis)
                return userbot
            else:
                userbot = await set_assistant(chat_id)
                return userbot
    else:
        if assistant in assistants:
            userbot = await get_client(assistant)
            return userbot
        else:
            userbot = await set_assistant(chat_id)
            return userbot

async def set_calls_assistant(chat_id):
    from VenomMusic.core.userbot import assistants
    ran_assistant = random.choice(assistants)
    assistantdict[chat_id] = ran_assistant
    await assdb.update_one(
        {"chat_id": chat_id},
        {"$set": {"assistant": ran_assistant}},
        upsert=True,
    )
    return ran_assistant

async def group_assistant(self, chat_id: int) -> int:
    from VenomMusic.core.userbot import assistants
    assistant = assistantdict.get(chat_id)
    if not assistant:
        dbassistant = await assdb.find_one({"chat_id": chat_id})
        if not dbassistant:
            assis = await set_calls_assistant(chat_id)
        else:
            assis = dbassistant["assistant"]
            if assis in assistants:
                assistantdict[chat_id] = assis
                assis = assis
            else:
                assis = await set_calls_assistant(chat_id)
    else:
        if assistant in assistants:
            assis = assistant
        else:
            assis = await set_calls_assistant(chat_id)
    if int(assis) == 1:
        return self.one
    elif int(assis) == 2:
        return self.two
    elif int(assis) == 3:
        return self.three
    elif int(assis) == 4:
        return self.four
    elif int(assis) == 5:
        return self.five

async def is_skipmode(chat_id: int) -> bool:
    mode = skipmode.get(chat_id)
    if not mode:
        user = await skipdb.find_one({"chat_id": chat_id})
        if not user:
            skipmode[chat_id] = True
            return True
        skipmode[chat_id] = False
        return False
    return mode

async def skip_on(chat_id: int):
    skipmode[chat_id] = True
    user = await skipdb.find_one({"chat_id": chat_id})
    if user:
        return await skipdb.delete_one({"chat_id": chat_id})

async def skip_off(chat_id: int):
    skipmode[chat_id] = False
    user = await skipdb.find_one({"chat_id": chat_id})
    if not user:
        return await skipdb.insert_one({"chat_id": chat_id})

async def get_upvote_count(chat_id: int) -> int:
    mode = count.get(chat_id)
    if not mode:
        mode = await countdb.find_one({"chat_id": chat_id})
        if not mode:
            return 5
        count[chat_id] = mode["mode"]
        return mode["mode"]
    return mode

async def set_upvotes(chat_id: int, mode: int):
    count[chat_id] = mode
    await countdb.update_one(
        {"chat_id": chat_id}, {"$set": {"mode": mode}}, upsert=True
    )

# --- FIXED AUTOEND FUNCTIONS ---

async def is_autoend() -> bool:
    chat_id = 1234 
    user = await autoenddb.find_one({"chat_id": chat_id})
    return bool(user)

async def autoend_on():
    chat_id = 1234
    user = await autoenddb.find_one({"chat_id": chat_id})
    if not user:
        return await autoenddb.insert_one({"chat_id": chat_id})

async def autoend_off():
    chat_id = 1234
    user = await autoenddb.find_one({"chat_id": chat_id})
    if user:
        return await autoenddb.delete_one({"chat_id": chat_id})

# -------------------------------

async def get_loop(chat_id: int) -> int:
    lop = loop.get(chat_id)
    if not lop:
        return 0
    return lop

async def set_loop(chat_id: int, mode: int):
    loop[chat_id] = mode

async def is_autoplay(chat_id: int) -> bool:
    mode = autoplaymode.get(chat_id)
    if mode is None:
        user = await autoplaydb.find_one({"chat_id": chat_id})
        if not user:
            autoplaymode[chat_id] = False
            return False
        autoplaymode[chat_id] = True
        return True
    return mode

async def autoplay_on(chat_id: int):
    autoplaymode[chat_id] = True
    user = await autoplaydb.find_one({"chat_id": chat_id})
    if not user:
        await autoplaydb.insert_one({"chat_id": chat_id})

async def autoplay_off(chat_id: int):
    autoplaymode[chat_id] = False
    autoplay_history.pop(chat_id, None)
    user = await autoplaydb.find_one({"chat_id": chat_id})
    if user:
        await autoplaydb.delete_one({"chat_id": chat_id})

async def get_autoplay_history(chat_id: int) -> list:
    return autoplay_history.get(chat_id, [])

async def add_autoplay_history(chat_id: int, vidid: str):
    hist = autoplay_history.setdefault(chat_id, [])
    hist.append(vidid)
    # keep only the most recent 20 ids so the "related" pool doesn't dry up
    if len(hist) > 20:
        del hist[: len(hist) - 20]

# -------------------------------

async def get_cmode(chat_id: int) -> int:
    mode = channelconnect.get(chat_id)
    if not mode:
        mode = await channeldb.find_one({"chat_id": chat_id})
        if not mode:
            return None
        channelconnect[chat_id] = mode["mode"]
        return mode["mode"]
    return mode

async def set_cmode(chat_id: int, mode: int):
    channelconnect[chat_id] = mode
    await channeldb.update_one(
        {"chat_id": chat_id}, {"$set": {"mode": mode}}, upsert=True
    )

async def get_playtype(chat_id: int) -> str:
    mode = playtype.get(chat_id)
    if not mode:
        mode = await playtypedb.find_one({"chat_id": chat_id})
        if not mode:
            playtype[chat_id] = "Everyone"
            return "Everyone"
        playtype[chat_id] = mode["mode"]
        return mode["mode"]
    return mode

async def set_playtype(chat_id: int, mode: str):
    playtype[chat_id] = mode
    await playtypedb.update_one(
        {"chat_id": chat_id}, {"$set": {"mode": mode}}, upsert=True
    )

async def get_playmode(chat_id: int) -> str:
    mode = playmode.get(chat_id)
    if not mode:
        mode = await playmodedb.find_one({"chat_id": chat_id})
        if not mode:
            playmode[chat_id] = "Direct"
            return "Direct"
        playmode[chat_id] = mode["mode"]
        return mode["mode"]
    return mode

async def set_playmode(chat_id: int, mode: str):
    playmode[chat_id] = mode
    await playmodedb.update_one(
        {"chat_id": chat_id}, {"$set": {"mode": mode}}, upsert=True
    )

async def get_lang(chat_id: int) -> str:
    mode = langm.get(chat_id)
    if not mode:
        lang = await langdb.find_one({"chat_id": chat_id})
        if not lang:
            langm[chat_id] = "en"
            return "en"
        langm[chat_id] = lang["lang"]
        return lang["lang"]
    return mode

async def set_lang(chat_id: int, lang: str):
    langm[chat_id] = lang
    await langdb.update_one({"chat_id": chat_id}, {"$set": {"lang": lang}}, upsert=True)

async def is_music_playing(chat_id: int) -> bool:
    mode = pause.get(chat_id)
    if not mode:
        return False
    return mode

async def music_on(chat_id: int):
    pause[chat_id] = True

async def music_off(chat_id: int):
    pause[chat_id] = False

async def get_active_chats() -> list:
    return active

async def is_active_chat(chat_id: int) -> bool:
    return chat_id in active

async def add_active_chat(chat_id: int):
    if chat_id not in active:
        active.append(chat_id)

async def remove_active_chat(chat_id: int):
    if chat_id in active:
        active.remove(chat_id)

async def get_active_video_chats() -> list:
    return activevideo

async def is_active_video_chat(chat_id: int) -> bool:
    return chat_id in activevideo

async def add_active_video_chat(chat_id: int):
    if chat_id not in activevideo:
        activevideo.append(chat_id)

async def remove_active_video_chat(chat_id: int):
    if chat_id in activevideo:
        activevideo.remove(chat_id)

async def check_nonadmin_chat(chat_id: int) -> bool:
    user = await authdb.find_one({"chat_id": chat_id})
    return bool(user)

async def is_nonadmin_chat(chat_id: int) -> bool:
    mode = nonadmin.get(chat_id)
    if not mode:
        user = await authdb.find_one({"chat_id": chat_id})
        if not user:
            nonadmin[chat_id] = False
            return False
        nonadmin[chat_id] = True
        return True
    return mode

async def add_nonadmin_chat(chat_id: int):
    nonadmin[chat_id] = True
    if await check_nonadmin_chat(chat_id):
        return
    return await authdb.insert_one({"chat_id": chat_id})

async def remove_nonadmin_chat(chat_id: int):
    nonadmin[chat_id] = False
    if not await check_nonadmin_chat(chat_id):
        return
    return await authdb.delete_one({"chat_id": chat_id})

async def is_on_off(on_off: int) -> bool:
    onoff = await onoffdb.find_one({"on_off": on_off})
    return bool(onoff)

async def add_on(on_off: int):
    if await is_on_off(on_off):
        return
    return await onoffdb.insert_one({"on_off": on_off})

async def add_off(on_off: int):
    if not await is_on_off(on_off):
        return
    return await onoffdb.delete_one({"on_off": on_off})

async def is_maintenance():
    if not maintenance:
        get = await onoffdb.find_one({"on_off": 1})
        if not get:
            maintenance.clear()
            maintenance.append(2)
            return True
        else:
            maintenance.clear()
            maintenance.append(1)
            return False
    return 1 not in maintenance

async def maintenance_off():
    maintenance.clear()
    maintenance.append(2)
    if await is_on_off(1):
        return await onoffdb.delete_one({"on_off": 1})

async def maintenance_on():
    maintenance.clear()
    maintenance.append(1)
    if not await is_on_off(1):
        return await onoffdb.insert_one({"on_off": 1})

async def is_served_user(user_id: int) -> bool:
    user = await usersdb.find_one({"user_id": user_id})
    return bool(user)

async def get_served_users() -> list:
    users_list = []
    async for user in usersdb.find({"user_id": {"$gt": 0}}):
        users_list.append(user)
    return users_list

async def add_served_user(user_id: int):
    if not await is_served_user(user_id):
        await usersdb.insert_one({"user_id": user_id})

async def get_served_chats() -> list:
    chats_list = []
    async for chat in chatsdb.find({"chat_id": {"$lt": 0}}):
        chats_list.append(chat)
    return chats_list

async def is_served_chat(chat_id: int) -> bool:
    chat = await chatsdb.find_one({"chat_id": chat_id})
    return bool(chat)

async def add_served_chat(chat_id: int):
    if not await is_served_chat(chat_id):
        await chatsdb.insert_one({"chat_id": chat_id})

async def blacklisted_chats() -> list:
    chats_list = []
    async for chat in blacklist_chatdb.find({"chat_id": {"$lt": 0}}):
        chats_list.append(chat["chat_id"])
    return chats_list

async def blacklist_chat(chat_id: int) -> bool:
    if not await blacklist_chatdb.find_one({"chat_id": chat_id}):
        await blacklist_chatdb.insert_one({"chat_id": chat_id})
        return True
    return False

async def whitelist_chat(chat_id: int) -> bool:
    if await blacklist_chatdb.find_one({"chat_id": chat_id}):
        await blacklist_chatdb.delete_one({"chat_id": chat_id})
        return True
    return False

async def _get_authusers(chat_id: int) -> Dict[str, int]:
    _notes = await authuserdb.find_one({"chat_id": chat_id})
    return _notes["notes"] if _notes else {}

async def get_authuser_names(chat_id: int) -> List[str]:
    return [note for note in await _get_authusers(chat_id)]

async def get_authuser(chat_id: int, name: str) -> Union[bool, dict]:
    _notes = await _get_authusers(chat_id)
    return _notes.get(name, False)

async def save_authuser(chat_id: int, name: str, note: dict):
    _notes = await _get_authusers(chat_id)
    _notes[name] = note
    await authuserdb.update_one(
        {"chat_id": chat_id}, {"$set": {"notes": _notes}}, upsert=True
    )

async def delete_authuser(chat_id: int, name: str) -> bool:
    notesd = await _get_authusers(chat_id)
    if name in notesd:
        del notesd[name]
        await authuserdb.update_one(
            {"chat_id": chat_id}, {"$set": {"notes": notesd}}, upsert=True,
        )
        return True
    return False

async def get_gbanned() -> list:
    return [user["user_id"] async for user in gbansdb.find({"user_id": {"$gt": 0}})]

async def is_gbanned_user(user_id: int) -> bool:
    user = await gbansdb.find_one({"user_id": user_id})
    return bool(user)

async def add_gban_user(user_id: int):
    if not await is_gbanned_user(user_id):
        await gbansdb.insert_one({"user_id": user_id})

async def remove_gban_user(user_id: int):
    if await is_gbanned_user(user_id):
        await gbansdb.delete_one({"user_id": user_id})

async def get_sudoers() -> list:
    sudoers = await sudoersdb.find_one({"sudo": "sudo"})
    return sudoers["sudoers"] if sudoers else []

async def add_sudo(user_id: int) -> bool:
    sudoers = await get_sudoers()
    if user_id not in sudoers:
        sudoers.append(user_id)
        await sudoersdb.update_one(
            {"sudo": "sudo"}, {"$set": {"sudoers": sudoers}}, upsert=True
        )
    return True

async def remove_sudo(user_id: int) -> bool:
    sudoers = await get_sudoers()
    if user_id in sudoers:
        sudoers.remove(user_id)
        await sudoersdb.update_one(
            {"sudo": "sudo"}, {"$set": {"sudoers": sudoers}}, upsert=True
        )
    return True

async def get_banned_users() -> list:
    return [user["user_id"] async for user in blockeddb.find({"user_id": {"$gt": 0}})]

async def is_banned_user(user_id: int) -> bool:
    user = await blockeddb.find_one({"user_id": user_id})
    return bool(user)

async def add_banned_user(user_id: int):
    if not await is_banned_user(user_id):
        await blockeddb.insert_one({"user_id": user_id})

async def remove_banned_user(user_id: int):
    if await is_banned_user(user_id):
        await blockeddb.delete_one({"user_id": user_id})

async def is_ignored_user(user_id: int) -> bool:
    user = await ignoredb.find_one({"user_id": user_id})
    return bool(user)

async def add_ignored_user(user_id: int):
    if not await is_ignored_user(user_id):
        await ignoredb.insert_one({"user_id": user_id})

async def remove_ignored_user(user_id: int):
    if await is_ignored_user(user_id):
        await ignoredb.delete_one({"user_id": user_id})

# --- CLEANMODE FUNCTIONS ---

async def is_cleanmode_on(chat_id: int) -> bool:
    chat = await cleandb.find_one({"chat_id": chat_id})
    if not chat:
        return True
    return chat.get("status", True)

async def set_queries(count: int):
    await queriesdb.update_one(
        {"stats": "queries"},
        {"$inc": {"total": count}},
        upsert=True
    )
