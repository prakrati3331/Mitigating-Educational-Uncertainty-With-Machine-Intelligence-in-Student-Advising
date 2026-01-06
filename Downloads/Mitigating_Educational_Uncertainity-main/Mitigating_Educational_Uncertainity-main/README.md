# AI in Education (ML–Dashboard–LLM Architecture)

This repository is an end-to-end **AI Education** system built around a **Dashboard-centric ML + LLM architecture**:

- **ML modules** generate predictions/recommendations (stream selection, course recommendations, dropout risk, etc.).
- A **Dashboard data layer** (`dashboard/DashboardService` + `/api/dashboard/...`) acts as the *single source of truth* for what the user has done and what the system has predicted.
- An **LLM module** (`LLM/llm.py`) answers questions about “what’s happening in the website” by:
  1) pulling the user’s dashboard data via HTTP, and
  2) using the dashboard HTML/JS as contextual knowledge.

> Important: The project currently mixes multiple runtimes (FastAPI + several Flask micro-apps + Streamlit prototypes). The **main entrypoint for the integrated system is `main.py` (FastAPI)**.

---

## 1) Quick Start (Recommended)

### Prerequisites

- Python 3.10+ recommended
- A virtual environment (`venv`) is strongly recommended

### Environment variables

Create a `.env` in the repository root:

```env
# Required for AI career guidance inside FastAPI (`main.py`) and `training/flask_app.py`
MISTRAL_API_KEY=...

# Optional (used by `LLM/llm.py` with LangChain OpenAI-compatible endpoints)
OPENAI_API_KEY=...
OPENAI_API_BASE=...

# Optional override (LLM defaults to http://localhost:8000)
DASHBOARD_API_URL=http://localhost:8000
```

### Install

```bash
pip install -r requirements.txt
```

### Run the integrated FastAPI server

```bash
uvicorn main:app --reload --port 8000
```

This serves:
- Main HTML pages (hub pages)
- ML endpoints (stream prediction, course recommenders)
- Dashboard pages + Dashboard API (`/api/dashboard/...`)
- AI chat endpoints (`/api/mistral-chat`)

---

## 2) Architecture Overview

### 2.1 High-level data flow

1. **User interacts with website pages** (stream assessment, course recommender, quizzes, etc.).
2. **FastAPI (`main.py`)** and/or individual module endpoints compute results.
3. Results are written into **in-memory `user_data_store`** and are aggregated by **`dashboard/DashboardService`**.
4. The **Dashboard UI** (`dashboard/templates/dashboard.html`) renders aggregated data.
5. The **LLM module** (`LLM/llm.py`) fetches the dashboard data via **Dashboard API** and answers user questions.

### 2.2 Key invariants

- **Dashboard is the integration hub**: most modules either write to `user_data_store` directly or can be synchronized into it.
- **LLM answers are grounded in dashboard data**: it calls `/api/dashboard/user/{user_id}` and `/api/dashboard/activities/{user_id}` and uses dashboard HTML/JS as structural context.
- **Current persistence is in-memory**: `user_data_store` is not persisted to a database (some modules do use JSON files; Career Mapping uses MongoDB). For production you’d typically unify persistence.

---

## 3) Repository Structure (Module-by-Module)

Below is a *complete* module map of the repository.

### 3.1 Root entrypoints

- **`main.py`**
  - Primary FastAPI application.
  - Mounts static assets and templates.
  - Loads and orchestrates:
    - Stream recommender (from `training/stream_model.pkl` etc.)
    - Course recommenders (Arts/Commerce/PCM/PCB/Vocational)
    - Quiz service
    - Career mapping service
    - Dropout risk service
    - Dashboard service
    - E-books, institution directory, school directory, timeline tracker backends
  - Provides:
    - Stream prediction endpoint: `POST /predict`
    - Career insights via Mistral: `POST /get_insights`
    - AI chat (Mistral): `POST /api/mistral-chat`
    - Dashboard API endpoints: `GET /api/dashboard/user/{user_id}`, `GET /api/dashboard/activities/{user_id}`, etc.
    - Several “bridge” endpoints to store results into `user_data_store` (e.g. `POST /api/set-recommended-stream`, `POST /api/set-course-recommendations`)

