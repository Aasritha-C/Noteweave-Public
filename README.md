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

- `extension/` contains the browser extension for capture, lookup, questions and manual notes.
- `engine_stub/` describes the processing layer.

## Public Submission Note

The NEXA engine is represented in this repository as an internal processing layer. For project documentation, it can be described as an AI-based component for entity extraction, relationship mapping, graph memory management, and query interpretation. The implementation details are not included in this documentation-safe package.

## Run the extension locally

Start a compatible Noteweave backend at `http://127.0.0.1:8000`.
This repository contains the browser extension and project documentation.
The backend is installed separately.

In Chrome, open `chrome://extensions` (in Edge, use `edge://extensions`),
enable Developer mode, select **Load unpacked**, and choose the
`extension/` directory.

Select text on a web page and choose **Send to Noteweave** from the
context menu. In the popup, use **Search Memory** for a named entity,
**Ask Question** for a natural-language query, or **Manual notes** to
save and reopen recent notes. Questions and notes require their
corresponding endpoints on the local backend.
