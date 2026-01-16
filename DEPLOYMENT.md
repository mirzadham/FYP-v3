# Deployment Guide - GCP Cloud Run

This guide covers deploying the Academic Advisor Chatbot to Google Cloud Platform using Cloud Run.

## Prerequisites

1. **GCP Account** with billing enabled
2. **gcloud CLI** installed and authenticated
3. **Docker** installed locally (for testing)
4. **GitHub repository** with secrets configured

## GCP Setup (One-Time)

### 1. Enable Required APIs
```bash
gcloud services enable \
  run.googleapis.com \
  sqladmin.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com
```

### 2. Create Artifact Registry
```bash
gcloud artifacts repositories create rasa-chatbot \
  --repository-format=docker \
  --location=asia-southeast1 \
  --description="Rasa chatbot Docker images"
```

### 3. Create Cloud SQL Instance
```bash
# Create PostgreSQL instance
gcloud sql instances create rasa-db \
  --database-version=POSTGRES_14 \
  --tier=db-f1-micro \
  --region=asia-southeast1

# Create database
gcloud sql databases create rasa_tracker --instance=rasa-db

# Set a strong, randomly generated password (recommended for production)
# Generate secure password: openssl rand -base64 32
gcloud sql users set-password postgres \
  --instance=rasa-db \
  --password=YOUR_SECURE_PASSWORD
```

### 4. Create Service Account for GitHub Actions
```bash
# Create service account
gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions"

# Grant permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:github-actions@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:github-actions@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:github-actions@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/cloudsql.client"

# Create key
gcloud iam service-accounts keys create key.json \
  --iam-account=github-actions@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

## GitHub Secrets Configuration

Add these secrets to your GitHub repository (Settings → Secrets → Actions):

| Secret | Value |
|--------|-------|
| `GCP_PROJECT_ID` | Your GCP project ID |
| `GCP_SA_KEY` | Contents of `key.json` |
| `CLOUD_SQL_CONNECTION` | `PROJECT:asia-southeast1:rasa-db` |
| `DATABASE_URL` | `postgresql://postgres:PASSWORD@/rasa_tracker?host=/cloudsql/PROJECT:asia-southeast1:rasa-db` |
| `RASA_PRO_LICENSE` | Your Rasa Pro license |
| `OPENAI_API_KEY` | Your OpenAI API key |
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token |

## Local Development

```bash
# Start services locally
docker-compose up --build

# Test the bot
curl -X POST http://localhost:5005/webhooks/rest/webhook \
  -H "Content-Type: application/json" \
  -d '{"sender": "test", "message": "hi"}'
```

## Deployment

Deployment is automatic via GitHub Actions:

1. Push to `feature/*` branch → Runs tests
2. Merge to `main` → Builds images and deploys to Cloud Run

### Manual Deployment
```bash
# Trigger deployment manually
gh workflow run deploy.yml
```

## Post-Deployment

### Set Telegram Webhook
After deployment, get your Cloud Run URL and set the webhook:

```bash
curl "https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook?url=https://rasa-server-xxxxx-xx.a.run.app/webhooks/telegram/webhook"
```

## Monitoring

- **Cloud Run Console**: https://console.cloud.google.com/run
- **Logs**: `gcloud run logs tail rasa-server --region=asia-southeast1`
- **Cloud SQL**: https://console.cloud.google.com/sql

## Architecture Notes

### Service Communication
The action server is deployed with `--ingress=internal` to restrict access to Cloud Run services within the same project and region. This prevents direct external access while allowing the Rasa server to communicate with it using the standard Cloud Run URL. No VPC connector is required for Cloud Run-to-Cloud Run communication in the same region.

## Estimated Costs

| Resource | Monthly Cost |
|----------|--------------|
| Cloud SQL (db-f1-micro) | ~RM35 |
| Cloud Run (Rasa, min=1) | ~RM40 |
| Cloud Run (Actions) | ~RM15 |
| **Total** | **~RM90** |
