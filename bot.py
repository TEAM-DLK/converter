from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import ffmpeg
from config import Config

bot = Client("AudioConverterBot", api_id=Config.API_ID, api_hash=Config.API_HASH, bot_token=Config.BOT_TOKEN)

# 🔹 User sends an audio file, and bot asks for format selection
@bot.on_message(filters.audio)
async def ask_format(client, message):
    file_id = message.audio.file_id  # Store the file_id
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("MP3", callback_data=f"mp3_{file_id}")],
        [InlineKeyboardButton("WAV", callback_data=f"wav_{file_id}")],
        [InlineKeyboardButton("FLAC", callback_data=f"flac_{file_id}")],
        [InlineKeyboardButton("M4A", callback_data=f"m4a_{file_id}")]
    ])
    await message.reply_text("🔄 Choose the format to convert:", reply_markup=keyboard)

# 🔹 Handle format conversion when user selects a format
@bot.on_callback_query()
async def convert_audio(client, callback_query):
    data_parts = callback_query.data.split("_")
    if len(data_parts) != 2:
        await callback_query.answer("❌ Invalid request!")
        return

    format_map = {
        "mp3": "mp3",
        "wav": "wav",
        "flac": "flac",
        "m4a": "m4a"
    }
    
    output_format = format_map.get(data_parts[0])  # Get the format (mp3, wav, etc.)
    audio_file_id = data_parts[1]  # Get the file ID from the callback

    if not output_format:
        await callback_query.answer("❌ Invalid format choice!")
        return

    # Download the audio file using the file_id
    file_path = await client.download_media(audio_file_id, file_name=f"{Config.DOWNLOAD_FOLDER}input_audio")
    output_path = f"{Config.DOWNLOAD_FOLDER}converted.{output_format}"

    try:
        ffmpeg.input(file_path).output(output_path).run(overwrite_output=True)
        await callback_query.message.reply_document(output_path, caption=f"✅ Here is your converted file ({output_format}) 🎵")
        os.remove(output_path)
    except Exception as e:
        await callback_query.message.reply_text(f"❌ Error converting file: {e}")

    os.remove(file_path)

bot.run()