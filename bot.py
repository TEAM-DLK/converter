from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import subprocess
import hashlib
from config import Config

bot = Client("AudioConverterBot", api_id=Config.API_ID, api_hash=Config.API_HASH, bot_token=Config.BOT_TOKEN)

file_data = {}  # Store audio file data

# 🔹 Set your custom thumbnail image (Upload your image and replace the file path)
CUSTOM_THUMBNAIL = "DevDLK.jpg"  # Replace with your image file path

# 🔹 User sends an audio file, bot extracts the title
@bot.on_message(filters.audio)
async def ask_format(client, message):
    file_id = message.audio.file_id  
    file_name = message.audio.file_name or "Unknown_Title"

    # Generate a unique identifier for the file
    file_hash = hashlib.md5(str(file_id).encode()).hexdigest()[:8]
    
    file_data[file_hash] = {"file_id": file_id, "title": file_name}  
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("MP3", callback_data=f"mp3_{file_hash}")],
        [InlineKeyboardButton("WAV", callback_data=f"wav_{file_hash}")],
        [InlineKeyboardButton("FLAC", callback_data=f"flac_{file_hash}")],
        [InlineKeyboardButton("M4A", callback_data=f"m4a_{file_hash}")]
    ])
    
    await message.reply_text(f"🎵 Choose format to convert '{file_name}':", reply_markup=keyboard)

# 🔹 Convert audio and add your custom thumbnail
@bot.on_callback_query()
async def convert_audio(client, callback_query):
    data_parts = callback_query.data.split("_")
    if len(data_parts) != 2:
        await callback_query.answer("❌ Invalid request!")
        return

    format_map = {"mp3": "mp3", "wav": "wav", "flac": "flac", "m4a": "m4a"}
    output_format = format_map.get(data_parts[0])
    file_hash = data_parts[1]

    if not output_format:
        await callback_query.answer("❌ Invalid format choice!")
        return

    file_info = file_data.get(file_hash)
    if not file_info:
        await callback_query.answer("❌ File ID not found!")
        return

    file_id = file_info["file_id"]
    original_title = file_info["title"].split(".")[0]  # Remove extension
    new_title = f"{original_title}.{output_format}"  # Rename with new format

    input_file = f"{Config.DOWNLOAD_FOLDER}/input_audio"
    output_file = f"{Config.DOWNLOAD_FOLDER}/{new_title}"
    
    file_path = await client.download_media(file_id, file_name=input_file)

    # FFmpeg command with your custom thumbnail
    command = [
        "ffmpeg", "-i", file_path, "-i", CUSTOM_THUMBNAIL,
        "-map", "0:a", "-map", "1:v", "-c:v", "jpeg", "-disposition:v", "attached_pic",
        "-y", output_file
    ]

    try:
        subprocess.run(command, check=True)
        await callback_query.message.reply_document(output_file, caption=f"✅ Here is your converted file: **{new_title}** 🎵")
        os.remove(output_file)
    except Exception as e:
        await callback_query.message.reply_text(f"❌ Error converting file: {e}")

    os.remove(file_path)

bot.run()