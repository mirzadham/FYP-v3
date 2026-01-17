Role: You are a Senior Machine Learning Engineer and Rasa Pro Specialist.

Objective: Re-initialize a local development environment for an Academic Advisor Chatbot using Rasa Pro (CALM/LLM-native). We are starting fresh to resolve dependency/configuration issues, but we MUST preserve and integrate existing assets.

The Tech Stack:

Framework: Rasa Pro (latest version).

LLM Provider: OpenAI.

Database: SQLite (Local file).

Frontend: Telegram Bot.

Existing Assets (Strictly Preserved):

/db folder: Contains a pre-populated SQLite database with UPM handbook data. Critical: Treat this as the source of truth. Do not overwrite or flush this data.

/data folder: Already contains flows.yml (CALM flows).

/domain folder: Contains domain definitions.

Keys: I have the OPENAI_API_KEY and RASA_LICENSE.

Task Instructions (Execute Step-by-Step):

Step 1: The Telegram "How-To" Guide

Before doing any coding, please provide a clear, step-by-step guide on how I can obtain the Telegram Bot Token and Verify string (if needed) using @BotFather.

Tell me exactly which values I need to have ready for the credentials.yml file.

Step 2: Environment & Installation

Create a fresh Python virtual environment.

Generate a requirements.txt strictly for Rasa Pro and SQLite support.

Provide the terminal command to install these dependencies.

Step 3: Configuration Generation

config.yml: Generate a clean CALM configuration.

Pipeline: Must include SingleStepLLMCommandGenerator.

Policies: Must include FlowPolicy.

Note: Do not include NLU classifiers (DIET) unless specifically needed for entity extraction in my existing flows.

endpoints.yml:

Configure the tracker_store to use the SQLite database found in /db.

Important: Ensure the dialect is set to sqlite and the path points correctly to the file inside the /db folder.

credentials.yml:

Generate the template for the Telegram channel.

Generate the template for the OpenAI connection.

Use explicit placeholders (e.g., YOUR_TELEGRAM_TOKEN) so I know where to paste my keys.

Step 4: Integration Check

Instruct me on how to run a "sanity check" to ensure Rasa Pro accepts the existing flows.yml in the /data folder without syntax errors.

Provide the CLI command to set the environment variables for the License and API key.

Step 5: Run Command

Provide the exact command to start the Rasa server with debug logs enabled (--debug) so we can see the flow triggers in real-time.

Deliverable: Output the content for the 3 configuration files (config.yml, endpoints.yml, credentials.yml), the Telegram setup guide, and the necessary terminal commands.