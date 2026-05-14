"use client";

import { useEffect, useRef, useState } from "react";
import { FileText, Upload, Loader2, LogOut, RefreshCw } from "lucide-react";
import { IndexedDocument, listDocuments, uploadDocument } from "@/lib/api";
import { clearToken } from "@/lib/auth";
import { useRouter } from "next/navigation";

export default function Sidebar() {
  const router = useRouter();
  const [docs, setDocs] = useState<IndexedDocument[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInput = useRef<HTMLInputElement | null>(null);

  async function refresh() {
    setLoading(true);
    setError(null);
    try {
      setDocs(await listDocuments());
    } catch (err: any) {
      setError(err?.message ?? "Failed to load documents");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function handleFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setError(null);
    try {
      await uploadDocument(file);
      await refresh();
    } catch (err: any) {
      setError(err?.message ?? "Upload failed");
    } finally {
      setUploading(false);
      if (fileInput.current) fileInput.current.value = "";
    }
  }

  function handleLogout() {
    clearToken();
    router.push("/login");
  }

  return (
    <aside className="w-72 shrink-0 border-r flex flex-col bg-muted/30">
      <div className="px-4 py-4 border-b">
        <h2 className="font-semibold text-sm">Documents</h2>
        <p className="text-xs text-foreground/60 mt-0.5">
          Source-of-truth for every answer
        </p>
      </div>

      <div className="px-4 py-3 border-b space-y-2">
        <input
          ref={fileInput}
          type="file"
          accept=".pdf,.txt"
          className="hidden"
          onChange={handleFile}
        />
        <button
          onClick={() => fileInput.current?.click()}
          disabled={uploading}
          className="w-full bg-accent text-white text-sm rounded-md py-2 flex items-center justify-center gap-2 hover:bg-accent/90 disabled:opacity-60"
        >
          {uploading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Upload className="w-4 h-4" />
          )}
          {uploading ? "Indexing..." : "Upload PDF / TXT"}
        </button>
        <button
          onClick={refresh}
          className="w-full text-xs text-foreground/60 hover:text-foreground flex items-center justify-center gap-1"
        >
          <RefreshCw className="w-3 h-3" /> Refresh
        </button>
      </div>

      <div className="flex-1 overflow-y-auto scrollbar-thin">
        {loading && (
          <div className="p-4 text-xs text-foreground/60 flex items-center gap-2">
            <Loader2 className="w-3 h-3 animate-spin" /> Loading...
          </div>
        )}
        {error && (
          <div className="p-4 text-xs text-red-400">{error}</div>
        )}
        {!loading && docs.length === 0 && !error && (
          <div className="p-4 text-xs text-foreground/60">
            No documents yet. Upload a PDF or TXT to get started.
          </div>
        )}
        <ul className="py-2">
          {docs.map((d) => (
            <li
              key={d.filename}
              className="px-4 py-2 flex items-start gap-2 hover:bg-muted/60"
            >
              <FileText className="w-4 h-4 mt-0.5 text-foreground/60" />
              <div className="min-w-0">
                <div className="text-sm truncate">{d.filename}</div>
                <div className="text-[10px] text-foreground/50">
                  {d.chunks} chunks · {d.pages} pages
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>

      <button
        onClick={handleLogout}
        className="border-t px-4 py-3 text-xs text-foreground/60 hover:text-foreground flex items-center gap-2"
      >
        <LogOut className="w-3 h-3" /> Sign out
      </button>
    </aside>
  );
}
