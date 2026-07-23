# AI-Enabled Conversational IVR Modernization Framework

This repository contains a Flask-based conversational IVR modernization platform for designing IVR flows, managing intents and responses, uploading knowledge-base documents, and simulating calls through a browser UI.

## Overview

The application includes:

- a Flask backend in `backend/app.py`
- SQLite persistence via `backend/database.py`
- NLP and intent-classification logic under `backend/models/`
- API endpoints under `backend/routes/`
- web templates and static assets under `backend/templates/` and `backend/static/`

## Correct Project Structure

```text
.
├── LICENSE
├── README.md
└── backend/
    ├── app.py
    ├── database.py
    ├── requirements.txt
    ├── seed_data.py
    ├── ivr_platform.db
    ├── models/
    │   ├── classifier.py
    │   ├── kb_engine.py
    │   └── nlp_engine.py
    ├── routes/
    │   ├── admin.py
    │   ├── auth.py
    │   ├── flow.py
    │   ├── intent.py
    │   ├── ivr.py
    │   ├── kb.py
    │   └── reports.py
    ├── scratch/
    ├── static/
    │   ├── css/
    │   └── js/
    ├── templates/
    │   ├── admin.html
    │   ├── dashboard.html
    │   ├── designer.html
    │   ├── index.html
    │   ├── kb.html
    │   ├── login.html
    │   ├── signup.html
    │   └── simulator.html
    └── uploads/
```

## Key Features

- User login and signup flow
- Role-based admin and agent access
- IVR call simulation API
- Intent detection and response generation
- Knowledge-base upload and retrieval
- Conversation analytics and reporting
- Admin backup/restore capabilities

## Tech Stack

- Python
- Flask
- SQLite
- scikit-learn
- NLTK
- spaCy
- TextBlob
- HTML, CSS, JavaScript

## Setup

1. Open PowerShell in the repository root.
2. Go to the backend folder and create a virtual environment.

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Install the dependencies.

```powershell
pip install -r requirements.txt
```

4. Start the application.

```powershell
python app.py
```

The app should run at:

```text
http://127.0.0.1:5000
```

## Default Credentials

During first run, the database is initialized automatically and creates default users:

- `admin` / `admin123`
- `agent` / `agent123`

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
