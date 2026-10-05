# 🚀 OpsPilot

**OpsPilot** is an AI-powered production operations agent designed to help engineers investigate operational issues, retrieve relevant documentation, analyze incidents, and eventually recommend or execute remediation actions.

The project is being built as a production-oriented AI engineering system using FastAPI, LLMs, RAG, tool calling, observability, and agentic workflows.

> Current Version: **v0.1.0 — Request Pipeline**

---

## 🎯 Project Goal

OpsPilot aims to provide an AI operations assistant capable of interacting with production engineering systems such as:

- Application logs
- Kubernetes
- AWS / cloud infrastructure
- Monitoring systems
- Internal documentation
- Incident reports
- Operational APIs

The long-term request flow will look like:

```text
User
  │
  ▼
FastAPI API
  │
  ▼
AI Agent
  │
  ├── RAG / Knowledge Base
  ├── Operational Tools
  ├── Logs
  ├── Kubernetes
  ├── Cloud APIs
  └── Monitoring
  │
  ▼
LLM Reasoning
  │
  ▼
Recommendation / Action
```

---

## ✅ Current Version — v0.1.0

The first development milestone implements the basic API request pipeline.

Current flow:

```text
Client
   │
   │ POST /api/v1/chat
   ▼
FastAPI
   │
   ▼
Pydantic Validation
   │
   ▼
Chat Router
   │
   ▼
ChatResponse
   │
   ▼
Client
```

### Implemented

- FastAPI application
- API routing
- Pydantic request validation
- Pydantic response models
- Environment-based configuration
- Health endpoint
- Swagger / OpenAPI documentation
- Modular backend structure

AI/LLM functionality is intentionally not implemented yet.

---

## 🏗️ Project Structure

```text
ops-pilot/
├── backend/
│   └── app/
│       ├── api/
│       │   └── routes/
│       │       └── chat.py
│       ├── agents/
│       ├── core/
│       │   └── config.py
│       ├── models/
│       │   └── chat.py
│       ├── rag/
│       ├── services/
│       ├── tools/
│       └── main.py
│
├── data/
│   ├── documents/
│   └── incidents/
│
├── tests/
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

---

## 🛠️ Technology Stack

Current:

- Python
- FastAPI
- Uvicorn
- Pydantic
- Pydantic Settings

Planned:

- OpenAI / LLM APIs
- Embeddings
- Vector database
- Retrieval-Augmented Generation (RAG)
- Agent tool calling
- Kubernetes API
- Cloud APIs
- Observability
- Docker
- Automated evaluation
- CI/CD

---

## ⚙️ Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/DevFlores01/ops-pilot.git
cd ops-pilot
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Git Bash on Windows:

```bash
source .venv/Scripts/activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy:

```text
.env.example
```

to:

```text
.env
```

Then configure the required values.

Never commit `.env` or API keys to Git.

### 5. Start the API

```bash
cd backend

uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

---

## 🔌 API

### Health Check

```http
GET /health
```

Example response:

```json
{
  "status": "healthy",
  "environment": "development"
}
```

### Chat

```http
POST /api/v1/chat
```

Example request:

```json
{
  "message": "Why is my production API returning HTTP 500 errors?"
}
```

Example v0.1 response:

```json
{
  "message": "OpsPilot received: Why is my production API returning HTTP 500 errors?",
  "status": "received"
}
```

---

## 🗺️ Development Roadmap

### v0.1 — Request Pipeline ✅

FastAPI → validation → router → response

### v0.2 — LLM Integration

FastAPI → service layer → LLM → structured response

### v0.3 — RAG

Documents → chunking → embeddings → vector store → retrieval → LLM

### v0.4 — Tool Calling

Allow the agent to safely invoke operational tools.

### v0.5 — Operations Integrations

Integrate systems such as Kubernetes, logs, monitoring, and cloud infrastructure.

### v0.6 — Agent Orchestration

Implement reasoning and controlled multi-step operational workflows.

### v0.7 — Evaluation & Observability

Add tracing, metrics, AI evaluation, latency monitoring, and failure analysis.

### v1.0 — Production-Ready OpsPilot

Containerized, tested, observable, secure, and deployable production AI operations agent.

---

## 🔐 Security

OpsPilot is intended to interact with production infrastructure, so security is a core design requirement.

Future versions will include:

- Read-only tools by default
- Explicit authorization for actions
- Tool input validation
- Secret management
- Audit logging
- Human approval for destructive actions
- Least-privilege infrastructure access

---

## 📌 Project Status

**Active development**

Current milestone:

```text
v0.1.0 — Request Pipeline
```

Next milestone:

```text
v0.2.0 — LLM Integration
```
