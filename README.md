# Noteweave

Noteweave is a local-first, subject-based annotation system. It lets a browser
extension capture selected text and send it to a local API, where an internal AI
processing layer extracts subjects, relationships, and searchable memory links.

## Project Idea

Traditional notes store text as isolated blocks. Noteweave stores captured text
as subject-centered knowledge, so users can later search by entity or ask simple
questions such as:

- Where is Steve?
- Who holds the apple?
- What is connected to this subject?

## Architecture

```text
Browser Extension
        |
        v
Local Noteweave API
        |
        v
Internal NEXA Processing Engine
        |
        v
Subject-Based Graph Memory
        |
        v
Query Interface
```

## Components

- `extension/` contains the Chrome extension for capture and lookup.
- `main.py` exposes the local FastAPI endpoints.
- `src/` contains the private/internal NEXA processing implementation.
- `data/` is local runtime memory and should not be committed or shared.

## Public Submission Note

The NEXA engine is represented in this repository as an internal processing layer. For project documentation, it can be described as an AI-based component for entity extraction, relationship mapping, graph memory management, and query interpretation. The implementation details are not included in this documentation-safe package.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

Ollama must be running locally with the configured model available:

```powershell
ollama pull qwen2.5-coder:1.5b
```

## Run

```powershell
python main.py
```

The API starts at:

```text
http://127.0.0.1:8000
```

Useful endpoints:

- `GET /health`
- `POST /ingest`
- `GET /query?q=Where is Steve?`
- `GET /query/Steve`
- `DELETE /clear`
