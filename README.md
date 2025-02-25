# Telegram Audio Converter Bot

A Telegram bot designed to convert audio files into various formats, supporting features like bitrate selection, metadata editing, and batch processing.

## Features

- **Supported Formats**: MP3, WAV, FLAC, M4A, OGG, OPUS
- **Bitrate Selection**: Options include 128kbps, 192kbps, and 320kbps
- **Metadata Editing**: Modify Title, Artist, and Album information
- **Batch Conversion**: Process multiple files simultaneously
- **Deployment Options**: Compatible with Heroku and VPS setups

## Installation

### Prerequisites

- Python installed on your system
- FFmpeg installed and accessible in your system's PATH

### Steps

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/TEAM-DLK/converter.git
   cd converter

	2.	Install Dependencies:

pip install -r requirements.txt


	3.	Set Up Environment Variables:
Create a .env file in the project directory with the following content:

API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token

Replace your_api_id, your_api_hash, and your_bot_token with your actual Telegram API credentials.

	4.	Run the Bot:

python bot.py



Deployment

Deploying to Heroku
	1.	Install Heroku CLI: Ensure you have the Heroku CLI installed.
	2.	Log In to Heroku:

heroku login


	3.	Create a New Heroku App:

heroku create your-app-name


	4.	Add FFmpeg Buildpack:

heroku buildpacks:add https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git


	5.	Deploy the Code:

git init
git add .
git commit -m "Initial commit"
git push heroku master


	6.	Set Environment Variables:
Configure your Telegram API credentials on Heroku:

heroku config:set API_ID=your_api_id
heroku config:set API_HASH=your_api_hash
heroku config:set BOT_TOKEN=your_bot_token



Deploying on a VPS
	1.	Install FFmpeg:

# For Debian/Ubuntu
sudo apt-get update
sudo apt-get install ffmpeg

# For CentOS
sudo yum install epel-release
sudo yum install ffmpeg


	2.	Follow the Installation Steps: As outlined in the Installation section above.

Usage

Once the bot is running, you can interact with it on Telegram:
	1.	Start a Chat: Find your bot on Telegram and start a conversation.
	2.	Send Audio Files: Upload the audio files you wish to convert.
	3.	Select Conversion Options: Choose the desired format and bitrate.
	4.	Receive Converted Files: The bot will process and return the converted files.

Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

License

This project is licensed under the MIT License. See the LICENSE file for details.
