from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import subprocess
import hashlib
from config import Config

bot = Client("AudioConverterBot", api_id=Config.API_ID, api_hash=Config.API_HASH, bot_token=Config.BOT_TOKEN)

file_data = {}

# 🔹 Start Command with Sticker and Inline Buttons
@bot.on_message(filters.command("start"))
async def start(client, message):
    sticker_id = "CAACAgUAAxkBAAIIi2e-DwMaYKLZd06WiF_0KQuKLwNCAAIFDwACeswpVXELUmxGWKyfNgQ"
    await message.reply_sticker(sticker_id)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Owner", url="https://t.me/iiiIiiiAiiiMiii")],
        [InlineKeyboardButton("Updates", url="https://t.me/DLKDevelopers")]
    ])
    await message.reply_text(
        "🎶 Welcome to the Audio Converter Bot! 🎵\n"
        "📂 Send an audio file to convert it to another format. 😎",
        reply_markup=keyboard
    )

# 🔹 User sends an audio file, bot extracts the title
@bot.on_message(filters.audio)
async def ask_format(client, message):
    file_id = message.audio.file_id
    file_name = message.audio.file_name or "Unknown_Title"

    file_hash = hashlib.md5(str(file_id).encode()).hexdigest()[:8]
    file_data[file_hash] = {"file_id": file_id, "title": file_name}

    # Provide options for converting to different formats
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("MP3", callback_data=f"mp3_{file_hash}")],
        [InlineKeyboardButton("WAV", callback_data=f"wav_{file_hash}")],
        [InlineKeyboardButton("FLAC", callback_data=f"flac_{file_hash}")],
        [InlineKeyboardButton("M4A", callback_data=f"m4a_{file_hash}")]
    ])

    await message.reply_text(f"🎵 Choose format for '{file_name}':", reply_markup=keyboard)

# 🔹 User selects a format, now they can choose effects (speed and pitch)
@bot.on_callback_query(filters.regex(r"^(mp3|wav|flac|m4a)_(.*)"))
async def choose_effects(client, callback_query):
    data_parts = callback_query.data.split("_")
    
    if len(data_parts) < 2:
        await callback_query.answer("❌ Invalid request!")
        return

    format_choice = data_parts[0]
    file_hash = data_parts[1]
    
    file_info = file_data.get(file_hash)
    if not file_info:
        await callback_query.answer(f"❌ File with hash {file_hash} not found!")
        return

    file_id = file_info["file_id"]
    file_name = file_info["title"]

    # Ask user if they want to adjust speed or pitch
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Speed Up", callback_data=f"speed_up_{file_hash}")],
        [InlineKeyboardButton("Slow Down", callback_data=f"slow_down_{file_hash}")],
        [InlineKeyboardButton("Higher Pitch", callback_data=f"higher_pitch_{file_hash}")],
        [InlineKeyboardButton("Lower Pitch", callback_data=f"lower_pitch_{file_hash}")],
        [InlineKeyboardButton("No Effects", callback_data=f"no_effects_{file_hash}")]
    ])

    await callback_query.message.reply_text(
        f"🎵 You've selected **{file_name}** to convert to {format_choice.upper()}.\n"
        "Do you want to adjust speed or pitch? Choose an effect below, or select 'No Effects' to convert without any effects.",
        reply_markup=keyboard
    )

# 🔹 Apply speed and pitch adjustments
@bot.on_callback_query(filters.regex(r"^(speed_up|slow_down|higher_pitch|lower_pitch|no_effects)_(.*)"))
async def apply_effects(client, callback_query):
    data_parts = callback_query.data.split("_")
    
    if len(data_parts) < 2:
        await callback_query.answer("❌ Invalid request!")
        return

    effect_choice = data_parts[0]
    file_hash = data_parts[1]
    
    file_info = file_data.get(file_hash)
    if not file_info:
        await callback_query.answer(f"❌ File with hash {file_hash} not found!")
        return

    file_id = file_info["file_id"]
    original_title = file_info["title"].split(".")[0]
    sanitized_title = "".join(c for c in original_title if c.isalnum() or c in " _-")
    new_title = f"{sanitized_title}_converted"

    # Select the output format based on user's previous choice
    output_format = data_parts[0]
    new_title += f".{output_format}"

    input_file = os.path.join(Config.DOWNLOAD_FOLDER, f"{file_hash}_input")
    output_file = os.path.join(Config.DOWNLOAD_FOLDER, new_title)

    # Download the media file
    file_path = await client.download_media(file_id, file_name=input_file)

    if os.path.exists(output_file):
        os.remove(output_file)

    # Setup FFmpeg effect commands
    speed_cmd = ""
    pitch_cmd = ""

    if effect_choice == "speed_up":
        speed_cmd = "-filter:a \"atempo=1.5\" "  # Speed up by 1.5x
    elif effect_choice == "slow_down":
        speed_cmd = "-filter:a \"atempo=0.7\" "  # Slow down by 0.7x
    elif effect_choice == "higher_pitch":
        pitch_cmd = "-filter:a \"asetrate=44100*1.2,aresample=44100\" "  # Raise pitch
    elif effect_choice == "lower_pitch":
        pitch_cmd = "-filter:a \"asetrate=44100*0.8,aresample=44100\" "  # Lower pitch
    elif effect_choice == "no_effects":
        pass  # No speed/pitch adjustments

    # FFmpeg command to apply the effects and convert
    command = [
        "ffmpeg", "-i", file_path,
        speed_cmd, pitch_cmd,
        "-y", output_file
    ]

    try:
        # Run FFmpeg and capture errors
        process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if process.returncode != 0:
            error_msg = process.stderr.decode()
            await callback_query.message.reply_text(f"❌ FFmpeg Error:\n```{error_msg}```", parse_mode="markdown")
            return

        # Send the converted file
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Join Update Channel", url="https://t.me/DLKDevelopers")]
        ])

        await callback_query.message.reply_document(output_file, caption=f"✅ Here is your converted file: **{new_title}** 🎵", reply_markup=keyboard)
        os.remove(output_file)
    except Exception as e:
        await callback_query.message.reply_text(f"❌ Error processing file: {e}")

    os.remove(file_path)

bot.run()