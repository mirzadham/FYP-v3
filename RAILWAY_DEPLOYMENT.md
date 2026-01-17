# Railway Deployment Guide

Deploy the Academic Advisor Chatbot to Railway with automatic GitHub integration.

## Prerequisites

- Railway account at [railway.app](https://railway.app)
- GitHub repository connected
- Required API keys:
  - Rasa Pro license
  - OpenAI API key
  - Telegram bot token

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Railway Project                          │
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  PostgreSQL  │    │ rasa-server  │    │action-server │  │
│  │  (Database)  │◄───│  (Dockerfile)│───►│(Dockerfile.actions)│  │
│  │              │    │              │    │  (Actions)   │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         ▲                   ▲                              │
│         │                   │                              │
│         └───────────────────┼──────────────────────────────│
│                             │                              │
└─────────────────────────────┼──────────────────────────────┘
                              │
                     ┌────────▼────────┐
                     │    Telegram     │
                     │    (Webhook)    │
                     └─────────────────┘
```

## Step-by-Step Setup

### 1. Create Railway Project

1. Go to [railway.app/new](https://railway.app/new)
2. Click **"Deploy from GitHub repo"**
3. Select your `AcademicAdvisor-Chatbot-V3` repository
4. Railway creates your first service automatically

### 2. Add PostgreSQL Database

1. In your Railway project, click **"+ New"**
2. Select **"Database"** → **"PostgreSQL"**
3. Railway auto-creates the database
4. The `DATABASE_URL` variable is automatically available to link

### 3. Create Action Server Service

1. Click **"+ New"** → **"GitHub Repo"**
2. Select your repository again
3. Click on the new service → **"Settings"**
4. Configure:
   - **Service Name**: `action-server`
   - **Root Directory**: Leave empty
   - **Dockerfile Path**: `Dockerfile.actions`
5. Go to **"Variables"** tab and add:
   - `RASA_PRO_LICENSE` = Your Rasa Pro license

### 4. Configure Rasa Server Service

1. Click on the first service (auto-created in step 1)
2. Go to **"Settings"** and configure:
   - **Service Name**: `rasa-server`
   - **Dockerfile Path**: `Dockerfile`
3. Go to **"Variables"** tab and add:

| Variable | Value |
|----------|-------|
| `RASA_PRO_LICENSE` | Your Rasa Pro license |
| `OPENAI_API_KEY` | Your OpenAI API key |
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token |
| `TELEGRAM_BOT_USERNAME` | `UPMAcademicAdvisorBot` |
| `DATABASE_URL` | `${{PostgreSQL.DATABASE_URL}}` (click "Add Reference") |
| `ACTION_SERVER_URL` | `http://action-server.railway.internal:8080/webhook` |
| `RASA_SERVER_URL` | (set after step 5) |

### 5. Generate Public Domain

1. Click on `rasa-server` service
2. Go to **"Settings"** → **"Networking"**
3. Click **"Generate Domain"**
4. Copy the URL (e.g., `https://rasa-server-production-xxxx.up.railway.app`)
5. Go back to **"Variables"** and set:
   - `RASA_SERVER_URL` = The URL you just copied

### 6. Set Telegram Webhook

Run this command (replace `<TOKEN>` and `<RAILWAY_URL>`):

```bash
curl "https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook?url=<RAILWAY_URL>/webhooks/telegram/webhook"
```

Example:
```bash
curl "https://api.telegram.org/bot123456789:ABCdefGHI/setWebhook?url=https://rasa-server-production-xxxx.up.railway.app/webhooks/telegram/webhook"
```

You should see: `{"ok":true,"result":true,"description":"Webhook was set"}`

### 7. Test Your Bot

Send a message to your Telegram bot! 🎉

## Automatic Deployments

Railway automatically deploys when you push to `main`:

```bash
# Make changes
git add .
git commit -m "Update feature"
git push origin main

# Railway auto-deploys! 🚀
```

No GitHub Actions or CI/CD configuration needed.

## Monitoring

- **Logs**: Click service → "Deployments" → "View Logs"
- **Metrics**: Service → "Metrics" tab
- **Database**: Click PostgreSQL → "Data" tab

## Estimated Costs (Hobby Plan)

| Resource | Monthly Cost |
|----------|--------------|
| PostgreSQL | ~$5 |
| Rasa Server | ~$10-15 |
| Action Server | ~$5-10 |
| **Total** | **~$20-30** |

*These are rough estimates. Railway pricing and any free credits can change over time—check Railway's current pricing page for the latest details and your actual charges.*

## Troubleshooting

### Build Fails
- Check Dockerfile path is correctly set in service settings
- View build logs: Service → Deployments → click on failed deployment
- Verify all files are committed and pushed

### Service Crashes or Won't Start
- Check "View Logs" for error messages
- Verify all required environment variables are set
- Ensure `RASA_PRO_LICENSE` is valid

### Database Connection Failed
- Verify `DATABASE_URL` references PostgreSQL service correctly
- Use Railway's "Add Reference" feature: `${{PostgreSQL.DATABASE_URL}}`

### Telegram Not Responding
- Verify webhook URL is set correctly (use curl command above)
- Check `RASA_SERVER_URL` matches the Railway domain exactly
- Ensure rasa-server service is running (green status)
- Check logs for webhook-related errors

### Action Server Not Responding
- Verify `ACTION_SERVER_URL` uses internal networking format
- Format: `http://action-server.railway.internal:8080/webhook`
- Check action-server logs for errors

## Local Development

For local testing, use docker-compose:

```bash
docker-compose up --build
```

This uses the same Dockerfiles but with local PostgreSQL.
