import os
import re
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps
from unidecode import unidecode
from youtubesearchpython.__future__ import VideosSearch
from VenomMusic import app
from config import YOUTUBE_IMG_URL


def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage


def clear(text):
    list = text.split(" ")
    title = ""
    for i in list:
        if len(title) + len(i) < 60:
            title += " " + i
    return title.strip()


async def get_qthumb(videoid):
    try:
        url = f"https://img.youtube.com/vi/{videoid}/maxresdefault.jpg"
        return url
    except Exception:
        return YOUTUBE_IMG_URL


async def get_thumb(videoid):
    try:
        url = f"https://img.youtube.com/vi/{videoid}/maxresdefault.jpg"
        return url
    except Exception:
        return YOUTUBE_IMG_URL