- **`main1.py`**
  - Alternative FastAPI variant (appears older/simplified). Not the primary.

- **Static HTML hub pages**
  - `recommendation_hub.html`, `home.html`, `stream_selection.html`, etc.
  - These act as UI entry points linking to different parts of the system.

---

## 4) Dashboard (MOST IMPORTANT MODULE)

### Location

- `dashboard/dashboard_service.py`
- `dashboard/templates/dashboard.html`

### Purpose

The dashboard is the **central aggregation layer** that unifies user state and outputs from all ML modules.

### Key class: `DashboardService`

- Initialized in `main.py` as:
  - `user_data_store = {}` (in-memory)
  - `dashboard_service = DashboardService(user_data_store)`

### What it aggregates

- **Stream results** (recommended stream, probabilities)
- **Course recommendations** for each stream (Arts/Commerce/PCM/PCB/Vocational)
- **Career assessment** output (Career Mapping)
- **Quiz results and analytics**
- **Dropout risk assessment**
- **Engagement / activity tracking**

### Dashboard API endpoints (FastAPI)

Defined in `main.py` (names may evolve; verify in the file):

- `GET /api/dashboard/user/{user_id}`
  - Returns full aggregated dashboard JSON for a user
- `GET /api/dashboard/activities/{user_id}?limit=20`
  - Returns recent activity feed
- `POST /api/dashboard/activity`
  - Track an activity event
- `GET /api/dashboard/stats/{user_id}`
  - User stats (completion, achievements, etc.)
- Additional helper endpoints also exist, e.g. quiz/career/dropout sync endpoints under `/api/dashboard/...`

### Dashboard UI

- `dashboard/templates/dashboard.html` is the main UI.
- The LLM module reads this HTML and extracts inline JS to understand dashboard structure.

---

## 5) LLM Module (MOST IMPORTANT MODULE)

### Location

- `LLM/llm.py`

### Purpose

Provides a **dashboard-aware assistant** that can answer questions like:
- “What are my recent activities?”
- “How did I do on my last quiz?”
- “What stream did you recommend and why?”
- “What course recommendations do I have?”

### How it works

- **Dashboard API client**: `DashboardAPIClient`
  - Calls (default base): `http://localhost:8000/api/...`
  - Key calls:
    - `GET /api/dashboard/user/{user_id}`
    - `GET /api/dashboard/activities/{user_id}`

- **Dashboard knowledge base**
  - Reads `dashboard/templates/dashboard.html`
  - Extracts:
    - HTML content
    - Inline `<script>` JS content
  - Splits into chunks for prompt context.

- **LLM runtime**
  - Uses `langchain_openai.ChatOpenAI` configured via env vars.
  - The configured model string is currently: `openai/gpt-oss-20b:free` (OpenAI-compatible gateway).

### Run it (local CLI)

```bash
python LLM/llm.py
```

Prerequisite: the FastAPI server must be running so the LLM can fetch dashboard data.

---

## 6) Stream Selection (Class 10 Stream Recommendation)

### Location

- `training/` (model artifacts and training notebooks)
- Used by `main.py` via `StreamRecommender`

### Files

- `training/stream_recommendation_dataset_2000.csv`
- `training/10_dataset.ipynb`
- `training/stream_model.pkl`
- `training/stream_scaler.pkl`
- `training/stream_label_encoder.pkl`

### APIs

- In FastAPI (`main.py`):
  - `POST /predict`
- Legacy Flask (`training/flask_app.py`):
  - `POST /predict`
  - `POST /get_insights`
  - `POST /api/mistral-chat`

---

## 7) Course Recommendation Modules (per Stream)

Each stream has:
- model/scaler/encoder pickle artifacts
- a recommender class
- a Flask app (`flask_app.py`) for standalone running

These recommenders are also imported and used by `main.py` and by `dashboard/DashboardService`.

### 7.1 Arts (`Arts_dataset/`)

- **Recommender:** `ArtsCourseRecommender` in `Arts_dataset/flask_app.py`
- **Approach:** cosine similarity over scaled feature vectors
- **Standalone API:** `POST /recommend`

