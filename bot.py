from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import ffmpeg
from config import Config

bot = Client("AudioConverterBot", api_id=Config.API_ID, api_hash=Config.API_HASH, bot_token=Config.BOT_TOKEN)

# 🔹 User sends an audio file, and bot asks for format selection
@bot.on_message(filters.audio)
async def ask_format(client, message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("MP3", callback_data=f"convert_mp3_{message.audio.file_id}"),
         InlineKeyboardButton("WAV", callback_data=f"convert_wav_{message.audio.file_id}")],
        [InlineKeyboardButton("FLAC", callback_data=f"convert_flac_{message.audio.file_id}"),
         InlineKeyboardButton("M4A", callback_data=f"convert_m4a_{message.audio.file_id}")]
    ])
    await message.reply_text("🔄 Choose the format to convert:", reply_markup=keyboard)

# 🔹 Handle format conversion when user selects a format
@bot.on_callback_query()
async def convert_audio(client, callback_query):
    data_parts = callback_query.data.split("_")
    if len(data_parts) != 3:
        await callback_query.answer("❌ Invalid request!")
        return

    format_map = {
        "convert_mp3": "mp3",
        "convert_wav": "wav",
        "convert_flac": "flac",
        "convert_m4a": "m4a"
    }
    
    output_format = format_map.get(f"{data_parts[0]}_{data_parts[1]}")
    audio_file_id = data_parts[2]

    if not output_format:
        await callback_query.answer("❌ Invalid format choice!")
        return
    
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