# 📊 Telegram Gold Price Bot

This is a powerful Telegram bot designed for **automated and manual gold pricing management**. It includes admin-only controls, custom price adjustments, source channel monitoring, and automatic formatting and forwarding of price messages to a destination channel.

---

## ✨ Features

- Enable/disable bot manually
- Set price adjustment margins (buy/sell per gram or misqal)
- Manually define prices (USD, ounce, global misqal)
- Parse and process messages from a source channel
- Format and forward final price message to a destination channel
- Secure access: only the defined admin can control the bot

---

## ⚙️ Requirements

- Python 3.9+
- [Telethon](https://github.com/LonamiWebs/Telethon)
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- SQLAlchemy
- nest_asyncio

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 📁 Project Structure

```
.
├── main.py               # Main bot script
├── bot_config.py         # API keys and configuration
├── database_bot.py       # Database handling functions
└── requirements.txt      # Python dependencies
```

---

## 🚀 Getting Started

1. Create a `bot_config.py` file with the following structure:

```python
api_id = 123456
api_hash = "your_api_hash"
phone_number = "+98xxxxxxxxxx"  # Your phone number for the userbot session
bot_token = "your_bot_token"
admin_id = 123456789            # Numeric Telegram ID of the admin
channel_destination = "@your_channel_username"
```

2. Run the bot:

```bash
python main.py
```

You will be asked to log in once (for userbot session). After that, the bot will start listening for source channel messages and admin commands.

---

## 🧪 Admin Commands

Once the admin sends `/start`:

- Interactive keyboard with options appears
- Set source channel by sending its `@username`
- Adjust pricing margins (increase/decrease)
- Start manual pricing step-by-step
- Confirm message before sending to channel

All inputs are validated and stored in the database.

---

## 🔐 Security

- Only the defined `admin_id` has access to the bot controls
- The bot ignores messages from unauthorized users
- The source channel must match the configured username or ID

---

## 🧠 How It Works

- The bot monitors a source Telegram channel for pricing messages.
- It parses values like **buy/sell price**, **USD**, **ounce**, and **global misqal**.
- Based on configured margins, it recalculates prices.
- The final message is formatted in a specific structure and sent to the destination channel.

---

## 🧾 License

MIT License. Free to use and modify with credit.

---

## 👨‍💻 Developer

Developed by [Matin Ebadi](https://github.com/matinebadi)  
Project: Atlas Gold Gallery 🔱

---
