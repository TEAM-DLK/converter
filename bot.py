from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import subprocess
import hashlib
from config import Config

bot = Client("AudioConverterBot", api_id=Config.API_ID, api_hash=Config.API_HASH, bot_token=Config.BOT_TOKEN)

file_data = {}  # Store audio file data (file_id and title)
selected_effects = {}  # Store selected effects for each file

# Function to generate a short file hash (8 characters from the md5 hash)
def generate_short_file_hash(file_id):
    return hashlib.md5(str(file_id).encode()).hexdigest()[:8]  # Take only the first 8 characters

# 🔹 Start Command with Sticker and Inline Buttons
@bot.on_message(filters.command("start"))
async def start(client, message):
    # Send a sticker first
    sticker_id = "CAACAgUAAxkBAAIIi2e-DwMaYKLZd06WiF_0KQuKLwNCAAIFDwACeswpVXELUmxGWKyfNgQ"  # Replace this with your sticker file_id or URL
    await message.reply_sticker(sticker_id)

    # Then send the welcome message with inline buttons
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
    file_name = message.audio.file_name or "Unknown_Title"  # Extract title

    # Generate a unique, short identifier for the file (limit to 8 characters)
    file_hash = generate_short_file_hash(file_id)
    
    file_data[file_hash] = {"file_id": file_id, "title": file_name}  # Store data
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("MP3", callback_data=f"mp3_{file_hash}")],
        [InlineKeyboardButton("WAV", callback_data=f"wav_{file_hash}")],
        [InlineKeyboardButton("FLAC", callback_data=f"flac_{file_hash}")],
        [InlineKeyboardButton("M4A", callback_data=f"m4a_{file_hash}")]
    ])
    
    await message.reply_text(f"🎵 Choose format to convert '{file_name}':", reply_markup=keyboard)

# 🔹 /edit Command to apply effects and select format
@bot.on_message(filters.command("edit"))
async def edit_audio(client, message):
    file_hash = message.reply_to_message.audio.file_id
    original_title = message.reply_to_message.audio.file_name.split(".")[0]  # Remove extension
    sanitized_title = "".join(c for c in original_title if c.isalnum() or c in " _-")  # Remove special chars

    # Send options for applying effects
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Slow", callback_data=f"slow_{file_hash}")],
        [InlineKeyboardButton("Reverb", callback_data=f"reverb_{file_hash}")],
        [InlineKeyboardButton("Pitch Down", callback_data=f"pitchdown_{file_hash}")],
        [InlineKeyboardButton("No Effects", callback_data=f"noeffects_{file_hash}")]
    ])

    await message.reply_text(
        "🎶 Choose an effect to apply to the audio. 🎵",
        reply_markup=keyboard
    )

# 🔹 User selects an effect via inline buttons
@bot.on_callback_query()
async def apply_effect_and_convert(client, callback_query):
    data_parts = callback_query.data.split("_")
    if len(data_parts) != 2:
        await callback_query.answer("❌ Invalid request!")
        return

    effect = data_parts[0].lower()
    file_hash = data_parts[1]

    # Store the selected effect
    selected_effects[file_hash] = effect

    # Respond to user
    await callback_query.answer(f"Effect '{effect}' selected! Now choose the output format.")

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("MP3", callback_data=f"mp3_{file_hash}")],
        [InlineKeyboardButton("WAV", callback_data=f"wav_{file_hash}")],
        [InlineKeyboardButton("FLAC", callback_data=f"flac_{file_hash}")],
        [InlineKeyboardButton("M4A", callback_data=f"m4a_{file_hash}")]
    ])

    await callback_query.message.edit_text(
        f"🎶 Effect '{effect}' applied! Now choose the format to convert your file.",
        reply_markup=keyboard
    )

# 🔹 Convert audio and apply effects
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

    # Apply effects (slow, reverb, pitch down)
    effect = selected_effects.get(file_hash)
    if effect == "slow":
        command += ["-filter:a", "atempo=0.5"]
    elif effect == "reverb":
        command += ["-filter:a", "aecho=0.8:0.88:60:0.4"]
    elif effect == "pitchdown":
        command += ["-filter:a", "asetrate=44100*0.8,aresample=44100"]

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