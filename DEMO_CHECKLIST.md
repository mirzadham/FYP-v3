# FYP Demonstration Checklist

> Complete this checklist **before** your demonstration to prevent common failures.

---

## 📋 Preparation (Day Before)

### Environment Setup
- [ ] Python 3.10 installed and verified
- [ ] Virtual environment created (`.\venv\Scripts\Activate.ps1`)
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file configured with all required keys

### Credentials Verified
- [ ] `RASA_LICENSE` is valid (not expired)
- [ ] `OPENAI_API_KEY` is valid (check at openai.com)
- [ ] `TELEGRAM_BOT_TOKEN` is valid (test with BotFather)

### Model Ready
- [ ] Rasa model trained (`rasa train`)
- [ ] Model file exists in `models/` directory
- [ ] No training warnings or errors

### Run Full Tests
```powershell
.\venv\Scripts\Activate.ps1
python -m pytest tests/ -v --tb=short
rasa data validate --domain domain/
```
- [ ] All unit tests pass
- [ ] Rasa data validation passes

---

## ⏱️ T-60 Minutes Before Demo

### Equipment Check
- [ ] Laptop fully charged or plugged in
- [ ] Internet connection stable and tested
- [ ] Backup phone ready if needed for Telegram

### Terminal Setup
Open 3 PowerShell terminals:

**Terminal 1 - Action Server:**
```powershell
cd "C:\path\to\AcademicAdvisor-Chatbot-V3"
.\venv\Scripts\Activate.ps1
rasa run actions --port 5055
```
✅ Should show: "Action endpoint is up and running"

**Terminal 2 - Rasa Server:**
```powershell
cd "C:\path\to\AcademicAdvisor-Chatbot-V3"
.\venv\Scripts\Activate.ps1
rasa run --enable-api --cors "*" --port 5005 --endpoints endpoints.local.yml --credentials credentials.local.yml
```
✅ Should show: "Rasa server is up and running"

**Terminal 3 - ngrok:**
```powershell
ngrok http 5005
```
✅ Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

---

## ⏱️ T-30 Minutes Before Demo

### Telegram Webhook Setup
1. Update `credentials.local.yml` with ngrok URL
2. Set webhook:
```
https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook?url=<NGROK_URL>/webhooks/telegram/webhook
```
3. Verify webhook:
```
https://api.telegram.org/bot<YOUR_TOKEN>/getWebhookInfo
```
- [ ] Webhook URL matches ngrok URL
- [ ] `last_error_date` is empty or old

### Quick Smoke Test
Send these messages to your Telegram bot:
1. "hello" → Should get greeting
2. "Tell me about CCS3101" → Should get course info
3. "What are the prerequisites for CSC4600?" → Should list prerequisites
4. "How to defer?" → Should get deferment info
5. "Thank you" → Should get polite response

- [ ] All 5 messages responded correctly

---

## 🎯 Demo Flow Scenarios

### Scenario 1: Happy Path (Recommended for Demo)
```
User: Hello
Bot: [Greeting + How can I help?]

User: Tell me about CCS3101
Bot: [Course details]

User: What are the prerequisites?
Bot: [Prerequisite list]

User: Thank you
Bot: [Polite closing]
```

### Scenario 2: Policy Question
```
User: How do I apply for deferment?
Bot: [Deferment policy info]

User: What is the deadline?
Bot: [Timing info/warning]
```

### Scenario 3: Graduation Check
```
User: What do I need to graduate?
Bot: [Graduation requirements]

User: How many credits do I need?
Bot: [Credit info - at least 120]
```

---

## 🚨 Emergency Recovery Procedures

### Bot Not Responding
1. Check ngrok terminal - is it still running?
2. Check action server terminal - any errors?
3. Check Rasa server terminal - any errors?
4. Restart ngrok → Update webhook URL → Try again

### "Connection Error" Message
1. Verify internet connection
2. Check if ngrok session expired (free tier = 2 hours)
3. Restart all services in order: Action → Rasa → ngrok → Webhook

### Slow Responses (>10 seconds)
1. OpenAI might be slow - this is normal occasionally
2. Have backup talking points ready while waiting
3. If persistent, check OpenAI status at status.openai.com

### Webhook Error
1. Re-run setWebhook API call with correct ngrok URL
2. Verify no typos in bot token
3. Check ngrok terminal for incoming requests

---

## 📝 Quick Reference

| Service | Port | Start Command |
|---------|------|---------------|
| Action Server | 5055 | `rasa run actions --port 5055` |
| Rasa Server | 5005 | `rasa run --enable-api --cors "*" --port 5005` |
| ngrok | - | `ngrok http 5005` |

### Important URLs
- Telegram API: `https://api.telegram.org/bot<TOKEN>/`
- Webhook Info: `getWebhookInfo`
- Set Webhook: `setWebhook?url=<URL>/webhooks/telegram/webhook`
- OpenAI Status: `status.openai.com`

---

## ✅ Final Sign-Off

**Complete this section 5 minutes before demo:**

- [ ] All 3 terminals running without errors
- [ ] Telegram bot responds to "hello"
- [ ] Course lookup works (tested with real course code)
- [ ] Backup phone ready
- [ ] Demo scenarios rehearsed

**🎉 You're ready for your FYP demonstration!**
