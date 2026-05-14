import { authHeaders } from "./auth";

export type SourceCitation = {
  source: string;
  page: number | null;
  snippet: string;
  score?: number | null;
};

export type IndexedDocument = {
  filename: string;
  chunks: number;
  pages: number;
};

// All requests go through Next.js rewrite -> backend /api/v1
const API = "/api";

export async function login(email: string, password: string): Promise<string> {
  const body = new URLSearchParams();
  body.set("username", email);
  body.set("password", password);
  const res = await fetch(`${API}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(parseError(text) || "Login failed");
  }
  const data = (await res.json()) as { access_token: string };
  return data.access_token;
}

export async function signup(
  email: string,
  password: string,
  fullName: string,
  role: "student" | "teacher" | "admin"
): Promise<void> {
  const res = await fetch(`${API}/auth/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email,
      password,
      full_name: fullName,
      role,
    }),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(parseError(text) || "Signup failed");
  }
}

export async function listDocuments(): Promise<IndexedDocument[]> {
  const res = await fetch(`${API}/upload/documents`, {
    headers: { ...authHeaders() },
  });
  if (!res.ok) throw new Error("Failed to load documents");
  const data = (await res.json()) as { documents: IndexedDocument[] };
  return data.documents;
}

export async function uploadDocument(file: File): Promise<void> {
  const fd = new FormData();
  fd.append("file", file);
  const res = await fetch(`${API}/upload/`, {
    method: "POST",
    headers: { ...authHeaders() },
    body: fd,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(parseError(text) || "Upload failed");
  }
}

export type StreamEvent =
  | { type: "sources"; sources: SourceCitation[] }
  | { type: "token"; token: string }
  | { type: "done"; answer: string }
  | { type: "error"; message: string };

/**
 * Stream chat tokens from the backend SSE endpoint.
 * The backend emits events: sources | token | done | error.
 */
export async function streamChat(
  query: string,
  onEvent: (event: StreamEvent) => void,
  signal?: AbortSignal
): Promise<void> {
  const res = await fetch(`${API}/chat/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
    },
    body: JSON.stringify({ query }),
    signal,
  });

  if (!res.ok || !res.body) {
    const text = await res.text().catch(() => "");
    throw new Error(parseError(text) || `Stream error ${res.status}`);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder("utf-8");
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    // SSE frames are separated by a blank line.
    let sepIdx;
    while ((sepIdx = buffer.indexOf("\n\n")) !== -1) {
      const frame = buffer.slice(0, sepIdx);
      buffer = buffer.slice(sepIdx + 2);
      const event = parseSseFrame(frame);
      if (event) onEvent(event);
    }
  }
}

function parseSseFrame(frame: string): StreamEvent | null {
  let event = "message";
  let dataRaw = "";
  for (const line of frame.split("\n")) {
    if (line.startsWith("event:")) event = line.slice(6).trim();
    else if (line.startsWith("data:")) dataRaw += line.slice(5).trim();
  }
  if (!dataRaw) return null;
  let parsed: unknown;
  try {
    parsed = JSON.parse(dataRaw);
  } catch {
    parsed = dataRaw;
  }
  switch (event) {
    case "sources":
      return { type: "sources", sources: (parsed as SourceCitation[]) || [] };
    case "token":
      return { type: "token", token: String(parsed ?? "") };
    case "done":
      return { type: "done", answer: String(parsed ?? "") };
    case "error":
      return { type: "error", message: String(parsed ?? "Unknown error") };
    default:
      return null;
  }
}

function parseError(text: string): string | null {
  try {
    const j = JSON.parse(text);
    if (typeof j?.detail === "string") return j.detail;
    if (Array.isArray(j?.detail)) return j.detail.map((d: any) => d.msg).join(", ");
    return null;
  } catch {
    return null;
  }
}
