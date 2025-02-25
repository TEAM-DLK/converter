from pyrogram import Client, filters
import os
import subprocess
import hashlib
from config import Config

bot = Client("AudioConverterBot", api_id=Config.API_ID, api_hash=Config.API_HASH, bot_token=Config.BOT_TOKEN)

file_data = {}  # Store audio file data (file_id and title)

# 🔹 Start Command with Sticker and Inline Buttons
@bot.on_message(filters.command("start"))
async def start(client, message):
    # Send a sticker first
    sticker_id = "CAACAgUAAxkBAAIIi2e-DwMaYKLZd06WiF_0KQuKLwNCAAIFDwACeswpVXELUmxGWKyfNgQ"  # Replace this with your sticker file_id or URL
    await message.reply_sticker(sticker_id)

    # Then send the welcome message
    await message.reply_text(
        "🎶 Welcome to the Audio Converter Bot! 🎵\n"
        "📂 Send an audio file to convert it to another format or edit it. 😎\n"
        "💬 Use /speed, /reverb, or /pitch to edit your audio."
    )

# 🔹 Speed Adjustment Command
@bot.on_message(filters.command("speed"))
async def change_speed(client, message):
    if not message.reply_to_message or not message.reply_to_message.audio:
        await message.reply_text("❌ Reply to an audio file to change speed.")
        return

    speed = message.text.split(" ")[1] if len(message.text.split(" ")) > 1 else "1.5"
    
    file_id = message.reply_to_message.audio.file_id
    file_name = message.reply_to_message.audio.file_name or "Unknown_Title"
    file_hash = hashlib.md5(str(file_id).encode()).hexdigest()[:8]

    # Process the audio and change speed using FFmpeg
    input_file = await client.download_media(file_id, file_name=f"{file_hash}_input")
    output_file = os.path.join(Config.DOWNLOAD_FOLDER, f"{file_hash}_speed_{speed}.mp3")

    command = [
        "ffmpeg", "-i", input_file, "-filter:a", f"atempo={speed}", "-vn", output_file
    ]
    
    try:
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        await message.reply_document(output_file, caption=f"✅ Your audio with speed {speed}x.")
        os.remove(output_file)  # Clean up
    except Exception as e:
        await message.reply_text(f"❌ Error changing speed: {e}")
    
    os.remove(input_file)

# 🔹 Reverb Effect Command
@bot.on_message(filters.command("reverb"))
async def add_reverb(client, message):
    if not message.reply_to_message or not message.reply_to_message.audio:
        await message.reply_text("❌ Reply to an audio file to add reverb effect.")
        return

    file_id = message.reply_to_message.audio.file_id
    file_name = message.reply_to_message.audio.file_name or "Unknown_Title"
    file_hash = hashlib.md5(str(file_id).encode()).hexdigest()[:8]

    # Process the audio and add reverb effect using FFmpeg
    input_file = await client.download_media(file_id, file_name=f"{file_hash}_input")
    output_file = os.path.join(Config.DOWNLOAD_FOLDER, f"{file_hash}_reverb.mp3")

    command = [
        "ffmpeg", "-i", input_file, "-filter:a", "aecho=0.8:0.9:1000:0.3", "-vn", output_file
    ]
    
    try:
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        await message.reply_document(output_file, caption="✅ Your audio with reverb effect.")
        os.remove(output_file)  # Clean up
    except Exception as e:
        await message.reply_text(f"❌ Error adding reverb: {e}")
    
    os.remove(input_file)

# 🔹 Pitch Adjustment Command
@bot.on_message(filters.command("pitch"))
async def adjust_pitch(client, message):
    if not message.reply_to_message or not message.reply_to_message.audio:
        await message.reply_text("❌ Reply to an audio file to adjust pitch.")
        return

    pitch = message.text.split(" ")[1] if len(message.text.split(" ")) > 1 else "1.0"
    
    file_id = message.reply_to_message.audio.file_id
    file_name = message.reply_to_message.audio.file_name or "Unknown_Title"
    file_hash = hashlib.md5(str(file_id).encode()).hexdigest()[:8]

    # Process the audio and adjust pitch using FFmpeg
    input_file = await client.download_media(file_id, file_name=f"{file_hash}_input")
    output_file = os.path.join(Config.DOWNLOAD_FOLDER, f"{file_hash}_pitch_{pitch}.mp3")

    command = [
        "ffmpeg", "-i", input_file, "-filter:a", f"asetrate={pitch}", "-vn", output_file
    ]
    
    try:
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        await message.reply_document(output_file, caption=f"✅ Your audio with pitch adjusted to {pitch}.")
        os.remove(output_file)  # Clean up
    except Exception as e:
        await message.reply_text(f"❌ Error adjusting pitch: {e}")
    
    os.remove(input_file)

# 🔹 User sends an audio file, bot extracts the title
@bot.on_message(filters.audio)
async def ask_format(client, message):
    file_id = message.audio.file_id  
    file_name = message.audio.file_name or "Unknown_Title"  # Extract title

    # Generate a unique identifier for the file
    file_hash = hashlib.md5(str(file_id).encode()).hexdigest()[:8]
    
    file_data[file_hash] = {"file_id": file_id, "title": file_name}  # Store data
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("MP3", callback_data=f"mp3_{file_hash}")],
        [InlineKeyboardButton("WAV", callback_data=f"wav_{file_hash}")],
        [InlineKeyboardButton("FLAC", callback_data=f"flac_{file_hash}")],
        [InlineKeyboardButton("M4A", callback_data=f"m4a_{file_hash}")]
    ])
    
    await message.reply_text(f"🎵 Choose format to convert '{file_name}':", reply_markup=keyboard)

# 🔹 Convert audio and rename using the title
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
    original_title = file_info["title"].split(".")[0]  # Remove extension
    sanitized_title = "".join(c for c in original_title if c.isalnum() or c in " _-")  # Remove special chars
    new_title = f"{sanitized_title}.{output_format}"  # Rename with new format

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

    # FFmpeg command
    command = [
        "ffmpeg", "-i", file_path
    ] + codec_map[output_format]

    command += ["-y", output_file]

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
        os.remove(output_file)  # Clean up
    except Exception as e:
        await callback_query.message.reply_text(f"❌ Error converting file: {e}")

    # Cleanup input file
    os.remove(file_path)

bot.run()