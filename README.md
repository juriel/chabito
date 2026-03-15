# Chabito - AI Chatbot Ecosystem

Bienvenido al monorepo de **Chabito**, un ecosistema modular diseñado para la gestión inteligente de interacciones a través de WhatsApp y servicios backend con capacidades de IA.

## Estructura del Monorepo

El proyecto está dividido en dos aplicaciones principales:

### 1. [Backend (Python/FastAPI)](chabito-backend/)
El motor central del sistema. Proporciona servicios de:
- **FastAPI**: Endpoints para mensajería y gestión de negocio.
- **RAG (Retrieval-Augmented Generation)**: Integración con Neo4j y Supabase para respuestas contextuales sobre productos y proveedores.
- **IA Generativa**: Soporte para modelos de OpenAI y Google Gemini.

### 2. [WhatsApp QR (Node.js/Yarn)](chabito-whatsapp-qr/)
Servicio de mensajería que conecta con WhatsApp:
- **WhatsApp Gateway**: Basado en `@whiskeysockets/baileys` para autenticación por código QR.
- **CLI Chat**: Interfaz de línea de comandos para interactuar manualmente con el backend.

---

## Inicio Rápido

### Requisitos Previos
- Python 3.11+
- Node.js & Yarn
- PostgreSQL con extensión `pgvector`
- Clave de API de Google Gemini (`GOOGLE_API_KEY`)

### Instalación General

1. **Backend**:
    ```bash
    cd chabito-backend
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

2. **WhatsApp QR**:
    ```bash
    cd chabito-whatsapp-qr
    yarn
    ```

---

## Ejecución

1. **Lanzar Backend**:
    ```bash
    cd chabito-backend
    python chabito-main.py
    ```

2. **Lanzar WhatsApp QR**:
    ```bash
    cd chabito-whatsapp-qr
    yarn start:wa
    ```

Para más detalles, consulta los README específicos de cada componente.
