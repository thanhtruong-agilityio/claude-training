import type { Patient, PatientDetail, Visit, VisitPayload } from "./types";

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

export const getPatient = (id: number) => request<PatientDetail>(`${BASE}/patients/${id}`);

export const createVisit = (patientId: number, data: VisitPayload) =>
  request<Visit>(`${BASE}/patients/${patientId}/visits`, {
    method: "POST",
    body: JSON.stringify(data),
  });

export const updateVisit = (id: number, data: VisitPayload) =>
  request<Visit>(`${BASE}/visits/${id}`, { method: "PUT", body: JSON.stringify(data) });

export const deleteVisit = (id: number) =>
  request<unknown>(`${BASE}/visits/${id}`, { method: "DELETE" });
