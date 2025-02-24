# 🎵 Telegram Audio Converter Bot  

A Telegram bot that converts audio files into different formats (MP3, WAV, FLAC, M4A).  
Supports **bitrate selection**, **metadata editing**, and **batch conversion**.  

---

## 🚀 Features  
✅ Convert **MP3, WAV, FLAC, M4A, OGG, OPUS**  
✅ Choose **bitrate (128kbps, 192kbps, 320kbps)**  
✅ Supports **metadata editing (Title, Artist, Album)**  
✅ Allows **batch conversion (multiple files at once)**  
✅ **Deploy on Heroku or VPS**  

---

## 🔧 Installation  

### **1️⃣ Install Dependencies**  
```sh
pip install -r requirements.txt

2️⃣ Set Up Environment Variables

Create a .env file and add:

API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token

🎯 Deploy on Heroku

heroku login
heroku create your-bot-name
git init
git add .
git commit -m "Deploying bot"
git push heroku master
heroku ps:scale worker=1

💻 Run Locally

python bot.py

📜 License

This bot is open-source and free to use. Feel free to contribute!