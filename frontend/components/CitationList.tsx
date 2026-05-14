"use client";

import { useState } from "react";
import { FileText, ChevronDown, ChevronRight } from "lucide-react";
import { SourceCitation } from "@/lib/api";

export default function CitationList({ sources }: { sources: SourceCitation[] }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="mt-2">
      <button
        onClick={() => setOpen((o) => !o)}
        className="text-xs text-foreground/60 hover:text-foreground flex items-center gap-1"
      >
        {open ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
        {sources.length} source{sources.length === 1 ? "" : "s"}
      </button>
      <div className="flex flex-wrap gap-1.5 mt-1.5">
        {sources.map((s, i) => (
          <span
            key={i}
            title={s.snippet}
            className="inline-flex items-center gap-1 text-[11px] bg-muted/70 border rounded-full px-2 py-0.5"
          >
            <FileText className="w-3 h-3 text-foreground/60" />
            <span className="font-medium">[{i + 1}]</span>
            <span className="truncate max-w-[160px]">{s.source}</span>
            {s.page != null && <span className="text-foreground/50">p.{s.page}</span>}
            {typeof s.score === "number" && (
              <span className="text-foreground/40">· {s.score.toFixed(2)}</span>
            )}
          </span>
        ))}
      </div>
      {open && (
        <ul className="mt-2 space-y-2">
          {sources.map((s, i) => (
            <li
              key={i}
              className="text-xs border rounded-md p-2 bg-muted/40"
            >
              <div className="font-medium text-foreground/80">
                [{i + 1}] {s.source}
                {s.page != null && (
                  <span className="font-normal text-foreground/50"> · page {s.page}</span>
                )}
              </div>
              <div className="text-foreground/60 mt-1">{s.snippet}</div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
