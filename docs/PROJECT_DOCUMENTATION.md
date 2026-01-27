# NeuralFlow Project Documentation

## 1. Project Overview
**NeuralFlow** is an AI-powered medical triage and health management assistant. It operates as an intelligent first-line support system using a **ReAct (Reasoning + Acting)** framework to interview patients, analyze symptoms, and provide structured insights.

> **Disclaimer**: NeuralFlow is a demonstration tool and NOT a medical device.

## 2. Architecture & Workflow

The application follows a standard **Client-Server** architecture:

### **Frontend (Client)**
- **Tech**: React, Vite, Tailwind CSS.
- **Role**: Handles user interaction, displays medical chat, visualizations for vitals, and prescription management.
- **Flow**: User inputs text -> Frontend sends API request -> API responds (streaming) -> Frontend renders response.

### **Backend (Server)**
- **Tech**: Python (FastAPI), LangChain context (custom impl), Groq LLM (for fast inference).
- **Role**: Manages authentication, orchestrates the AI agents, maintains session state (SQL database), and executes business logic.

### **High-Level Data Flow**
1. **User Message**: Enters via `/chat/message` endpoint.
2. **Session Manager**: Loads user history and context.
3. **Medical Agent (ReAct)**:
    - Analyzes input.
    - Extracts/Saves Vitals (if any).
    - Detects Symptom Codes (normalized).
    - **Think**: Decides if it needs to Search Web, Ask Question, or Answer.
    - **Act**: Executes tool (Search, Save Vital, etc.).
    - **Observe**: Gets result.
    - **Loop**: Repeats until `Final_Answer` is reached.
4. **Response**: Streamed back to the frontend.

## 3. Core Functionality

### A. Intelligent Medical Chat
- **ReAct Loop**: The `MedicalReActAgent` doesn't just answer; it "thinks" about the user's symptoms, checks history, and determines the best course of action.
- **Symptom Extraction**: Automatically parses free text (e.g., "my head hurts a lot") into structured data (e.g., `{"code": "pain.head", "severity": "high"}`) using the `detect_symptom_codes` method.
- **Context Awareness**: The LLM prompt includes:
    - Recent conversation history.
    - Recently recorded vitals.
    - Historical symptom trends (recurring issues, worsening patterns).

### B. Vitals Management
- **Extraction**: The system uses LLM-based extraction to find vitals in chat messages (e.g., "BP is 120/80").
- **Storage**: Vitals are stored in the `vitals` table via `SessionManager`.
- **Visualization**: Frontend likely graphs these (implied by "Trend Awareness" features).

### C. Presetcriptions & Reminders
- **Management**: Users can add prescriptions with dosage and frequency.
- **Scheduling**: The `ReminderScheduler` (in services) handles logic for when to remind users (functionality appears backend-focused for now, possibly served via API).

### D. Authentication
- **Dual Support**: 
    - Traditional Username/Password.
    - Google OAuth (via `Authlib`).
- **Session**: Uses JWT (JSON Web Tokens) for stateless authentication after login.

## 4. Codebase Structure

### `src/` (Backend)
| Path | Description |
| :--- | :--- |
| **`api.py`** | **Entry Point**. Defines all FastAPI endpoints (`/chat`, `/auth`, `/vitals`). Connects components together. |
| **`agents/`** | Contains AI logic. |
| &nbsp; `medical_agent.py` | Contains `MedicalReActAgent` class. Implements the ReAct loop, prompt management, and tool execution. |
| &nbsp; `medical_prompt.py` | Stores the system prompts for the LLM. |
| **`core/`** | Core infrastructure. |
| &nbsp; `session_manager.py` | **Critical**. Wrapper around the DB. Handles User Switching, History loading, and Context building. |
| &nbsp; `brain.py` | Likely handles RAG / Vector DB interaction (referenced in imports). |
| **`services/`** | External integrations. |
| &nbsp; `llm_groq.py` | Wrapper for Groq API interactions. |
| &nbsp; `database.py` | Raw SQL / ORM interactions with SQLite. |
| &nbsp; `search_tool.py` | Web search capability (DuckDuckGo or similar). |

### `frontend/` (Frontend)
| Path | Description |
| :--- | :--- |
| `src/App.jsx` | Main Router and layout definition. |
| `src/pages/` | `Chat.jsx` (Main interface), `Login.jsx`, `Prescriptions.jsx`. |
| `src/components/` | Reusable UI elements (e.g., `DynamicBackground`). |

## 5. Key Classes & Methods

### `class MedicalReActAgent` (`src/agents/medical_agent.py`)
- **`run(user_input, history, session_manager)`**: The main driver.
    - **Step 1**: Calls `auto_extract_and_save_vitals`.
    - **Step 2**: Calls `detect_symptom_codes` to normalize symptoms.
    - **Step 3**: Builds `context_text` from history + vitals + trends.
    - **Step 4**: Enters `for` loop (max_steps=5) sending Prompt to LLM.
    - **Step 5**: Parses `Action:` from LLM response.
    - **Step 6**: Executes Action (`Search_Web`, `Save_Vital`, `Final_Answer`).

### `class SessionManager` (`src/core/session_manager.py`)
- **`set_user(user_id)`**: Switches context to a specific user.
- **`ensure_session()`**: Makes sure the user has an active conversation ID, creating one if needed.
- **`get_symptom_trends(days)`**: Aggregates SQL data to find worsening or recurring symptoms to feed into the AI context.

## 6. How to Run
1. **Backend**:
   ```bash
   cd simple_chatbot
   python -m src.api
   ```
   Runs on `http://localhost:8000`.

2. **Frontend**:
   ```bash
   cd frontend
   npm run dev
   ```
   Runs on `http://localhost:5173`.
