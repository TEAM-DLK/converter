from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import subprocess
import hashlib
import re
from config import Config

bot = Client("AudioConverterBot", api_id=Config.API_ID, api_hash=Config.API_HASH, bot_token=Config.BOT_TOKEN)

file_data = {}  # Store audio file data (file_id and title)

# 🔹 Updated File Name Sanitization Function (Supports more languages including Sinhala)
def sanitize_filename(filename: str):
    # Allow alphanumeric characters, spaces, underscores, hyphens, and all Unicode characters including Sinhala
    return re.sub(r'[<>:"/\\|?*\x00-\x1F]', '', filename)

# 🔹 Start Command with Sticker and Inline Buttons
@bot.on_message(filters.command("start"))
async def start(client, message):
    # Send a sticker first
    sticker_id = "CAACAgUAAxkBAAIIi2e-DwMaYKLZd06WiF_0KQuKLwNCAAIFDwACeswpVXELUmxGWKyfNgQ"  # Replace with your sticker file_id
    await message.reply_sticker(sticker_id)

    # Stylish Start Message
    start_text = (
        "🎵 **Welcome to Audio Converter Bot!** 🎶\n\n"
        "🔹 Send me an **audio file**, and I'll convert it into your desired format.\n"
        "🔹 Choose from **MP3, WAV, FLAC, and M4A** formats.\n"
        "🔹 Fast, **high-quality conversion** with FFmpeg. 🚀\n\n"
        "⚡ **Let's get started!** Just send an audio file below. ⬇️"
    )

    # Inline Buttons
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("👨‍💻 Owner", url="https://t.me/iiiIiiiAiiiMiii")],
        [InlineKeyboardButton("📢 Updates", url="https://t.me/DLKDevelopers")]
    ])

    await message.reply_text(start_text, reply_markup=keyboard)


# 🔹 User Sends an Audio File
@bot.on_message(filters.audio)
async def ask_format(client, message):
    file_id = message.audio.file_id  
    file_name = message.audio.file_name or "Unknown_Title"

    # Generate a unique identifier for the file
    file_hash = hashlib.md5(str(file_id).encode()).hexdigest()[:8]
    
    file_data[file_hash] = {"file_id": file_id, "title": file_name}  

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎵 MP3", callback_data=f"mp3_{file_hash}")],
        [InlineKeyboardButton("🎼 WAV", callback_data=f"wav_{file_hash}")],
        [InlineKeyboardButton("🎶 FLAC", callback_data=f"flac_{file_hash}")],
        [InlineKeyboardButton("🎧 M4A", callback_data=f"m4a_{file_hash}")]
    ])
    
    await message.reply_text(f"🎼 **Select the format** to convert `{file_name}`:", reply_markup=keyboard)


# 🔹 Convert Audio and Rename Using Title
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

    user_id = callback_query.from_user.id
    file_id = file_info["file_id"]
    original_title = file_info["title"].split(".")[0]  
    sanitized_title = sanitize_filename(original_title)  # Use new sanitized function
    new_title = f"{sanitized_title}.{output_format}"

    input_file = os.path.join(Config.DOWNLOAD_FOLDER, f"{file_hash}_input")
    output_file = os.path.join(Config.DOWNLOAD_FOLDER, new_title)
    
    # Download the media file
    file_path = await client.download_media(file_id, file_name=input_file)

    # Ensure output file doesn't exist
    if os.path.exists(output_file):
        os.remove(output_file)

    # Define FFmpeg codec mapping
    codec_map = {
        "mp3": ["-c:a", "libmp3lame"],
        "wav": ["-c:a", "pcm_s16le"],
        "flac": ["-c:a", "flac"],
        "m4a": ["-c:a", "aac"]
    }

    # FFmpeg Command
    command = ["ffmpeg", "-i", file_path] + codec_map[output_format] + ["-y", output_file]

    try:
        # Show processing message
        processing_msg = await callback_query.message.reply_text(
            "⏳ **Processing your file...**\n"
            f"🎛️ Converting to `{output_format.upper()}` format..."
        )

        # Run FFmpeg and capture errors
        process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if process.returncode != 0:
            error_msg = process.stderr.decode()
            await callback_query.message.reply_text(f"❌ **Conversion Failed!**\n```\n{error_msg}\n```", parse_mode="markdown")
            return

        # ✅ Send Converted File
        await callback_query.message.reply_document(
            output_file, 
            caption=(
                "🎉 **Conversion Successful!** 🎵\n\n"
                f"✅ **File:** `{new_title}`\n"
                f"🎧 **Format:** `{output_format.upper()}`\n"
                "🚀 **High-quality FFmpeg conversion completed!**\n\n"
                "💡 **Join our updates for more cool tools!**"
            ),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 Updates", url="https://t.me/DLKDevelopers")]
            ])
        )

        os.remove(output_file)  # Cleanup output file
        await processing_msg.delete()  # Remove processing message

    except Exception as e:
        await callback_query.message.reply_text(f"❌ **Error:** {e}")

    os.remove(file_path)  # Cleanup input file


# Run the bot
bot.run()