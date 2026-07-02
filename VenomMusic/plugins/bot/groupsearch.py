from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ButtonStyle # Style ke liye zaroori import
import aiohttp
import re
import os
from VenomMusic import app


@app.on_message(filters.command("tg"))
async def search_command(_, message):
    if len(message.command) < 2:
        return await message.reply("Please provide a search query!")
        
    msg = await message.reply("Searching...")
    async with aiohttp.ClientSession() as session:
        start = 1
        async with session.get(
            f"https://content-customsearch.googleapis.com/customsearch/v1?cx=ec8db9e1f9e41e65e&q={message.text.split()[1]}&key=AIzaSyAa8yy0GdcGPHdtD083HiGGx_S0vMPScDM&start={start}",
            headers={"x-referer": "https://explorer.apis.google.com"},
        ) as r:
            response = await r.json()
            result = ""

            if not response.get("items"):
                return await msg.edit("No results found!")

            for item in response["items"]:
                title = item["title"]
                link = item["link"]
                if "/s" in item["link"]:
                    link = item["link"].replace("/s", "")
                elif re.search(r"\/\d", item["link"]):
                    link = re.sub(r"\/\d", "", item["link"])
                if "?" in link:
                    link = link.split("?")[0]
                if link in result:
                    continue
                result += f"{title}\n{link}\n\n"

            # Next button ko Green (Success) style diya hai
            prev_and_next_btns = [
                [InlineKeyboardButton("▶️Next▶️", callback_data=f"next {start+10} {message.text.split()[1]}", style=ButtonStyle.SUCCESS)]
            ]
            await msg.edit(result, reply_markup=InlineKeyboardMarkup(prev_and_next_btns), disable_web_page_preview=True)
            await session.close()


@app.on_callback_query(filters.regex(r"prev (.*) (.*)"))
async def prev_callback(_, callback_query):
    start = int(callback_query.data.split()[1])
    query = callback_query.data.split()[2]
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://content-customsearch.googleapis.com/customsearch/v1?cx=ec8db9e1f9e41e65e&q={query}&key=AIzaSyAa8yy0GdcGPHdtD083HiGGx_S0vMPScDM&start={start}",
            headers={"x-referer": "https://explorer.apis.google.com"},
        ) as r:
            response = await r.json()
            if response.get("error"):
                return await callback_query.answer("No more results!")

            result = ""
            for item in response["items"]:
                title = item["title"]
                link = item["link"]
                if "/s" in item["link"]:
                    link = item["link"].replace("/s", "")
                elif re.search(r"\/\d", item["link"]):
                    link = re.sub(r"\/\d", "", item["link"])
                if "?" in link:
                    link = link.split("?")[0]
                if link in result:
                    continue
                result += f"{title}\n{link}\n\n"

            # Prev ko Red (Danger) aur Next ko Green (Success)
            prev_and_next_btns = [
                [
                    InlineKeyboardButton("◀️Prev◀️", callback_data=f"prev {start-10} {query}", style=ButtonStyle.DANGER),
                    InlineKeyboardButton("▶️Next▶️", callback_data=f"next {start+10} {query}", style=ButtonStyle.SUCCESS)
                ]
            ]
            await callback_query.edit_message_text(result, reply_markup=InlineKeyboardMarkup(prev_and_next_btns), disable_web_page_preview=True)
            await session.close()


@app.on_callback_query(filters.regex(r"next (.*) (.*)"))
async def next_callback(_, callback_query):
    start = int(callback_query.data.split()[1])
    query = callback_query.data.split()[2]
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://content-customsearch.googleapis.com/customsearch/v1?cx=ec8db9e1f9e41e65e&q={query}&key=AIzaSyAa8yy0GdcGPHdtD083HiGGx_S0vMPScDM&start={start}",
            headers={"x-referer": "https://explorer.apis.google.com"},
        ) as r:
            response = await r.json()
            if response.get("searchInformation") and response["searchInformation"]["totalResults"] == "0":
                return await callback_query.answer("No more results!")

            result = ""
            if "items" in response:
                for item in response["items"]:
                    title = item["title"]
                    link = item["link"]
                    if "/s" in item["link"]:
                        link = item["link"].replace("/s", "")
                    elif re.search(r"\/\d", item["link"]):
                        link = re.sub(r"\/\d", "", item["link"])
                    if "?" in link:
                        link = link.split("?")[0]
                    if link in result:
                        continue
                    result += f"{title}\n{link}\n\n"

            prev_and_next_btns = [
                [
                    InlineKeyboardButton("◀️Prev◀️", callback_data=f"prev {start-10} {query}", style=ButtonStyle.DANGER),
                    InlineKeyboardButton("▶️Next▶️", callback_data=f"next {start+10} {query}", style=ButtonStyle.SUCCESS)
                ]
            ]
            await callback_query.edit_message_text(result, reply_markup=InlineKeyboardMarkup(prev_and_next_btns), disable_web_page_preview=True)
            await session.close()
