export const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export type LeadStatus = "PENDING" | "REACHED_OUT";

export type Lead = {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  resume_original_name: string;
  resume_content_type: string;
  status: LeadStatus;
  created_at: string;
  updated_at: string;
};

async function parseError(response: Response): Promise<string> {
  try {
    const data = await response.json();
    return data.detail ?? "Request failed";
  } catch {
    return "Request failed";
  }
}

export async function submitLead(formData: FormData) {
  const response = await fetch(`${API_URL}/leads`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error(await parseError(response));
  }

  return response.json();
}

export async function login(email: string, password: string) {
  const response = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    throw new Error(await parseError(response));
  }

  return response.json() as Promise<{
    access_token: string;
    token_type: string;
  }>;
}

export async function getLeads(token: string): Promise<Lead[]> {
  const response = await fetch(`${API_URL}/leads`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(await parseError(response));
  }

  return response.json();
}

export async function markReachedOut(
  token: string,
  leadId: string
): Promise<Lead> {
  const response = await fetch(`${API_URL}/leads/${leadId}/status`, {
    method: "PATCH",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ status: "REACHED_OUT" }),
  });

  if (!response.ok) {
    throw new Error(await parseError(response));
  }

  return response.json();
}

export async function downloadResume(
  token: string,
  leadId: string,
  filename: string
) {
  const response = await fetch(`${API_URL}/leads/${leadId}/resume`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!response.ok) {
    throw new Error(await parseError(response));
  }

  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}
