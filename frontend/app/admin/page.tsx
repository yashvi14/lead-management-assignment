"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import {
  downloadResume,
  getLeads,
  Lead,
  markReachedOut,
} from "@/lib/api";

export default function AdminPage() {
  const router = useRouter();
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [updatingId, setUpdatingId] = useState<string | null>(null);

  const loadLeads = useCallback(async () => {
    const token = localStorage.getItem("lead_admin_token");
    if (!token) {
      router.replace("/admin/login");
      return;
    }

    try {
      setError("");
      setLeads(await getLeads(token));
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unable to load leads.";
      setError(message);

      if (message.toLowerCase().includes("authentication")) {
        localStorage.removeItem("lead_admin_token");
        router.replace("/admin/login");
      }
    } finally {
      setLoading(false);
    }
  }, [router]);

  useEffect(() => {
    loadLeads();
  }, [loadLeads]);

  async function handleMarkReachedOut(leadId: string) {
    const token = localStorage.getItem("lead_admin_token");
    if (!token) return;

    setUpdatingId(leadId);
    setError("");

    try {
      const updated = await markReachedOut(token, leadId);
      setLeads((current) =>
        current.map((lead) => (lead.id === leadId ? updated : lead))
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Update failed.");
    } finally {
      setUpdatingId(null);
    }
  }

  async function handleDownload(lead: Lead) {
    const token = localStorage.getItem("lead_admin_token");
    if (!token) return;

    try {
      await downloadResume(token, lead.id, lead.resume_original_name);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Download failed.");
    }
  }

  function logout() {
    localStorage.removeItem("lead_admin_token");
    router.push("/admin/login");
  }

  return (
    <main className="dashboardShell">
      <header className="dashboardHeader">
        <div>
          <div className="eyebrow">INTERNAL LEAD MANAGEMENT</div>
          <h1>Prospect leads</h1>
          <p className="muted">
            Review incoming prospects and track outreach.
          </p>
        </div>
        <button className="secondaryButton" onClick={logout}>
          Sign out
        </button>
      </header>

      {error && <div className="alert error">{error}</div>}

      {loading ? (
        <div className="card emptyState">Loading leads…</div>
      ) : leads.length === 0 ? (
        <div className="card emptyState">
          No leads yet. Submit one through the public form.
        </div>
      ) : (
        <div className="tableCard">
          <table>
            <thead>
              <tr>
                <th>Prospect</th>
                <th>Email</th>
                <th>Resume</th>
                <th>Submitted</th>
                <th>Status</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {leads.map((lead) => (
                <tr key={lead.id}>
                  <td>
                    <strong>
                      {lead.first_name} {lead.last_name}
                    </strong>
                  </td>
                  <td>{lead.email}</td>
                  <td>
                    <button
                      className="linkButton"
                      onClick={() => handleDownload(lead)}
                    >
                      {lead.resume_original_name}
                    </button>
                  </td>
                  <td>{new Date(lead.created_at).toLocaleString()}</td>
                  <td>
                    <span
                      className={`statusBadge ${
                        lead.status === "PENDING" ? "pending" : "reached"
                      }`}
                    >
                      {lead.status === "PENDING" ? "Pending" : "Reached out"}
                    </span>
                  </td>
                  <td className="actionCell">
                    {lead.status === "PENDING" ? (
                      <button
                        className="smallButton"
                        disabled={updatingId === lead.id}
                        onClick={() => handleMarkReachedOut(lead.id)}
                      >
                        {updatingId === lead.id
                          ? "Updating…"
                          : "Mark reached out"}
                      </button>
                    ) : (
                      <span className="complete">✓ Complete</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </main>
  );
}
