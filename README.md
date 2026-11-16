# Discord Online Judge & Incident Management Platform

An asynchronous coding evaluation engine and SLA-driven IT support system that enables users to browse algorithmic problems, submit and execute Python code inside isolated Docker sandboxes, receive token-optimized AI debugging assistance, and report system incidents directly from Discord.

---

---

## Key Engineering Highlights

- **Containerized Code Sandboxing (`app/workers/sandbox_worker.py`):**
  Executes untrusted user submissions inside ephemeral `python:3.12-alpine` Docker containers with network access disabled (`network_disabled=True`), strict memory caps (`256MB`), read-only bind mounts (`mode='ro'`), and hard execution timeouts (`Time Limit Exceeded / TLE` protection against infinite loops).
- **Non-Blocking Asynchronous Evaluation (`app/services/judge_service.py`):**
  Decouples heavy container execution and SMTP notifications from HTTP request lifecycles using FastAPI `BackgroundTasks` and non-blocking `asyncio.to_thread` calls in the Discord event loop.
- **Token-Optimized AI Debugging (`app/services/ai_service.py`):**
  Parses Python tracebacks to locate the exact failing line number and slices a localized 5-line window around the fault before querying Gemini, reducing prompt token consumption by up to 80% on large submissions.
- **SLA Countdown & Incident Tracking (`app/api/endpoints/tickets.py`):**
  Interactive Discord UI buttons classify tickets into **Priority** (`15-minute` SLA for System/API outages) or **Necessary** (`3-hour` SLA for Problem/Code issues), featuring a real-time countdown dashboard, automatic transition to `Expired` status upon SLA breach, and automated Gmail SMTP alerts.

---

## Discord Bot Commands

This bot was created to provide an easy way to code directly on Discord without needing a PC or Mac. Users can write code directly on Discord and get results anywhere. Below is the syntax for using this bot:

- `*problems` : Show all problems.
- `*problem <id>` : View problem details (e.g., `*problem 1`).
- `*submit <id> <code>` : Submit your Python code for a problem.
- `*explain <submission_id>` : Ask AI to explain and fix your code error.
- `*ticket <description>` : Report a system or problem issue to the Admin.

---

## Tech Stack

- **Backend:** Python 3.12, FastAPI, SQLAlchemy 2.0, Pydantic
- **Database:** MySQL (`pymysql`)
- **Sandbox Runtime:** Docker SDK for Python (`python:3.12-alpine`)
- **Client & UI:** `discord.py` (Interactive Views & Buttons), Alpine.js, Tailwind CSS
- **AI & Messaging:** Google Generative AI (`gemini-3.5-flash-lite`), Python `smtplib` (SSL)

---

## Local Setup

1. **Clone the repository and create a virtual environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. **Configure environment variables:**
   Copy `.env.example` to `.env` and fill in your credentials:

   ```bash
   cp .env.example .env
   ```
3. **Pull the Python sandbox image for Docker:**

   ```bash
   docker pull python:3.12-alpine
   ```
4. **Start the FastAPI server and Admin Console:**

   ```bash
   uvicorn main:app --reload
   ```
   Open `http://127.0.0.1:8000/admin` to access the Admin Console.
5. **Run the Discord Bot:**

   ```bash
   python bot.py
   ```
