# Local Demo Setup Guide

Run the Academic Advisor Chatbot locally without Docker or cloud deployment.

## Prerequisites

1. **Python 3.10** installed
2. **ngrok** installed ([download here](https://ngrok.com/download))
3. **Telegram Bot Token** (from BotFather)
4. **OpenAI API Key** (for LLM-powered responses)
5. **Rasa Pro License** (from Rasa)

## Quick Start

### 1. Setup Environment

```powershell
# Clone/navigate to project
cd "c:\Users\ADMIN 2025\Documents\AcademicAdvisor-Chatbot-V3"

# Create virtual environment (if not exists)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```
RASA_LICENSE = <your-rasa-pro-license>
OPENAI_API_KEY = <your-openai-api-key>
TELEGRAM_BOT_TOKEN = <your-telegram-bot-token>
```

### 3. Train Model (if needed)

```powershell
rasa train
```

### 4. Run the Bot

**Option A: Using the script (recommended)**
```powershell
.\scripts\run_local.ps1
```

**Option B: Manual startup**
```powershell
# Terminal 1: Action Server
.\venv\Scripts\Activate.ps1
rasa run actions --port 5055

# Terminal 2: Rasa Server
.\venv\Scripts\Activate.ps1
rasa run --enable-api --cors "*" --port 5005 --endpoints endpoints.local.yml --credentials credentials.local.yml
```

### 5. Setup Telegram Webhook

```powershell
# Terminal 3: Start ngrok
ngrok http 5005
```

Copy the HTTPS URL from ngrok (e.g., `https://abc123.ngrok.io`)

Set the webhook:
```
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=<NGROK_URL>/webhooks/telegram/webhook
```

### 6. Test the Bot

Open Telegram and message your bot!

---

## Troubleshooting

### Bot not responding?
- Check if all terminals are running (action server + rasa server + ngrok)
- Verify the webhook is set correctly: `https://api.telegram.org/bot<TOKEN>/getWebhookInfo`

### ngrok session expired?
- Free ngrok sessions expire after ~2 hours
- Restart ngrok and update the webhook URL

### Model training fails?
- Ensure `RASA_LICENSE` is set in your `.env`
- Check for syntax errors in domain/data files

### "No module named X" errors?
- Activate the virtual environment: `.\venv\Scripts\Activate.ps1`
- Reinstall dependencies: `pip install -r requirements.txt`

---

## Demo Day Checklist

- [ ] Laptop fully charged or plugged in
- [ ] All terminals open and running before presenting
- [ ] Test bot works before going live
- [ ] Have backup phone for Telegram if demo phone fails
- [ ] Keep ngrok terminal visible to catch any disconnections
