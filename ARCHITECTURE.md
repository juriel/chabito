# Chabito Monorepo Architecture

## Overview

This repository is a **monorepo** with two runnable services:

1. `chabito-backend` (Python/FastAPI + LangChain/Gemini + SQLAlchemy/Postgres)
2. `chabito-whatsapp-qr` (Node.js/TypeScript + Baileys WhatsApp bridge)

The WhatsApp service receives inbound WhatsApp messages and forwards them to the backend API. The backend generates responses with Gemini via LangChain and returns text back to WhatsApp.

## Monorepo Structure

```text
/
├── chabito-backend/            # Backend API and domain/data access code
│   ├── chabito-main.py         # Main FastAPI entrypoint (uvicorn.run)
│   ├── endpoints/
│   │   ├── chat_webservice.py  # HTTP router and chat endpoint
│   │   └── dto/message_dto.py  # Pydantic request/response DTOs
│   ├── chabito/agent/
│   │   └── chabito_agent.py    # Generic tool-calling agent helper
│   ├── business/
│   │   ├── common/             # SQLAlchemy base, engine/session, GenericDAO
│   │   ├── entities/           # ORM entities (chat, tercero)
│   │   └── dao/                # DAO layer for entities
│   ├── sql/chabito.sql         # SQL schema for chat tables
│   └── requirements.txt
├── chabito-whatsapp-qr/        # WhatsApp integration service
│   ├── src/index.ts            # Service mode switch (wa vs chat CLI)
│   ├── src/whatsapp_handler.ts # Baileys socket lifecycle + message relay
│   ├── src/chat_cli.ts         # Console chat client to backend
│   └── package.json
└── README.md                   # Minimal root readme
```

## Service 1: `chabito-backend`

### Responsibilities

- Expose HTTP API routes for chat.
- Manage in-memory conversation history by `user_id`.
- Call Gemini models through LangChain.
- Define persistence model and DAO abstractions for Postgres entities.

### Runtime Entry

- File: `chabito-backend/chabito-main.py`
- Loads `.env` with `python-dotenv`.
- Requires `GOOGLE_API_KEY` (falls back to interactive prompt if missing).
- Creates `FastAPI()` app and includes `chat_webservice_api_router`.
- Runs `uvicorn` on `127.0.0.1:8000`.

### API Layer

- File: `chabito-backend/endpoints/chat_webservice.py`
- Defines class-based router (`fastapi-utils` `@cbv`) with endpoint:
  - `POST /api/chat_v2.0`
- Request DTO:
  - `message: str`
  - `user_id: str`
  - `mime_type: Optional[str]`
  - `file_base64: Optional[str]`
- Response shape (current implementation):
  - `{ "answer": "<model_output>" }`

### Chat Orchestration

`/api/chat_v2.0` flow:

1. Initialize Gemini model (`gemini-2.5-flash`) using `GOOGLE_API_KEY`.
2. Resolve conversation history from `_conversations[user_id]` (in-memory dict).
3. Build a LangChain agent with a system prompt and chat history.
4. Execute agent with input message.
5. Append `HumanMessage` and `AIMessage` to in-memory history.
6. Return `answer`.

Notes:
- Tools list is currently empty in this endpoint (`tools = []`), but agent pipeline is set up for future tool-calling.
- Conversation state is process-local and non-persistent.

### Domain and Data Access Layer

`business/common`:
- `base.py`: SQLAlchemy declarative base (`Base`).
- `connection.py`: Engine/session factory from env vars:
  - `chabito_db_user`
  - `chabito_db_password`
  - `chabito_db_host`
  - `chabito_db_port`
  - `chabito_db_dbname`
- `dao.py`: `GenericDAO` with CRUD helpers.

`business/entities`:
- `chat.py`: chat entities (`ChatContact`, `ChatConversation`, `ChatMessage`) with UUID keys and constraints.

`business/dao`:
- `chatbot_dao.py`: DAO specializations for chat entities, with query helpers.

### Database Model (Chat)

Defined in both:
- ORM: `business/entities/chat.py`
- SQL DDL: `sql/chabito.sql`

Core tables:
- `chat_contact`
- `chat_conversation`
- `chat_message`

Includes:
- UUID identifiers
- status/type check constraints
- indexes for conversation/message lookup

## Service 2: `chabito-whatsapp-qr`

### Responsibilities

- Manage WhatsApp Web session via Baileys.
- Print QR code for login.
- Receive incoming WhatsApp messages (text/media).
- Download media (image/audio), convert to base64, and forward to backend.
- Send backend response back to WhatsApp user.
- Offer a local CLI mode for manual chat testing.

### Runtime Entry

- File: `src/index.ts`
- Modes:
  - Default: WhatsApp service (`yarn start:wa`)
  - `chat`: CLI mode (`yarn start:chat`)

### WhatsApp Bridge Flow

File: `src/whatsapp_handler.ts`

1. Initialize auth state with `useMultiFileAuthState("auth_info_baileys")`.
2. Create socket via `makeWASocket`.
3. Subscribe to:
   - `creds.update`
   - `messages.upsert`
   - `connection.update`
4. On inbound message:
   - Ignore self-sent messages.
   - Detect content type (`imageMessage`, `audioMessage`, text).
   - Download media to temp file when needed.
   - Convert file to base64.
   - POST to backend `http://127.0.0.1:8000/api/chat_v2.0`.
   - Send backend `answer` as WhatsApp reply.

### CLI Flow

File: `src/chat_cli.ts`

- Reads user input from terminal.
- Calls backend endpoint (default `http://127.0.0.1:8000/api/graphrag/enhanced/ask` unless `BACKEND_URL` is set).
- Prints response to console.

## Cross-Service Interaction

Primary integration path:

1. WhatsApp user sends message.
2. `chabito-whatsapp-qr` receives and normalizes payload.
3. `chabito-whatsapp-qr` calls backend `/api/chat_v2.0`.
4. `chabito-backend` runs Gemini/LangChain inference.
5. Backend returns answer JSON.
6. WhatsApp bridge posts answer back to user chat.

Transport details:
- Protocol: HTTP JSON
- Default backend base URL: `http://127.0.0.1:8000`

## External Dependencies

Backend:
- FastAPI, Uvicorn
- LangChain (`langchain`, `langchain-core`, `langchain-google-genai`)
- Google Generative AI (Gemini)
- SQLAlchemy + psycopg2
- python-dotenv

WhatsApp service:
- `@whiskeysockets/baileys`
- `qrcode`
- `tsx`, TypeScript

## Architectural Characteristics

- **Monorepo, multi-runtime**: Python backend + Node.js integration service.
- **Layered backend**: endpoints -> DTOs -> agent/orchestration -> DAO/entity (partially wired).
- **State model**:
  - Chat memory in backend is in-process and volatile.
  - WhatsApp auth is file-based (`auth_info_baileys`) and persistent across runs.
- **Tight local coupling by default**: services assume localhost backend URL.

## Current Gaps / Observations

- Root `README.md` is minimal; operational docs live in subprojects.
- Backend README lists additional endpoints that are not present in current `chat_webservice.py`.
- Two SQLAlchemy base definitions exist:
  - `business/common/base.py`
  - `business/entities/chat.py` (local `DeclarativeBase`)
  This can split metadata management unless intentionally separated.
- `chat_cli.ts` default endpoint differs from WhatsApp handler endpoint; environment config is important for consistency.

