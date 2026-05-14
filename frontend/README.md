# Edu RAG — Frontend

Next.js 14 (App Router) + TypeScript + Tailwind chat UI for the educational RAG backend.

## Features

- JWT login / signup (talks to FastAPI `/api/v1/auth`)
- Document sidebar with upload and chunk/page stats (`/api/v1/upload/documents`)
- Streaming chat using Server-Sent Events from `/api/v1/chat/stream`
- Inline citation chips with rerank score, expandable source snippets
- Dark theme by default

## Setup

```bash
cd frontend
cp .env.local.example .env.local   # adjust NEXT_PUBLIC_API_URL if backend is not on :8000
npm install
npm run dev
```

Open http://localhost:3000.

The Next dev server rewrites `/api/*` to `${NEXT_PUBLIC_API_URL}/api/v1/*` so
no CORS issues and the JWT token (stored in localStorage) is sent transparently.

## Architecture

- `app/login` — auth screen, stores token in localStorage
- `app/chat`  — main 2-pane layout (Sidebar + ChatWindow)
- `lib/api.ts` — typed API client including SSE parser for streaming chat
- `components/` — `Sidebar`, `ChatWindow`, `MessageBubble`, `CitationList`
