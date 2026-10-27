import type { DueFollowUps, FollowUp, Patient, PatientDetail, Revenue, Visit, VisitPayload } from "./types";

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

// The search term goes in a POST body, never the URL, so it stays out of access logs.
export const listPatients = (q?: string, includeArchived = false) =>
  q
    ? request<Patient[]>(`${BASE}/patients/search`, {
        method: "POST",
        body: JSON.stringify({ q, include_archived: includeArchived }),
      })
    : request<Patient[]>(`${BASE}/patients${includeArchived ? "?include_archived=true" : ""}`);

export const updatePatient = (id: number, data: { is_archived: boolean }) =>
  request<Patient>(`${BASE}/patients/${id}`, { method: "PATCH", body: JSON.stringify(data) });

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

export const listFollowUps = (date?: string) =>
  request<FollowUp[]>(`${BASE}/visits/follow-ups${date ? `?date=${date}` : ""}`);

export const getDueFollowUps = (asOf?: string) =>
  request<DueFollowUps>(`${BASE}/reports/follow-ups${asOf ? `?as_of=${asOf}` : ""}`);

export const getRevenue = (from: string, to: string) =>
  request<Revenue>(`${BASE}/reports/revenue?from=${from}&to=${to}`);
