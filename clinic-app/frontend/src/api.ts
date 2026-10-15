import type { Patient } from "./types";

const BASE = "/api";

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return res.json() as Promise<T>;
}

export type NewPatient = Partial<Omit<Patient, "id" | "is_archived" | "created_at">> & {
  full_name: string;
};

export const listPatients = (q?: string) =>
  request<Patient[]>(`${BASE}/patients${q ? `?q=${encodeURIComponent(q)}` : ""}`);

export const createPatient = (data: NewPatient) =>
  request<Patient>(`${BASE}/patients`, { method: "POST", body: JSON.stringify(data) });
