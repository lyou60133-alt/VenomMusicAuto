import asyncio
import os
import random
import config
from datetime import datetime, timedelta
from typing import Union

from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup
from pytgcalls import PyTgCalls, StreamType
from pytgcalls.exceptions import (
    AlreadyJoinedError,
    NoActiveGroupCall,
    TelegramServerError,
)
from pytgcalls.types import Update
from pytgcalls.types.input_stream import AudioPiped, AudioVideoPiped
from pytgcalls.types.input_stream.quality import HighQualityAudio, MediumQualityVideo
from pytgcalls.types.stream import StreamAudioEnded

from VenomMusic import LOGGER, YouTube, app
from VenomMusic.misc import db
from VenomMusic.utils.database import (
    add_active_chat,
    add_active_video_chat,
    add_autoplay_history,
    get_autoplay_history,
    get_lang,
    get_loop,
    group_assistant,
    is_autoend,
    is_autoplay,
    music_on,
    remove_active_chat,
    remove_active_video_chat,
    set_loop,
)
from VenomMusic.utils.exceptions import AssistantErr
from VenomMusic.utils.formatters import check_duration, seconds_to_min, speed_converter
from VenomMusic.utils.inline.play import stream_markup
from VenomMusic.utils.stream.autoclear import auto_clean
from VenomMusic.utils.stream.queue import put_queue
from VenomMusic.utils.thumbnails import get_thumb
from strings import get_string

# Note: If delete_old_message is needed, find its correct path. 
# Usually, it's in utils.functions or utils.inline
try:
    from VenomMusic.utils.functions import delete_old_message
except ImportError:
    async def delete_old_message(*args, **kwargs):
        pass

autoend = {}
counter = {}
preload_lock = {}


async def _clear_(chat_id):
    if chat_id in db:
        db[chat_id] = []
    await remove_active_video_chat(chat_id)
    await remove_active_chat(chat_id)


