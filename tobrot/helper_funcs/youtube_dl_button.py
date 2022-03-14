import logging
import os
import re
import json
import math
import time
import shutil
import random
import ffmpeg
import asyncio
import subprocess
import requests
from tobrot import AUTH_CHANNEL, DOWNLOAD_LOCATION, CHUNK_SIZE, TG_MAX_FILE_SIZE, DEF_THUMB_NAIL_VID_S, LOGGER, ZEE_COMMAND
from script import script
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from datetime import datetime
from PIL import Image

from tobrot.plugins.helpers import(
    progress_for_pyrogram,
    humanbytes,
    headers,
    take_screen_shot,
    DownLoadFile
)

async def youtube_dl_call_back(bot, update):
  
    try:
        cb_data = update.data
        tg_send_type, youtube_dl_format, youtube_dl_ext = cb_data.split("|")
        current_user_id = update.message.reply_to_message.from_user.id
        current_touched_user_id = update.from_user.id
        if current_user_id != current_touched_user_id:
            await bot.answer_callback_query(
                callback_query_id=update.id,
                text="Dont Touch On This. This Leech isnt started by you..馃槨馃槨馃槨",
                show_alert=True,
                cache_time=0,
        )
            return False, None
        
        thumb_image_path = DOWNLOAD_LOCATION + \
            "/" + str(update.from_user.id) + ".jpg"

        save_ytdl_json_path = DOWNLOAD_LOCATION + \
            "/" + str(update.from_user.id) + ".json"
        try:
            with open(save_ytdl_json_path, "r", encoding="utf8") as f:
                response_json = json.load(f)
        except (FileNotFoundError) as e:
            await bot.delete_messages(
                chat_id=update.message.chat.id,
                message_ids=update.message.message_id,
                revoke=True
            )
            return False
        
        youtube_dl_url = zee5_capture.url
        
        linksplit = update.message.reply_to_message.text.split("/")
        videoname = linksplit[+5]
        logger.info(videoname)
        
        custom_file_name = videoname + ".mp4"

        await bot.edit_message_text(
            text=script.DOWNLOAD_START,
            chat_id=update.message.chat.id,
            message_id=update.message.message_id
        )
        description = script.CUSTOM_CAPTION_UL_FILE.format(newname=custom_file_name)

        tmp_directory_for_each_user = DOWNLOAD_LOCATION + "/" + str(update.from_user.id)
        if not os.path.isdir(tmp_directory_for_each_user):
            os.makedirs(tmp_directory_for_each_user)
        download_directory = tmp_directory_for_each_user + "/" + custom_file_name
        command_to_exec = []
        
        minus_f_format = youtube_dl_format + "+bestaudio"
        command_to_exec = [
            "youtube-dl",
            "-c",
            "-f", minus_f_format,
            "--hls-prefer-ffmpeg", youtube_dl_url,
            "-o", download_directory
        ]                  
        command_to_exec.append("--no-warnings")
        command_to_exec.append("--geo-bypass-country")
        command_to_exec.append("IN")
        
        start = datetime.now()
        process = await asyncio.create_subprocess_exec(
            *command_to_exec,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        e_response = stderr.decode().strip()
        t_response = stdout.decode().strip()

        if os.path.isfile(download_directory):
            logger.info("no issues")
        else:
            logger.info("issues found, passing to sub process")
            command_to_exec.clear()
            minus_f_format = youtube_dl_format
            command_to_exec = [
                "youtube-dl",
                "-c",
                "--max-filesize", str(TG_MAX_FILE_SIZE),
                "-f", minus_f_format,
                "--hls-prefer-ffmpeg", youtube_dl_url,
                "-o", download_directory
            ]                  
            command_to_exec.append("--no-warnings")
            command_to_exec.append("--geo-bypass-country")
            command_to_exec.append("IN")
        
            start = datetime.now()
            process = await asyncio.create_subprocess_exec(
                *command_to_exec,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()
            e_response = stderr.decode().strip()
            t_response = stdout.decode().strip()

        ad_string_to_replace = "please report this issue on https://yt-dl.org/bug . Make sure you are using the latest version; see  https://yt-dl.org/update  on how to update. Be sure to call youtube-dl with the --verbose flag and include its complete output."
        if e_response and ad_string_to_replace in e_response:
            error_message = e_response.replace(ad_string_to_replace, "")
            await bot.edit_message_text(
                chat_id=update.message.chat.id,
                message_id=update.message.message_id,
                text=error_message
            )
            return False
        if t_response:
            os.remove(save_ytdl_json_path)
            end_one = datetime.now()
            time_taken_for_download = (end_one -start).seconds
            file_size = TG_MAX_FILE_SIZE + 1
            try:
                file_size = os.stat(download_directory).st_size
            except FileNotFoundError as exc:
                download_directory = os.path.splitext(download_directory)[0] + "." + "mp4"
                file_size = os.stat(download_directory).st_size
            if file_size > TG_MAX_FILE_SIZE:
                await bot.edit_message_text(
                    chat_id=update.message.chat.id,
                    text=script.RCHD_TG_API_LIMIT.format(time_taken_for_download, humanbytes(file_size)),
                    message_id=update.message.message_id
                )
            else:
                await bot.edit_message_text(
                    text=script.UPLOAD_START,
                    chat_id=update.message.chat.id,
                    message_id=update.message.message_id
                )

                # get the correct width, height, and duration for videos greater than 10MB
                width = 0
                height = 0
                duration = 0
                if tg_send_type != "file":
                    metadata = extractMetadata(createParser(download_directory))
                    if metadata is not None:
                        if metadata.has("duration"):
                            duration = metadata.get('duration').seconds            
                # get the correct width, height, and duration for videos greater than 10MB
                
                if not os.path.exists(thumb_image_path):
                    mes = await thumb(update.from_user.id)
                    if mes != None:
                        m = await bot.get_messages(update.chat.id, mes.msg_id)
                        await m.download(file_name=thumb_image_path)
                        thumb_image_path = thumb_image_path
                    else:
                        try:
                            thumb_image_path = await take_screen_shot(
                                download_directory,
                                os.path.dirname(download_directory),
                                random.randint(
                                    0,
                                    duration - 1
                                )
                            )
                        except:
                            thumb_image_path = None
                            pass  
                else:
                    width = 0
                    height = 0
                    metadata = extractMetadata(createParser(thumb_image_path))
                    if metadata.has("width"):
                        width = metadata.get("width")
                    if metadata.has("height"):
                        height = metadata.get("height")
                    if tg_send_type == "vm":
                        height = width               
                    Image.open(thumb_image_path).convert(
                        "RGB").save(thumb_image_path)
                    img = Image.open(thumb_image_path)
                    img.thumbnail((90, 90))
                    if tg_send_type == "file":
                        img.resize((320, height))
                    else:
                        img.resize((90, height))
                    img.save(thumb_image_path, "JPEG")
  
                start_time = time.time()

                if tg_send_type == "file":
                    await bot.send_document(
                        chat_id=update.message.chat.id,
                        document=download_directory,
                        thumb=thumb_image_path,
                        caption=description,
                        parse_mode="HTML",
                        # reply_markup=reply_markup,
                        reply_to_message_id=update.message.reply_to_message.message_id,
                        progress=progress_for_pyrogram,
                        progress_args=(
                            script.UPLOAD_START,
                            update.message,
                            start_time
                        )
                    )
                elif tg_send_type == "video":
                    await bot.send_video(
                        chat_id=update.message.chat.id,
                        video=download_directory,
                        caption=description,
                        parse_mode="HTML",
                        duration=duration,
                        width=width,
                        height=height,
                        supports_streaming=True,
                        # reply_markup=reply_markup,
                        thumb=thumb_image_path,
                        reply_to_message_id=update.message.reply_to_message.message_id,
                        progress=progress_for_pyrogram,
                        progress_args=(
                            script.UPLOAD_START,
                            update.message,
                            start_time
                        )
                    )
                else:
                    logger.info("Did this happen? :\\")

                try:
                    shutil.rmtree(tmp_directory_for_each_user)
                except:
                    pass
                try:
                    os.remove(thumb_image_path)
                except:
                    pass

                await bot.edit_message_text(
                    text=script.AFTER_SUCCESSFUL_UPLOAD_MSG_WITH_TS,
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="馃檶馃徎 SHARE ME 馃檶馃徎", url="tg://msg?text=%2A%2AHai%20%E2%9D%A4%EF%B8%8F%2C%2A%2A%20%0A__Today%20i%20just%20found%20out%20an%20intresting%20and%20Powerful__%20%2A%2AZee5%20Downloader%20Bot%2A%2A%20__for%20Free%F0%9F%A5%B0.__%20%20%0A%2A%2ABot%20Link%20%3A%20%40Zee5HEXBot%2A%2A%20%F0%9F%94%A5")]]),
                    chat_id=update.message.chat.id,
                    message_id=update.message.message_id,
                    disable_web_page_preview=True
                )               
    except:
        await update.reply_text("Couldn't download your video!", quote=True)
        logger.info('error in process')
