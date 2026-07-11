
# NoElephant

> **Note:** The bot is still under development.


Telegram bot for helping non-native Italian speakers prepare for job interviews.

## Current scope
- Start bot with `/start`
- Select Italian level
- Select feedback language
- Select task
- Upload CV as PDF or DOCX
- Perform technical validation
- Extract CV text and show preview

## Install requirements

```bash
python -m pip install -r requirements.txt
````

## Environment variables

Rename `.env.example` to `.env` and add your Telegram bot token:

```env
TELEGRAM_TOKEN=your_telegram_token_here
```

## Run

```bash
python bot.py
```
