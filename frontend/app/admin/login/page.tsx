"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { login } from "@/lib/api";

export default function AdminLoginPage() {
  const router = useRouter();
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (localStorage.getItem("lead_admin_token")) {
      router.replace("/admin");
    }
  }, [router]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError("");

    const data = new FormData(event.currentTarget);
    const email = String(data.get("email") ?? "");
    const password = String(data.get("password") ?? "");

    try {
      const result = await login(email, password);
      localStorage.setItem("lead_admin_token", result.access_token);
      router.push("/admin");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to sign in.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="pageShell">
      <section className="card loginCard">
        <div className="eyebrow">INTERNAL</div>
        <h1>Attorney sign in</h1>
        <p className="muted">Sign in to review and manage submitted leads.</p>

        <form onSubmit={handleSubmit} className="form">
          <label>
            Email
            <input name="email" type="email" required />
          </label>

          <label>
            Password
            <input name="password" type="password" required />
          </label>

          {error && <div className="alert error">{error}</div>}

          <button type="submit" disabled={submitting}>
            {submitting ? "Signing in…" : "Sign in"}
          </button>
        </form>
      </section>
    </main>
  );
}
