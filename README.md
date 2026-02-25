# UPM Academic Advisor Chatbot

A Telegram-based chatbot that helps Universiti Putra Malaysia (UPM) students navigate academic policies, course information, and university procedures. Built with Rasa Pro's CALM (Conversational AI with Language Models) architecture and backed by a Retrieval-Augmented Generation (RAG) pipeline for answering open-ended questions from official university handbooks.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Variables](#environment-variables)
  - [Training the Model](#training-the-model)
  - [Running Locally](#running-locally)
  - [Setting Up Telegram Webhook](#setting-up-telegram-webhook)
- [Docker Deployment](#docker-deployment)
- [Knowledge Base](#knowledge-base)
- [Conversation Flows](#conversation-flows)
- [Testing](#testing)
- [Data Extraction Tools](#data-extraction-tools)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

Students at UPM often have questions about course prerequisites, graduation requirements, academic probation, industrial training eligibility, and more. The answers are scattered across multiple PDF handbooks and faculty documents, making it hard to find the right information quickly.

This chatbot consolidates that knowledge into a single conversational interface accessible through Telegram. Students can ask questions in natural language, and the bot will either walk them through a structured assessment (e.g., "Am I on academic probation?") or retrieve relevant information from the handbook using semantic search.

---

## Key Features

**Structured Academic Assessments**
- Graduation readiness check — validates total credits, outstanding requirements
- Academic probation assessment — determines probation level based on CGPA
- Convocation eligibility — checks MUET band and degree completion
- Course drop consequences — advises based on the current week of the semester
- Industrial training eligibility — checks year of study against faculty requirements
- Grade appeal readiness — validates appeal deadlines and documentation

**Course Information Lookup**
- Search courses by code (e.g., `CCS3101`, `CSC4600`)
- View credits, prerequisites, faculty, and descriptions (English & Malay)
- Prerequisite chain checking
- Fuzzy matching for course code typos

**Policy & Procedure Guidance**
- Credit transfer eligibility
- Program change requirements
- Semester deferment timing
- Full-class and timetable clash resolution
- Course repeat guidelines

**RAG-Powered Fallback**
- When a question doesn't match any predefined flow, the bot performs semantic search across three knowledge domains (courses, academic calendar, academic rules) and generates an answer using GPT-4o-mini with the relevant context

**Telegram Integration**
- Deployed as a Telegram bot for easy mobile access
- Webhook-based for real-time responses
- Supports local development via ngrok tunneling

---

## Architecture

```
┌─────────────┐     Webhook      ┌──────────────────┐
│  Telegram   │ ◄──────────────► │   Rasa Server    │
│  (User)     │                  │  (CALM + Flows)  │
└─────────────┘                  └────────┬─────────┘
                                          │
                                          ▼
                                 ┌──────────────────┐
                                 │  Action Server   │
                                 │  (Custom Logic)  │
                                 └────────┬─────────┘
                                          │
                              ┌───────────┼───────────┐
                              ▼           ▼           ▼
                     ┌──────────┐  ┌───────────┐  ┌────────┐
                     │ Handbook │  │  OpenAI   │  │ SQLite │
                     │  Store   │  │  (GPT +   │  │Tracker │
                     │(JSON +   │  │Embeddings)│  │  Store │
                     │Embeddings│  │           │  │        │
                     └──────────┘  └───────────┘  └────────┘
```

- **Rasa Server** handles NLU through the `CompactLLMCommandGenerator` pipeline, routing user messages to the appropriate conversation flow
- **Action Server** executes custom Python logic for assessments, database lookups, and RAG queries
- **HandbookStore** is a singleton that loads and caches all JSON + embedding data at startup for fast lookups
- **OpenAI** provides both the LLM (GPT-4o-mini) for command generation and response generation, and `text-embedding-3-small` for semantic search
- **SQLite** stores conversation tracker data locally (PostgreSQL for production on Railway)

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Dialogue Engine | Rasa Pro 3.10+ (CALM architecture) |
| LLM | OpenAI GPT-4o-mini |
| Embeddings | OpenAI text-embedding-3-small |
| Language | Python 3.10 |
| Action Server | Rasa SDK 3.10+ |
| Messaging | Telegram Bot API |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Deployment | Docker, Railway |
| Semantic Search | NumPy cosine similarity |

---

## Project Structure

```
AcademicAdvisor-Chatbot-V3/
│
├── actions/                     # Custom action server code
│   ├── academic/                # Course info, prerequisites, graduation, convocation, drop
│   ├── policies/                # Probation, industrial training, grade appeal, deferment
│   ├── admin/                   # Credit transfer, program change, registration issues
│   └── system/                  # HandbookStore utility, OpenAI RAG fallback
│
├── data/                        # Training data and knowledge base
│   ├── academic/                # CALM flows for academic tasks
│   ├── policies/                # CALM flows for policy-related tasks
│   ├── general/                 # Greetings, help, identity flows
│   ├── admin/                   # Registration and admin flows
│   ├── support/                 # Fallback and support flows
│   ├── handbook/                # Knowledge base (JSON + embeddings)
│   │   ├── json/                #   Structured data (courses, calendar, rules)
│   │   ├── embeddings/          #   Pre-computed vector embeddings
│   │   ├── academic_calendar/   #   Raw calendar source files
│   │   └── academic_rules/      #   Raw rules source files
│   └── system/                  # System-level flow data
│
├── domain/                      # Rasa domain definitions
│   ├── academic/                # Slots, responses, and actions for academic domain
│   ├── policies/                # Slots, responses for policy domain
│   ├── admin/                   # Admin-related domain config
│   ├── general/                 # General conversation responses
│   ├── support/                 # Support domain
│   └── system/                  # System-level domain config
│
├── tests/                       # Test suite
│   ├── academic/                # Unit tests for academic actions
│   ├── policies/                # Unit tests for policy actions
│   ├── admin/                   # Unit tests for admin actions
│   ├── system/                  # Tests for handbook utils and OpenAI actions
│   ├── integration/             # End-to-end integration tests
│   ├── e2e_test_cases.yml       # End-to-end conversation test cases
│   └── test_flows.yml           # Flow-level test cases
│
├── tools/                       # Data extraction scripts
│   ├── extract_handbook_pdf.py  # Extract course data from faculty PDF handbooks
│   ├── extract_calendar.py      # Extract academic calendar events
│   └── extract_rules.py         # Extract academic rules and policies
│
├── scripts/
│   └── run_local.ps1            # PowerShell script for local development
│
├── config.yml                   # Rasa pipeline and policy configuration
├── credentials.yml              # Channel credentials (Telegram)
├── endpoints.yml                # Action server and tracker store endpoints
├── docker-compose.yml           # Local Docker setup
├── Dockerfile                   # Rasa server container (multi-stage)
├── Dockerfile.actions           # Action server container
├── requirements.txt             # Python dependencies
└── .env.example                 # Environment variable template
```

---

## Getting Started

### Prerequisites

- Python 3.10
- A valid [Rasa Pro license](https://rasa.com/rasa-pro/)
- An [OpenAI API key](https://platform.openai.com/api-keys)
- A [Telegram Bot Token](https://core.telegram.org/bots#botfather) (for Telegram deployment)
- [ngrok](https://ngrok.com/download) (for local Telegram testing)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/AcademicAdvisor-Chatbot-V3.git
cd AcademicAdvisor-Chatbot-V3

# Create and activate a virtual environment
python -m venv venv

# Windows
.\venv\Scripts\Activate.ps1

# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Copy the example file and fill in your credentials:

```bash
cp .env.example .env
```

Required variables:

| Variable | Description |
|----------|-------------|
| `RASA_LICENSE` | Your Rasa Pro license key |
| `OPENAI_API_KEY` | OpenAI API key for GPT-4o-mini and embeddings |
| `TELEGRAM_BOT_TOKEN` | Bot token from BotFather |
| `TELEGRAM_BOT_USERNAME` | Your bot's username |

For production deployment on Railway, also set `DATABASE_URL`, `ACTION_SERVER_URL`, and `RASA_SERVER_URL`.

### Training the Model

```bash
rasa train
```

This will generate a trained model in the `models/` directory. Training requires a valid `RASA_LICENSE`.

### Running Locally

You need three terminals running simultaneously:

**Terminal 1 — Action Server:**
```bash
rasa run actions --port 5055
```

**Terminal 2 — Rasa Server:**
```bash
rasa run --enable-api --cors "*" --port 5005 --endpoints endpoints.local.yml --credentials credentials.local.yml
```

**Terminal 3 — ngrok (for Telegram):**
```bash
ngrok http 5005
```

Alternatively, use the helper script:
```powershell
.\scripts\run_local.ps1
```

### Setting Up Telegram Webhook

1. Start ngrok and copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)
2. Update `credentials.local.yml` with the ngrok URL:
   ```yaml
   telegram:
     access_token: "<your-bot-token>"
     verify: "YourBotUsername"
     webhook_url: "https://abc123.ngrok.io/webhooks/telegram/webhook"
   ```
3. Register the webhook with Telegram:
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=<NGROK_URL>/webhooks/telegram/webhook
   ```
4. Open Telegram and message your bot

---

## Docker Deployment

For containerized deployment (local or Railway):

```bash
# Build and start both services
docker compose up --build

# Rasa server will be available at localhost:5005
# Action server at localhost:5055
```

The `docker-compose.yml` spins up two services:
- **rasa** — The main Rasa server (port 5005)
- **action-server** — The custom action server (port 5055)

For Railway deployment, configure the environment variables in the Railway dashboard and push the repo. Railway will automatically build and deploy from the Dockerfiles.

---

## Knowledge Base

The chatbot's knowledge base is built from official UPM documents and organized into three domains:

| Domain | Source | Content |
|--------|--------|---------|
| **Courses** | Faculty handbook PDFs | Course codes, names (EN/MY), credits, prerequisites, descriptions |
| **Calendar** | Academic calendar documents | Semester dates, registration periods, exam schedules, holidays |
| **Rules** | Academic regulations booklet | Grading policies, probation rules, graduation requirements, appeals |

Each domain has:
- **JSON files** — Structured data extracted from source documents
- **Embedding files** (.pkl) — Pre-computed OpenAI `text-embedding-3-small` vectors for semantic search

The `HandbookStore` singleton loads all data into memory once and caches it for the lifetime of the action server process.

---

## Conversation Flows

The chatbot uses Rasa CALM flows instead of traditional intent-based stories. Each flow is a YAML file defining a multi-step conversation with slot collection, validation, branching, and action calls.

| Category | Flows |
|----------|-------|
| **Academic** | Course info lookup, prerequisite check, graduation assessment, convocation eligibility, drop course assessment, course search, academic calendar, career prospects |
| **Policies** | Probation assessment, industrial training eligibility, grade appeal, deferment, repeat policy |
| **Admin** | Credit transfer, change program, registration deadlines |
| **General** | Greetings, help menu, bot identity, thank you |
| **Support** | OpenAI RAG fallback for unhandled queries |

---

## Testing

The project includes unit tests, integration tests, and end-to-end conversation tests.

```bash
# Run all tests
pytest tests/

# Run tests for a specific module
pytest tests/academic/
pytest tests/policies/

# Run end-to-end tests
rasa test --stories tests/e2e_test_cases.yml

# Run flow tests
rasa test --stories tests/test_flows.yml
```

---

## Data Extraction Tools

The `tools/` directory contains Python scripts that extract and structure data from raw UPM documents:

| Script | Purpose |
|--------|---------|
| `extract_handbook_pdf.py` | Parses faculty handbook PDFs into structured JSON (courses, credits, prerequisites) and generates OpenAI embeddings |
| `extract_calendar.py` | Extracts academic calendar events and generates embeddings |
| `extract_rules.py` | Extracts academic rules/regulations and generates embeddings |

These scripts are run manually whenever source documents are updated. They output to `data/handbook/json/` and `data/handbook/embeddings/`.

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes and add tests
4. Run the test suite to make sure nothing is broken
5. Commit and push (`git push origin feature/your-feature`)
6. Open a pull request

---

## License

This project was developed as a Final Year Project at the Faculty of Computer Science and Information Technology, Universiti Putra Malaysia.