### 7.2 Commerce (`Commerce_dataset/`)

- **Recommender:** `CommerceCourseRecommender` in `Commerce_dataset/flask_app.py`
- **Standalone API:** `POST /api/recommend`

### 7.3 PCM (`pcm_dataset/`)

- **Recommender:** `PCMCourseRecommender` in `pcm_dataset/flask_app.py`
- **Standalone API:** `POST /get_recommendations`

### 7.4 PCB (`pcb_dataset/`)

- **Recommender:** `PCBCourseRecommender` in `pcb_dataset/flask_app.py`
- **Standalone API:** `POST /get_recommendations` and `POST /recommend`

### 7.5 Vocational (`Vocational_dataset/`)

- **Recommender:** `VocationalCourseRecommender` in `Vocational_dataset/flask_app.py`
- **Standalone API:** `POST /recommend`

---

## 8) Interest & Quizzes (`Interest_and_quizzes/`)

### Purpose

Provides aptitude/subject quizzes and tracks quiz progress and results.

### Key components

- **`quiz_service.py`**: `QuizService` with JSON persistence (`quiz_data.json`)
- **`flask_app.py`**: standalone quiz web app + REST endpoints

### Integration

- `main.py` uses `QuizService()` and dashboard aggregates quiz results.
- `Interest_and_quizzes/flask_app.py` attempts to push quiz results into the dashboard service.

---

## 9) Dropout Risk (`Dropout_risk_factor/`)

### Purpose

Computes dropout risk score and risk level using a weighted factor model.

### Key component

- `Dropout_risk_factor/imp/dropout_risk_service.py` → `DropoutRiskService`

### Integration

- Imported and used in `main.py`.
- Results are stored into `dashboard_service.user_data[user_id]['dropout_assessment']`.

---

## 10) Career Mapping (`Career_Mapping/`)

### Purpose

Career guidance based on stream + scores, with compatibility scoring and persistence.

### Key files

- `career_service.py` → `CareerService`
  - Uses MongoDB (`pymongo`) via `Career_Mapping/database/db.py`.
- `flask_app.py` provides a standalone UI + API.

---

## 11) Content & Directories

These modules provide additional dashboard-connected features.

### 11.1 E-books (`ebooks/`)

- `ebooks_backend.py` → `EbooksBackend`
- JSON-backed library + categories + user reading progress.

### 11.2 Institution Directory (`institution_directory/`)

- `institution_backend.py` → `InstitutionBackend`
- JSON-backed institution list + filtering/search.

### 11.3 School Directory (`school_directory/`)

- `school_backend.py` → `SchoolBackend`
- JSON-backed school list + filtering/search.

### 11.4 Timeline Tracker (`timeline_tracker/`)

- `timeline_backend.py` → `TimelineBackend`
- JSON-backed events calendar + filtering/search.

---

## 12) Zephyra Chatbot (Separate Service)

### Location

- `Zephyra-Chabot-main/`

### Purpose

A separate intent-classification chatbot (TensorFlow/Keras + NLTK).

### Key files

- `zephyra_chatbot.py` → `ZephyraChatbot`
- `app.py` → Flask UI (`/chat`)
- `intents.json` + `words.pkl` + `classes.pkl` + `chatbot_model.h5`

### Run

```bash
pip install -r Zephyra-Chabot-main/requirements.txt
python Zephyra-Chabot-main/app.py
```

---

## 13) Notes / Known Limitations

- **Multiple servers**: There are several standalone Flask apps; the integrated flow is via `main.py`.
- **Persistence**: `user_data_store` is in-memory; restart clears user dashboard state.
- **Mixed dependency versions**: some model pickles were created with older sklearn; keep `scikit-learn==1.4.0` unless you re-export the pickles.

---

## 14) What to read first

- `main.py` (system orchestration + APIs)
- `dashboard/dashboard_service.py` (aggregation + user timeline)
- `dashboard/templates/dashboard.html` (dashboard UI + what LLM uses as structure)
- `LLM/llm.py` (how questions are answered using dashboard data)

