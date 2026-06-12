<div align="center">

# REMI

**Your documents, understood.**

Upload any document — PDF, Word, PowerPoint, or text — and chat with it.
REMI summarizes your file instantly and answers follow-up questions using
retrieval-augmented generation with page-level citations.

[Live Demo](https://github.com/hirensai111/Remi#) · [Report Bug](https://github.com/hirensai111/Remi/issues) · [Request Feature](https://github.com/hirensai111/Remi/issues)

</div>

---

## Features

- **Multi-format ingestion** — Drop a PDF, DOCX, PPTX, TXT, or Markdown file
- **Instant summarization** — Get a concise overview + key bullet points in seconds
- **Natural Q&A** — Ask vague or specific questions; REMI infers intent from context
- **Page citations** — Answers cite the exact page or slide they came from
- **Query rewriting** — Follow-ups like "is it safe?" are automatically expanded into
  searchable standalone queries before retrieval
- **Smart truncation** — Large documents are gracefully truncated to fit the model context
- **Liquid-glass UI** — A polished, translucent interface with ambient animated backgrounds

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, FastAPI |
| Document parsing | PyMuPDF, python-docx, python-pptx |
| Embeddings | sentence-transformers (`all-MiniLM-L6-v2`) |
| Vector search | In-memory numpy cosine similarity |
| LLM | OpenAI GPT API (default: `gpt-5.4-nano`) |
| Frontend | Vanilla HTML, CSS, JavaScript |
| Deployment | Railway |

## Architecture

```
User uploads file
      |
      v
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   ingest    │────▶│   chunk &   │────▶│   embed &   │
│  (PyMuPDF)  │     │   overlap   │     │    store    │
└─────────────┘     └─────────────┘     └─────────────┘
      |                                          |
      v                                          v
┌─────────────┐                         ┌─────────────┐
│  summarize  │                         │  retrieve   │
│   (LLM)     │                         │   (numpy)   │
└─────────────┘                         └─────────────┘
                                               |
User asks question ──▶ query rewrite ──▶ top-8 chunks
                                               |
                                               v
                                        ┌─────────────┐
                                        │   answer    │
                                        │   (LLM)     │
                                        └─────────────┘
```

## Quick Start (Local)

### Prerequisites

- Python 3.11+
- An [OpenAI API key](https://platform.openai.com/api-keys)

### 1. Clone the repo

```bash
git clone https://github.com/hirensai111/Remi.git
cd Remi
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> **Note:** The first run will download the `all-MiniLM-L6-v2` embedding model (~90 MB).

### 4. Add your API key

```bash
cp .env.example .env
# Edit .env and paste your OpenAI API key
```

### 5. Run the app

```bash
cd backend && uvicorn main:app --reload
```

Open http://localhost:8000 in your browser. The backend serves both the API and the frontend.

---

## Deploy on Railway

1. **Fork or push** this repo to your GitHub account.
2. Go to [Railway](https://railway.app) → **New Project** → **Deploy from GitHub repo**.
3. Select your `Remi` repository.
4. Add these environment variables in Railway's dashboard:
   - `OPENAI_API_KEY` — your OpenAI API key
   - `OPENAI_BASE_URL` — `https://api.openai.com/v1` (optional)
   - `OPENAI_MODEL` — `gpt-5.4-nano` (optional)
5. Click **Deploy**.

Railway will auto-detect Python, install dependencies, and start the FastAPI server. Your custom domain will serve the full app.

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | **Yes** | — | Your OpenAI API key |
| `OPENAI_BASE_URL` | No | `https://api.openai.com/v1` | API base URL (supports proxies / Azure) |
| `OPENAI_MODEL` | No | `gpt-5.4-nano` | Model name for completions |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/upload` | Upload a document file |
| `POST` | `/ask` | Ask a question about the uploaded document |

### Upload

```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@document.pdf"
```

**Response:**
```json
{
  "document_id": "uuid",
  "summary": "Document summary...",
  "page_count": 12,
  "truncated": false,
  "pages_read": 12,
  "file_type": "pdf"
}
```

### Ask

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"document_id": "uuid", "question": "What are the key risks?"}'
```

**Response:**
```json
{
  "answer": "According to Page 4..."
}
```

---

## Project Structure

```
Remi/
├── backend/
│   ├── main.py           # FastAPI app, LLM calls, RAG pipeline
│   ├── ingest.py         # Multi-format document text extraction
│   ├── retrieval.py      # Chunking, embeddings, vector search
│   └── requirements.txt  # Python dependencies
├── frontend/
│   └── index.html        # Single-file liquid-glass UI
├── .env                  # Environment variables (not committed)
├── .gitignore
├── Procfile              # Railway process definition
├── mise.toml             # Mise configuration for Railway builds
├── README.md
└── REMI_About.pdf        # Short project overview
```

---

## How It Works

1. **Ingestion** — `ingest.py` extracts text from your file, preserving page/slide markers.
2. **Chunking** — Documents are split into ~1000-character overlapping chunks.
3. **Embedding** — `sentence-transformers` encodes chunks into 384-dimension vectors.
4. **Storage** — Vectors live in a simple in-memory dict keyed by document ID.
5. **Query Rewriting** — Vague follow-ups are rewritten into standalone search queries via a small LLM call.
6. **Retrieval** — Cosine similarity ranks chunks; top 8 are returned.
7. **Answer Generation** — The LLM receives only the relevant excerpts + conversation history + your original question.

---

## License

MIT

---
