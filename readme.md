🏥 NeuralFlow Medical Assistant

NeuralFlow is an AI-powered medical triage and health-management assistant designed to act as an intelligent first-line support system.
It leverages a ReAct (Reasoning + Acting) framework to analyze symptoms, ask clinically relevant follow-up questions, and provide structured, explainable insights.

⚠️ Important: NeuralFlow is not a medical device and does not provide medical diagnoses. It is intended for informational and triage support only.

✨ Features
🧠 Intelligent Medical Reasoning

ReAct Clinical Engine
Applies step-by-step reasoning to evaluate symptom clusters and possible differentials.

Dynamic Symptom Interviewing
Automatically asks clarifying questions when key clinical information is missing.

Structured Responses
Outputs are organized into:

Possible Causes

Severity Assessment

Recommended Actions

🚨 Red Flags

💊 Health Management

Medication Tracking
Track active prescriptions, dosages, and schedules.

Vitals Logging
Extracts and stores vitals such as Heart Rate, Blood Pressure, and SpO₂ from conversations.

Smart Reminders
Supports medication adherence through scheduled reminders.

💾 Long-Term Context & Memory

Retrieval-Augmented Generation (RAG)
Uses a vector database to retain medical history and prior interactions.

Trend Awareness
Enables detection of recurring or worsening symptom patterns over time.

🎨 User Interface

Modern UI (“Viral Health” Theme)
Glassmorphism-inspired components and dynamic gradients.

Responsive Design
Optimized for desktop and mobile.

Smooth Animations
Powered by Framer Motion.

🛠️ Tech Stack
Backend

Python 3.11+

FastAPI – High-performance async API

LangChain – Agent orchestration and ReAct loop

Groq LLM – Low-latency inference

ChromaDB – Local vector database for RAG

Authlib – OAuth authentication (Google)

Frontend

React + Vite

Tailwind CSS

Framer Motion

Lucide React

🚀 Getting Started
Prerequisites

Python 3.11 or newer

Node.js 18 or newer

A local chroma/ directory will be created automatically

Backend Setup
# Clone the repository
git clone <your-repo-url>
cd simple_chatbot

# Create and activate a virtual environment (recommended)
python -m venv venv

# Windows
.\venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
# or (if using Poetry)
poetry install

# Run the API server
python -m src.api


Backend runs at:
http://localhost:8000

Frontend Setup
cd frontend
npm install
npm run dev


Frontend runs at:
http://localhost:5173

🔑 Environment Variables

Create a .env file in the project root.
Never commit this file to GitHub.

# AI Provider
GROQ_API_KEY=your_groq_api_key_here

# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback

# JWT Configuration
JWT_SECRET_KEY=change_this_to_a_secure_random_value
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24


📌 Security Notes

Add .env to .gitignore

Rotate keys if they are ever exposed

Use environment variables in production (Docker, CI/CD, or cloud secrets)

🧪 Testing

The project includes automated tests covering core workflows and deployment sanity checks.

python -m pytest tests/test_deployment.py

⚠️ Medical Disclaimer

NeuralFlow is not a doctor or a medical professional.
It does not provide diagnoses or treatment plans.

Information is provided for educational and triage purposes only

Always consult a licensed healthcare provider for medical advice

If you experience emergency symptoms (e.g., chest pain, difficulty breathing, severe bleeding), contact emergency services immediately

Make a Docker-ready README

Just tell me how you plan to use this repo.
