# AI-First Healthcare CRM (HCP Interaction Module) — Complete Technical Submission

[![React 19](https://img.shields.io/badge/React-19.0-61DAFB?style=for-the-badge&logo=react)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-State_Machine-8B5CF6?style=for-the-badge)](https://langchain-ai.github.io/langgraph/)
[![Groq LLM](https://img.shields.io/badge/Groq-gemma2--9b--it-F55036?style=for-the-badge)](https://groq.com/)
[![Supabase PostgreSQL](https://img.shields.io/badge/Supabase-PostgreSQL_3NF-3ECF8E?style=for-the-badge&logo=supabase)](https://supabase.com/)

An AI-First Healthcare CRM application specifically designed for **Medical Representatives (Field Agents)** in the life sciences and pharmaceutical industry to log interactions with **Healthcare Professionals (HCPs)** using conversational natural language.

---

## 📋 Table of Contents
1. [Project Overview & Core Philosophy](#1-project-overview--core-philosophy)
2. [System Architecture & Split Layout Design](#2-system-architecture--split-layout-design)
3. [LangGraph State Machine Workflow & 5 Mandatory Tools](#3-langgraph-state-machine-workflow--5-mandatory-tools)
4. [Normalized Supabase PostgreSQL Schema (3NF)](#4-normalized-supabase-postgresql-schema-3nf)
5. [Complete Directory Structure](#5-complete-directory-structure)
6. [Step-by-Step Installation & Setup Guide](#6-step-by-step-installation--setup-guide)
   - [Supabase Setup](#a-supabase-setup)
   - [Groq Setup](#b-groq-setup)
   - [Backend Execution (FastAPI)](#c-backend-execution-fastapi)
   - [Frontend Execution (React 19 + Vite)](#d-frontend-execution-react-19--vite)
7. [REST API Documentation](#7-rest-api-documentation)
8. [Requirement Traceability Matrix (RTM Audit)](#8-requirement-traceability-matrix-rtm-audit)
9. [Interview Video Recording Guide (10–15 Minutes Walkthrough)](#9-interview-video-recording-guide-1015-minutes-walkthrough)

---

## 1. Project Overview & Core Philosophy

### The Clinical Sales Challenge
In traditional CRM systems, Medical Representatives spend hours typing repetitive data into dozens of form fields after meeting doctors (`HCP Name`, `Interaction Type`, `Date`, `Time`, `Attendees`, `Topics Discussed`, `Materials Shared`, `Samples Distributed`, `Observed Sentiment`, `Outcomes`, `Follow-up Actions`). This manual friction leads to delayed logs, inaccurate data, and loss of valuable clinical insights.

### Our AI-First Solution
This module reinvents HCP interaction logging by introducing two core design principles:
1. **100% Read-Only Structured Form (`pointer-events: none`)**: The structured form on the left pane displays all 12 interaction fields clearly. However, users **never manually type or edit directly into the form fields**.
2. **Conversational AI Assistant Control**: A conversational AI chat on the right pane controls the entire form lifecycle. Users speak naturally (*"I met Dr Sharma at Apollo Hospital today morning. Discussed CardioPlus clinical trials and gave 15 trial samples..."*). The LangGraph agent extracts exact clinical entities, generates a professional summary, synchronizes the UI form in real time via Redux Toolkit, requests user confirmation, and persists validated records directly into **Supabase PostgreSQL**.

---

## 2. System Architecture & Split Layout Design

```
+----------------------------------------------------------------------------------------------------+
|                                    REACT 19 + VITE FRONTEND (PORT 5173)                            |
|                                                                                                    |
|  +--------------------------------------------+    +--------------------------------------------+  |
|  |     LEFT PANE: Read-Only Interaction Form  |    |     RIGHT PANE: AI Assistant Chat          |  |
|  |                                            |    |                                            |  |
|  |  [🔒 Read-Only Mode (AI Controlled)]       |    |  • Natural Language Input Box              |  |
|  |  • HCP Name & Hospital                     |    |  • 3 Quick-Click Example Prompt Pills      |  |
|  |  • Date, Time & Attendees                  |    |  • Live LangGraph Tool Execution Badge     |  |
|  |  • Topics Discussed & Materials Shared     |    |  • Animated Typing Dots                    |  |
|  |  • Samples Distributed (Quantity/Product)  |    |  • [✅ Confirm & Save to Supabase Banner]  |  |
|  |  • Observed Sentiment & Outcomes           |    |                                            |  |
|  |  • Follow-up Actions & AI Summary          |    |                                            |  |
|  +--------------------------------------------+    +--------------------------------------------+  |
|                        ^                                                 |                         |
|                        | (State Sync)                                    | (Axios REST /chat)      |
|                        v                                                 v                         |
|                 [ Redux Toolkit Store: chat | interaction | hcp | toolExecution ]                |
+----------------------------------------------------------------------------------------------------+
                                                                           |
                                                                           v (HTTP POST)
+----------------------------------------------------------------------------------------------------+
|                                      FASTAPI BACKEND (PORT 8000)                                   |
|                                                                                                    |
|  +----------------------------------------------------------------------------------------------+  |
|  | REST Endpoints: /chat | /interaction (CRUD) | /hcp (Search) | /history/{id} (Analytics)       |  |
|  +----------------------------------------------------------------------------------------------+  |
|                                                  |                                                 |
|                                                  v                                                 |
|  +----------------------------------------------------------------------------------------------+  |
|  |                       LANGGRAPH STATE MACHINE (`AgentState`)                                 |  |
|  |                                                                                              |  |
|  |   [User Message + Current Form State] ---> [ Router Node (Groq gemma2-9b-it) ]               |  |
|  |                                                  |                                           |  |
|  |        +---------------------+-------------------+-------------------+                       |  |
|  |        |                     |                   |                   |                       |  |
|  |        v                     v                   v                   v                       |  |
|  |  (log_interaction)   (edit_interaction)    (search_hcp)        (hcp_history)                 |  |
|  |        |                     |                   |                   |                       |  |
|  |        +---------------------+-------------------+-------------------+                       |  |
|  |                                                  |                                           |  |
|  |                                                  v                                           |  |
|  |                                          (save_interaction)                                  |  |
|  |                                                  |                                           |  |
|  |                                                  v                                           |  |
|  |                          [ Returns Updated Form JSON & Tool Diagnostic Badge ]               |  |
|  +----------------------------------------------------------------------------------------------+  |
+----------------------------------------------------------------------------------------------------+
                                                  |
                                                  v (SQLAlchemy ORM + Alembic)
+----------------------------------------------------------------------------------------------------+
|                                    SUPABASE POSTGRESQL DATABASE                                    |
|                                                                                                    |
|  Tables: hcp | interaction | follow_up | audit_log | chat_history                               |
+----------------------------------------------------------------------------------------------------+
```

---

## 3. LangGraph State Machine Workflow & 5 Mandatory Tools

Our backend avoids brittle regex and generic mock loops by leveraging a deterministic **LangGraph State Machine (`AgentState`)**.

### Agent State Schema (`backend/app/ai/state.py`)
```python
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    current_form_data: Dict[str, Any]
    active_hcp_id: Optional[int]
    executed_tool: Optional[str]
    tool_input: Optional[Dict[str, Any]]
    tool_output: Optional[Dict[str, Any]]
    needs_confirmation: bool
    saved_interaction_id: Optional[int]
```

### The 5 Mandatory LangGraph Tools
1. **`log_interaction` (`backend/app/ai/tools/log_interaction.py`)**:
   - **Trigger**: When the user reports a clinical meeting narrative.
   - **Action**: Extracts `Doctor Name`, `Hospital`, `Interaction Date`, `Time`, `Attendees`, `Products Discussed`, `Materials Shared`, `Samples Distributed`, `Sentiment`, `Outcomes`, and `Follow-up Actions`. Auto-matches existing HCP profiles from the database and synthesizes a professional executive summary.
2. **`edit_interaction` (`backend/app/ai/tools/edit_interaction.py`)**:
   - **Trigger**: When the user asks to modify specific values (*"Change sentiment to Negative"*, *"Make samples 20 boxes"*).
   - **Action**: Updates **only requested fields without overwriting unchanged values** and re-generates the summary if necessary.
3. **`search_hcp` (`backend/app/ai/tools/search_hcp.py`)**:
   - **Trigger**: When the user searches for a doctor or hospital profile.
   - **Action**: Queries the `hcp` table using `ILIKE`, returns doctor profile details (`specialty`, `email`, `phone`), and lists their 3 most recent historical meetings.
4. **`hcp_history` (`backend/app/ai/tools/hcp_history.py`)**:
   - **Trigger**: When the user queries past interactions or analytics.
   - **Action**: Returns past meetings, frequently discussed pharmaceutical products (`CardioPlus`, `OncoBoost`, `GlucoFix`), and computes **Sentiment Trend Distribution (`Positive`, `Neutral`, `Negative`)**.
5. **`save_interaction` (`backend/app/ai/tools/save_interaction.py`)**:
   - **Trigger**: When the user explicitly confirms submission (*"Yes, save it"*).
   - **Action**: Validates mandatory fields, commits records to `interaction` and `follow_up` tables in Supabase, and writes an immutable record to `audit_log`.

---

## 4. Normalized Supabase PostgreSQL Schema (3NF)

The database (`database.sql`) contains 5 fully normalized tables linked with indexed foreign keys (`ON DELETE CASCADE`):

1. **`hcp`**: `id` (PK), `name`, `specialty`, `hospital`, `contact_email`, `phone`, `city`, `created_at`, `updated_at`.
2. **`interaction`**: `id` (PK), `hcp_id` (FK -> `hcp.id`), `interaction_type`, `interaction_date`, `interaction_time`, `attendees`, `topics_discussed`, `materials_shared`, `samples_distributed`, `observed_sentiment` (`Positive/Neutral/Negative`), `outcomes`, `ai_summary`, `status` (`Draft/Confirmed/Saved`).
3. **`follow_up`**: `id` (PK), `interaction_id` (FK -> `interaction.id`), `hcp_id` (FK -> `hcp.id`), `action_description`, `due_date`, `status`.
4. **`audit_log`**: `id` (PK), `entity_type`, `entity_id`, `action` (`AI_SAVE`, `UPDATE`, `DELETE`), `changes` (JSON diff), `timestamp`.
5. **`chat_history`**: `id` (PK), `session_id`, `sender` (`user/ai/system`), `message`, `tool_called`, `created_at`.

---

## 5. Complete Directory Structure

```
ai-crm-hcp/
├── database.sql                      # Complete Supabase DDL + Realistic Seed Data
├── README.md                         # This comprehensive specification
├── .env.example                      # Root environment variable template
├── backend/                          # Python FastAPI + LangGraph Backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI initialization & CORS
│   │   ├── database.py               # SQLAlchemy async/sync engine & session generator
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── schema.py             # SQLAlchemy ORM models (5 tables)
│   │   │   └── pydantic_schemas.py     # Request/Response validation schemas
│   │   ├── ai/                       # LangGraph AI State Machine Engine
│   │   │   ├── __init__.py
│   │   │   ├── state.py              # AgentState TypedDict
│   │   │   ├── agent.py              # StateGraph compiled graph (`crm_graph`)
│   │   │   ├── prompts.py            # Groq gemma2-9b-it prompts & router
│   │   │   └── tools/                # Specialized LangGraph Tools
│   │   │       ├── __init__.py
│   │   │       ├── log_interaction.py  # Tool 1: Entity extraction & summary
│   │   │       ├── edit_interaction.py # Tool 2: Field modification without overwrites
│   │   │       ├── search_hcp.py       # Tool 3: HCP search & recent logs
│   │   │       ├── hcp_history.py      # Tool 4: Meeting timeline & sentiment trends
│   │   │       └── save_interaction.py # Tool 5: Supabase commit & audit log
│   │   └── routers/
│   │       ├── __init__.py
│   │       ├── chat.py               # POST /chat (Primary AI Endpoint)
│   │       ├── interaction.py        # CRUD /interaction REST Endpoints
│   │       └── hcp.py                # GET /hcp, /hcp/{id}, /history/{id}
│   ├── alembic/                      # Database migration scaffolding
│   ├── alembic.ini                   # Alembic configuration
│   ├── requirements.txt              # Python dependencies
│   └── test_integration.py           # E2E Automated Verification Script
└── frontend/                         # React 19 + Vite + Redux Toolkit Frontend
    ├── package.json
    ├── vite.config.ts
    ├── tsconfig.json
    ├── index.html
    └── src/
        ├── main.tsx
        ├── App.tsx                   # Root component with Toast & Router
        ├── styles/
        │   └── theme.css             # Premium Dark/Light UI tokens & Read-only form rules
        ├── services/
        │   └── api.ts                # Axios HTTP client
        ├── store/                    # Redux Toolkit State Store
        │   ├── index.ts
        │   ├── chatSlice.ts          # Chat messages & typing states
        │   ├── interactionSlice.ts   # Live form sync reducer
        │   ├── hcpSlice.ts
        │   ├── toolExecutionSlice.ts # Live tool diagnostic badge reducer
        │   └── notificationSlice.ts
        └── components/
            ├── Header/Header.tsx     # Navigation & Dark/Light mode switcher
            ├── Dashboard/DashboardLayout.tsx # Responsive 50/50 split layout
            ├── Form/InteractionForm.tsx      # Read-only structured form with 12 fields
            └── Chat/
                ├── ChatWindow.tsx            # Conversational AI interface with quick pills
                └── ToolExecutionBadge.tsx    # Live LangGraph tool status indicator
```

---

## 6. Step-by-Step Installation & Setup Guide

### A. Supabase Setup
1. Create a free project at [Supabase](https://supabase.com/).
2. Navigate to **SQL Editor** -> **New Query**.
3. Copy the entire content of `database.sql` and click **Run**.
4. This creates all 5 tables (`hcp`, `interaction`, `follow_up`, `audit_log`, `chat_history`), foreign keys, indexes, and populates realistic seed doctors (`Dr. Rakesh Sharma` at Apollo Hospital, `Dr. Anjali Gupta` at AIIMS, etc.).
5. Go to **Project Settings -> Database** and copy your `URI` / `Connection string`.

### B. Groq Setup
1. Create a free API token at [Groq Console](https://console.groq.com/docs/models).
2. The default model used across all prompts is mandatory **`gemma2-9b-it`**.

### C. Backend Execution (FastAPI)
Open your terminal and navigate to the `backend/` directory:
```bash
cd backend

# Create virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```
Create a `.env` file inside `backend/` based on `backend/.env.example`:
```env
DATABASE_URL=postgresql+psycopg2://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT].supabase.co:5432/postgres
GROQ_API_KEY=your_groq_api_key_here
PORT=8000
```
Run the automated end-to-end verification script to ensure everything works cleanly:
```bash
python test_integration.py
```
Start the FastAPI server:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
API Documentation will be live at `http://localhost:8000/docs`.

### D. Frontend Execution (React 19 + Vite)
Open a second terminal window and navigate to `frontend/`:
```bash
cd frontend

# Install Node dependencies
npm install

# Start Vite dev server
npm run dev
```
Open your browser at `http://localhost:5173` to explore the application!

---

## 7. REST API Documentation

| HTTP Method | Endpoint | Description | Payload / Response |
| :--- | :--- | :--- | :--- |
| `POST` | `/chat` | Primary conversational AI assistant endpoint executing LangGraph workflow | Body: `{ session_id, message, current_form_data }` -> Returns `ChatResponse` |
| `POST` | `/interaction` | Create new interaction directly (with `AuditLog` entry) | Body: `InteractionCreate` schema |
| `GET` | `/interaction` | List all logged interactions (Supports `?hcp_id=` & `?status=` filters) | Returns `List[InteractionResponse]` |
| `GET` | `/interaction/{id}` | Retrieve specific interaction details by ID | Returns `InteractionResponse` |
| `PUT` | `/interaction/{id}` | Update specific fields without overwriting unchanged values | Body: `InteractionUpdate` schema |
| `DELETE` | `/interaction/{id}` | Delete interaction and record deletion event in `AuditLog` | Returns `204 No Content` |
| `GET` | `/hcp` | List or search all Healthcare Professionals (`?search=Sharma`) | Returns `List[HCPResponse]` |
| `GET` | `/hcp/{id}` | Retrieve doctor profile by ID | Returns `HCPResponse` |
| `GET` | `/history/{id}` | Retrieve comprehensive meeting timeline & **Sentiment Distribution** | Returns `Dict` with meetings & sentiment trends |

---

## 8. Requirement Traceability Matrix (RTM Audit)

| Req ID | Requirement Description | Verification Destination | Status |
| :--- | :--- | :--- | :--- |
| **REQ-01** | React 19, Vite, Redux Toolkit, React Router, Axios, React Hook Form, Google Inter Font | `frontend/package.json`, `index.html` | ✅ Fully Implemented |
| **REQ-02** | Python, FastAPI, SQLAlchemy ORM, Pydantic, Alembic | `backend/requirements.txt`, `backend/alembic/env.py`, `main.py` | ✅ Fully Implemented |
| **REQ-03** | LangGraph State Machine with Groq API (`gemma2-9b-it`) | `backend/app/ai/agent.py`, `backend/app/ai/prompts.py` | ✅ Fully Implemented |
| **REQ-04** | Supabase PostgreSQL normalized tables & environment setup | `database.sql`, `backend/app/database.py`, `schema.py` | ✅ Fully Implemented |
| **REQ-05** | Read-Only Form & Live AI Sync (`pointer-events: none`) | `InteractionForm.tsx`, `theme.css` | ✅ Fully Implemented |
| **REQ-06** | AI Assistant Chat Interface (Typing dots, split screen) | `ChatWindow.tsx`, `DashboardLayout.tsx` | ✅ Fully Implemented |
| **REQ-07** | LangGraph Tool 1 (`Log Interaction`) | `backend/app/ai/tools/log_interaction.py` | ✅ Fully Implemented |
| **REQ-08** | LangGraph Tool 2 (`Edit Interaction`) | `backend/app/ai/tools/edit_interaction.py` | ✅ Fully Implemented |
| **REQ-09** | LangGraph Tool 3 (`Search HCP`) | `backend/app/ai/tools/search_hcp.py` | ✅ Fully Implemented |
| **REQ-10** | LangGraph Tool 4 (`HCP History`) | `backend/app/ai/tools/hcp_history.py` | ✅ Fully Implemented |
| **REQ-11** | LangGraph Tool 5 (`Save Interaction`) | `backend/app/ai/tools/save_interaction.py` | ✅ Fully Implemented |
| **REQ-12** | Backend API CRUD & `/chat` Endpoints | `backend/app/routers/*.py` | ✅ Fully Implemented |
| **REQ-13** | Redux Store (`chat`, `interaction`, `hcp`, `toolExecution`) | `frontend/src/store/*.ts` | ✅ Fully Implemented |
| **REQ-14** | Dark & Light Mode high-contrast CRM theme | `theme.css`, `Header.tsx` | ✅ Fully Implemented |

---

## 9. Interview Video Recording Guide (10–15 Minutes Walkthrough)

When recording your video submission (`Instructions(Task 1).mp4`), structure your presentation as follows:

1. **Introduction & Architecture Overview (2 Mins)**:
   - Introduce the goal: Solving clinical sales reporting friction for Medical Representatives.
   - Explain the split layout: Show the Left Read-Only Form (`pointer-events: none`) and Right AI Chat.
2. **Demo Tool 1 (`log_interaction`) & Tool 5 (`save_interaction`) (4 Mins)**:
   - Click the quick example pill or type: *"I met Dr Sharma at Apollo Hospital today morning. Discussed CardioPlus clinical trials and shared the clinical monograph brochure. Gave 15 samples of CardioPlus 50mg. Doctor was positive. Schedule follow up next Tuesday."*
   - Point out the **Tool Execution Badge (`log_interaction()`)** appearing live.
   - Show how all 12 read-only form fields populated instantaneously without manual typing!
   - Click the **Confirm & Save** button to execute `save_interaction()` and show the success toast.
3. **Demo Tool 2 (`edit_interaction`) (2 Mins)**:
   - Type: *"Change the observed sentiment to Negative and update the samples distributed to 25 starter kits."*
   - Show that only those two fields updated while doctor name and date remained untouched (`Never overwrite unchanged values`).
4. **Demo Tool 3 (`search_hcp`) & Tool 4 (`hcp_history`) (3 Mins)**:
   - Type: *"Search for Dr. Anjali Gupta at AIIMS"* -> Show profile card returned.
   - Type: *"Show history and sentiment trend for Dr. Rakesh Sharma"* -> Point out the **Sentiment Distribution (`Positive/Neutral/Negative`)** and frequently discussed products (`CardioPlus`).
5. **Code Explanation & Key Takeaways (3 Mins)**:
   - Briefly show `backend/app/ai/agent.py` (LangGraph `StateGraph`) and `backend/app/ai/tools/`.
   - Show `database.sql` (Supabase 3NF schema and `AuditLog` immutability).
   - Summarize how AI-first interfaces completely eliminate CRM data entry burden.

---

*Built with passion and engineering rigor for the technical interview assignment.*
