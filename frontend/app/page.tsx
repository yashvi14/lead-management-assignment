"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";

import { submitLead } from "@/lib/api";

export default function Home() {
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setMessage("");
    setError("");

    const form = event.currentTarget;
    const formData = new FormData(form);

    try {
      await submitLead(formData);
      setMessage(
        "Thanks! We received your information and will be in touch soon."
      );
      form.reset();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="pageShell">
      <section className="card formCard">
        <div className="eyebrow">GET IN TOUCH</div>
        <h1>Tell us how we can help.</h1>
        <p className="muted">
          Submit your information and resume. A member of our legal team will
          review it and reach out.
        </p>

        <form onSubmit={handleSubmit} className="form">
          <div className="gridTwo">
            <label>
              First name
              <input name="first_name" required maxLength={100} />
            </label>

            <label>
              Last name
              <input name="last_name" required maxLength={100} />
            </label>
          </div>

          <label>
            Email
            <input name="email" type="email" required />
          </label>

          <label>
            Resume / CV
            <input
              name="resume"
              type="file"
              accept=".pdf,.doc,.docx"
              required
            />
            <span className="helpText">PDF, DOC, or DOCX. Maximum 5 MB.</span>
          </label>

          {error && <div className="alert error">{error}</div>}
          {message && <div className="alert success">{message}</div>}

          <button type="submit" disabled={submitting}>
            {submitting ? "Submitting…" : "Submit information"}
          </button>
        </form>

        <div className="adminLink">
          <Link href="/admin/login">Attorney sign in →</Link>
        </div>
      </section>
    </main>
  );
}