class Call(PyTgCalls):
    def __init__(self):
        self.userbot1 = Client(
            name="VenomAss1",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING1),
        )
        self.one = PyTgCalls(self.userbot1, cache_duration=100)
        
        self.userbot2 = Client(
            name="VenomAss2",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING2),
        )
        self.two = PyTgCalls(self.userbot2, cache_duration=100)
        
        self.userbot3 = Client(
            name="VenomAss3",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING3),
        )
        self.three = PyTgCalls(self.userbot3, cache_duration=100)
        
        self.userbot4 = Client(
            name="VenomAss4",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING4),
        )
        self.four = PyTgCalls(self.userbot4, cache_duration=100)
        
        self.userbot5 = Client(
            name="VenomAss5",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING5),
        )
        self.five = PyTgCalls(self.userbot5, cache_duration=100)

    async def pause_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.pause_stream(chat_id)

    async def resume_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.resume_stream(chat_id)

    async def stop_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        try:
            await _clear_(chat_id)
            await assistant.leave_group_call(chat_id)
        except:
            pass

    async def stop_stream_force(self, chat_id: int):
        try:
            if config.STRING1: await self.one.leave_group_call(chat_id)
            if config.STRING2: await self.two.leave_group_call(chat_id)
            if config.STRING3: await self.three.leave_group_call(chat_id)
            if config.STRING4: await self.four.leave_group_call(chat_id)
            if config.STRING5: await self.five.leave_group_call(chat_id)
            await _clear_(chat_id)
        except:
            pass

    async def speedup_stream(self, chat_id: int, file_path, speed, playing):
        assistant = await group_assistant(self, chat_id)
        if str(speed) != "1.0":
            base = os.path.basename(file_path)
            chatdir = os.path.join(os.getcwd(), "playback", str(speed))
            if not os.path.isdir(chatdir):
                os.makedirs(chatdir)
            out = os.path.join(chatdir, base)
            if not os.path.isfile(out):
                vs = {"0.5": 2.0, "0.75": 1.35, "1.5": 0.68, "2.0": 0.5}.get(str(speed), 1.0)
                proc = await asyncio.create_subprocess_shell(
                    cmd=f"ffmpeg -i {file_path} -filter:v setpts={vs}*PTS -filter:a atempo={speed} {out}",
                    stdin=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                await proc.communicate()
        else:
            out = file_path

        dur = await asyncio.get_event_loop().run_in_executor(None, check_duration, out)
        dur = int(dur)
        played, con_seconds = speed_converter(playing[0]["played"], speed)
        duration = seconds_to_min(dur)
        
        stream = (
            AudioVideoPiped(out, audio_parameters=HighQualityAudio(), video_parameters=MediumQualityVideo(), additional_ffmpeg_parameters=f"-ss {played} -to {duration}")
            if playing[0]["streamtype"] == "video"
            else AudioPiped(out, audio_parameters=HighQualityAudio(), additional_ffmpeg_parameters=f"-ss {played} -to {duration}")
        )
        
        if str(db[chat_id][0]["file"]) == str(file_path):
            await assistant.change_stream(chat_id, stream)
            db[chat_id][0].setdefault("old_dur", db[chat_id][0]["dur"])
            db[chat_id][0].setdefault("old_second", db[chat_id][0]["seconds"])
            db[chat_id][0].update({"played": con_seconds, "dur": duration, "seconds": dur, "speed_path": out, "speed": speed})
        else:
            raise AssistantErr("Umm")

    async def force_stop_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        try:
            check = db.get(chat_id)
            if check: check.pop(0)
        except:
            pass
        await remove_active_video_chat(chat_id)
        await music_on(chat_id) 
        await remove_active_chat(chat_id)
        try:
            await assistant.leave_group_call(chat_id)
        except:
            pass

    async def skip_stream(self, chat_id: int, link: str, video: Union[bool, str] = None, image: Union[bool, str] = None):
        assistant = await group_assistant(self, chat_id)
        stream = AudioVideoPiped(link, audio_parameters=HighQualityAudio(), video_parameters=MediumQualityVideo()) if video else AudioPiped(link, audio_parameters=HighQualityAudio())
        await assistant.change_stream(chat_id, stream)

    async def seek_stream(self, chat_id, file_path, to_seek, duration, mode):
        assistant = await group_assistant(self, chat_id)
        stream = (
            AudioVideoPiped(file_path, audio_parameters=HighQualityAudio(), video_parameters=MediumQualityVideo(), additional_ffmpeg_parameters=f"-ss {to_seek} -to {duration}")
            if mode == "video"
            else AudioPiped(file_path, audio_parameters=HighQualityAudio(), additional_ffmpeg_parameters=f"-ss {to_seek} -to {duration}")
        )
        await assistant.change_stream(chat_id, stream)

    async def stream_call(self, link):
        assistant = await group_assistant(self, config.LOGGER_ID)
        await assistant.join_group_call(config.LOGGER_ID, AudioVideoPiped(link), stream_type=StreamType().pulse_stream)
        await asyncio.sleep(0.2)
        await assistant.leave_group_call(config.LOGGER_ID)

    async def join_call(self, chat_id: int, original_chat_id: int, link, video: Union[bool, str] = None, image: Union[bool, str] = None):
        assistant = await group_assistant(self, chat_id)
        language = await get_lang(chat_id)
        _ = get_string(language)
        stream = AudioVideoPiped(link, audio_parameters=HighQualityAudio(), video_parameters=MediumQualityVideo()) if video else AudioPiped(link, audio_parameters=HighQualityAudio())
        
        try:
            await assistant.join_group_call(chat_id, stream, stream_type=StreamType().pulse_stream)
        except NoActiveGroupCall:
            raise AssistantErr(_["call_8"])
        except AlreadyJoinedError:
            raise AssistantErr(_["call_9"])
        except TelegramServerError:
            raise AssistantErr(_["call_10"])
            
        await add_active_chat(chat_id)
        await music_on(chat_id)
        if video: await add_active_video_chat(chat_id)
        if await is_autoend():
            counter[chat_id] = {}
            users = len(await assistant.get_participants(chat_id))
            if users == 1:
                autoend[chat_id] = datetime.now() + timedelta(minutes=1)

    async def _preload_autoplay(self, chat_id: int, current: dict):
        """
        Fires the moment a track starts playing (if it's the last one queued and
        autoplay is on). Fetches AND downloads the next same-channel track in the
        background, ahead of time, so when this track ends the next one is
        already on disk and change_stream can play it instantly with no lookup
        or download delay.
        """
        current_vidid = current.get("vidid")
        if not current_vidid or current_vidid in ("telegram", "soundcloud"):
            return
        if preload_lock.get(chat_id) == current_vidid:
            return
        preload_lock[chat_id] = current_vidid
        try:
            check = db.get(chat_id)
            if not check or len(check) != 1 or check[0].get("vidid") != current_vidid:
                return  # something else already queued / state moved on

            history = await get_autoplay_history(chat_id)
            related_ids = await YouTube.related(current_vidid)
            eligible = [rid for rid in related_ids if rid not in history] or related_ids
            if not eligible:
                return
            next_id = random.choice(eligible)

            title, duration_min, duration_sec, thumbnail, _vidid = await YouTube.details(
                next_id, True
            )
            streamtype = current.get("streamtype", "audio")
            file_path, direct = await YouTube.download(
                next_id, None, video=(streamtype == "video"), videoid=True
            )
            if not file_path:
                return

            # Re-check nothing changed while the download was in flight
            check = db.get(chat_id)
            if not check or len(check) != 1 or check[0].get("vidid") != current_vidid:
                return

            await put_queue(
                chat_id,
                current.get("chat_id", chat_id),
                file_path if direct else f"vid_{next_id}",
                title,
                duration_min,
                "Autoplay",
                next_id,
                0,
                streamtype,
            )
            await add_autoplay_history(chat_id, next_id)
        except Exception as e:
            LOGGER(__name__).warning(f"Autoplay preload failed for {chat_id}: {e}")
        finally:
            preload_lock.pop(chat_id, None)

    async def _autoplay_next(self, chat_id: int, popped: dict) -> bool:
        """
        Called when the queue runs out. Looks up a related song for the last
        played track and pushes it onto the queue so change_stream can play it.
        Returns True if a track was successfully queued.
        """
        if not popped:
            return False
        vidid = popped.get("vidid")
        if not vidid or vidid in ("telegram", "soundcloud"):
            return False
        try:
            history = await get_autoplay_history(chat_id)
            related_ids = await YouTube.related(vidid)
            eligible = [rid for rid in related_ids if rid not in history]
            if not eligible:
                # every track from this channel has been played recently, recycle
                eligible = related_ids
            if not eligible:
                return False
            next_id = random.choice(eligible)
            title, duration_min, duration_sec, thumbnail, _vidid = await YouTube.details(
                next_id, True
            )
        except Exception as e:
            LOGGER(__name__).warning(f"Autoplay lookup failed for {chat_id}: {e}")
            return False

        original_chat_id = popped.get("chat_id", chat_id)
        streamtype = popped.get("streamtype", "audio")
        await put_queue(
            chat_id,
            original_chat_id,
            f"vid_{next_id}",
            title,
            duration_min,
            "Autoplay",
            next_id,
            0,
            streamtype,
        )
        await add_autoplay_history(chat_id, next_id)
        return True

    async def change_stream(self, client: PyTgCalls, chat_id: int):
        await delete_old_message(chat_id)
        check = db.get(chat_id)
        popped = None
        loop = await get_loop(chat_id)
        
        try:
            if not check:
                await _clear_(chat_id)
                try: await client.leave_group_call(chat_id)
                except: pass
                return

            if loop == 0:
                popped = check.pop(0)
            else:
                await set_loop(chat_id, loop - 1)
            
            if popped: await auto_clean(popped)

            if not check and popped and await is_autoplay(chat_id):
                queued_next = await self._autoplay_next(chat_id, popped)
                if queued_next:
                    check = db.get(chat_id)

            if not check:
                await _clear_(chat_id)
                try:
                    end_msg = await app.send_message(chat_id, "𝐓ʜє 𝐌υsɪᴄ 𝐐υєυє 𝐇ᴧ𝐬 𝐄ηᴅєᴅ.\n➤ 𝐔𝐬𝐞 /play 𝐓𝐨 𝐀𝐝𝐝 𝐌𝐨𝐫𝐞 𝐒𝐨𝐧𝐠𝐬 ")
                    await client.leave_group_call(chat_id)
                    await asyncio.sleep(60)
                    await end_msg.delete()
                except: pass
                return
        except Exception as e:
            LOGGER(__name__).error(f"Error in change_stream: {e}")
            await _clear_(chat_id)
            return

        # Play logic for next track
        queued = check[0]["file"]
        language = await get_lang(chat_id)
        _ = get_string(language)
        title = (check[0]["title"]).title()
        user = check[0]["by"]
        original_chat_id = check[0]["chat_id"]
        streamtype = check[0]["streamtype"]
        videoid = check[0]["vidid"]
        db[chat_id][0]["played"] = 0
        
        if (exis := check[0].get("old_dur")):
            db[chat_id][0].update({"dur": exis, "seconds": check[0]["old_second"], "speed_path": None, "speed": 1.0})
            
        video = bool(str(streamtype) == "video")
        
        # Determine Stream Input
        if "live_" in queued:
            n, link = await YouTube.video(videoid, True)
            if n == 0: return await app.send_message(original_chat_id, text=_["call_6"])
            stream = AudioVideoPiped(link, audio_parameters=HighQualityAudio(), video_parameters=MediumQualityVideo()) if video else AudioPiped(link, audio_parameters=HighQualityAudio())
        elif "vid_" in queued:
            mystic = await app.send_message(original_chat_id, _["call_7"])
            try:
                file_path, _ = await YouTube.download(videoid, mystic, videoid=True, video=video)
            except:
                return await mystic.edit_text(_["call_6"])
            stream = AudioVideoPiped(file_path, audio_parameters=HighQualityAudio(), video_parameters=MediumQualityVideo()) if video else AudioPiped(file_path, audio_parameters=HighQualityAudio())
            await mystic.delete()
        else:
            stream = AudioVideoPiped(queued, audio_parameters=HighQualityAudio(), video_parameters=MediumQualityVideo()) if video else AudioPiped(queued, audio_parameters=HighQualityAudio())

        try:
            await client.change_stream(chat_id, stream)
        except:
            return await app.send_message(original_chat_id, text=_["call_6"])

        if await is_autoplay(chat_id):
            asyncio.create_task(self._preload_autoplay(chat_id, dict(check[0])))

        # Update UI
        img = await get_thumb(videoid) if videoid not in ["telegram", "soundcloud"] else (config.TELEGRAM_AUDIO_URL if "telegram" in videoid else config.SOUNCLOUD_IMG_URL)
        button = stream_markup(_, chat_id)
        run = await app.send_photo(
            chat_id=original_chat_id,
            photo=img,
            caption=_["stream_1"].format(f"https://t.me/{app.username}?start=info_{videoid}", title[:23], check[0]["dur"], user),
            reply_markup=InlineKeyboardMarkup(button),
        )
        db[chat_id][0]["mystic"] = run
        db[chat_id][0]["markup"] = "tg"

    async def ping(self):
        pings = []
        for bot in [self.one, self.two, self.three, self.four, self.five]:
            try: pings.append(await bot.ping)
            except: pass
        return str(round(sum(pings) / len(pings), 3)) if pings else "0.0"

    async def start(self):
        LOGGER(__name__).info("Starting PyTgCalls Clients...\n")
        if config.STRING1: await self.one.start()
        if config.STRING2: await self.two.start()
        if config.STRING3: await self.three.start()
        if config.STRING4: await self.four.start()
        if config.STRING5: await self.five.start()

    async def decorators(self):
        @self.one.on_kicked()
        @self.two.on_kicked()
        @self.three.on_kicked()
        @self.four.on_kicked()
        @self.five.on_kicked()
        @self.one.on_closed_voice_chat()
        @self.two.on_closed_voice_chat()
        @self.three.on_closed_voice_chat()
        @self.four.on_closed_voice_chat()
        @self.five.on_closed_voice_chat()
        @self.one.on_left()
        @self.two.on_left()
        @self.three.on_left()
        @self.four.on_left()
        @self.five.on_left()
        async def stream_services_handler(_, chat_id: int):
            await self.stop_stream(chat_id)

        @self.one.on_stream_end()
        @self.two.on_stream_end()
        @self.three.on_stream_end()
        @self.four.on_stream_end()
        @self.five.on_stream_end()
        async def stream_end_handler1(client, update: Update):
            chat_id = getattr(update, "chat_id", None)
            if chat_id and isinstance(update, StreamAudioEnded):
                await self.change_stream(client, chat_id)


Venom = Call()
