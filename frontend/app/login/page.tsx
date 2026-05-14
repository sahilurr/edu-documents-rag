"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { BookOpen, Loader2 } from "lucide-react";
import { login, signup } from "@/lib/api";
import { setToken } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [role, setRole] = useState<"student" | "teacher" | "admin">("teacher");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      if (mode === "signup") {
        await signup(email, password, fullName, role);
      }
      const token = await login(email, password);
      setToken(token);
      router.push("/chat");
    } catch (err: any) {
      setError(err?.message ?? "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="flex items-center gap-3 mb-8 justify-center">
          <div className="p-2 rounded-lg bg-accent/15">
            <BookOpen className="w-6 h-6 text-accent" />
          </div>
          <div>
            <h1 className="text-xl font-semibold">Edu RAG</h1>
            <p className="text-xs text-foreground/60">Research-grade grounded answers</p>
          </div>
        </div>

        <form
          onSubmit={handleSubmit}
          className="bg-muted/40 border rounded-xl p-6 space-y-4"
        >
          <div className="flex gap-2 text-sm">
            <button
              type="button"
              onClick={() => setMode("login")}
              className={`flex-1 py-2 rounded-md ${mode === "login" ? "bg-accent text-white" : "bg-transparent border"}`}
            >
              Login
            </button>
            <button
              type="button"
              onClick={() => setMode("signup")}
              className={`flex-1 py-2 rounded-md ${mode === "signup" ? "bg-accent text-white" : "bg-transparent border"}`}
            >
              Sign up
            </button>
          </div>

          {mode === "signup" && (
            <>
              <label className="block">
                <span className="text-sm text-foreground/70">Full name</span>
                <input
                  type="text"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="mt-1 w-full rounded-md bg-background border px-3 py-2 text-sm"
                />
              </label>
              <label className="block">
                <span className="text-sm text-foreground/70">Role</span>
                <select
                  value={role}
                  onChange={(e) => setRole(e.target.value as any)}
                  className="mt-1 w-full rounded-md bg-background border px-3 py-2 text-sm"
                >
                  <option value="student">Student</option>
                  <option value="teacher">Teacher</option>
                  <option value="admin">Admin</option>
                </select>
              </label>
            </>
          )}

          <label className="block">
            <span className="text-sm text-foreground/70">Email</span>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 w-full rounded-md bg-background border px-3 py-2 text-sm"
            />
          </label>

          <label className="block">
            <span className="text-sm text-foreground/70">Password</span>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 w-full rounded-md bg-background border px-3 py-2 text-sm"
            />
          </label>

          {error && (
            <div className="text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded-md px-3 py-2">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-accent text-white py-2 rounded-md text-sm font-medium hover:bg-accent/90 disabled:opacity-60 flex items-center justify-center gap-2"
          >
            {loading && <Loader2 className="w-4 h-4 animate-spin" />}
            {mode === "login" ? "Sign in" : "Create account & sign in"}
          </button>
        </form>
      </div>
    </main>
  );
}
