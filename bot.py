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
        [InlineKeyboardButton("MP3", callback_data="convert_mp3"),
         InlineKeyboardButton("WAV", callback_data="convert_wav")],
        [InlineKeyboardButton("FLAC", callback_data="convert_flac"),
         InlineKeyboardButton("M4A", callback_data="convert_m4a")]
    ])
    await message.reply_text("🔄 Choose the format to convert:", reply_markup=keyboard)

# 🔹 Handle format conversion when user selects a format
@bot.on_callback_query()
async def convert_audio(client, callback_query):
    format_map = {
        "convert_mp3": "mp3",
        "convert_wav": "wav",
        "convert_flac": "flac",
        "convert_m4a": "m4a"
    }
    
    output_format = format_map.get(callback_query.data)
    if not output_format:
        await callback_query.answer("❌ Invalid choice!")
        return
    
    message = callback_query.message.reply_to_message
    audio = message.audio
    file_path = await client.download_media(audio, file_name=Config.DOWNLOAD_FOLDER + audio.file_name)
    output_path = f"{Config.DOWNLOAD_FOLDER}converted.{output_format}"

    try:
        ffmpeg.input(file_path).output(output_path).run(overwrite_output=True)
        await callback_query.message.reply_document(output_path, caption=f"✅ Here is your converted file ({output_format}) 🎵")
        os.remove(output_path)
    except Exception as e:
        await callback_query.message.reply_text(f"❌ Error converting file: {e}")

    os.remove(file_path)

bot.run()
