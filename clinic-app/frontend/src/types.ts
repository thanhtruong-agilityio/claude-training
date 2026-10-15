export interface Patient {
  id: number;
  full_name: string;
  birth_year: number | null;
  sex: string | null;
  phone: string | null;
  address: string | null;
  allergies: string | null;
  medical_history: string | null;
  is_archived: boolean;
  created_at: string;
  last_visit_date?: string | null;
}

export interface PrescriptionItem {
  id?: number;
  drug_name: string;
  dosage: string | null;
  days: number;
  note: string | null;
}

export interface Visit {
  id: number;
  patient_id: number;
  visited_at: string;
  symptoms: string | null;
  diagnosis: string | null;
  notes: string | null;
  weight_kg: number | null;
  temperature_c: number | null;
  blood_pressure: string | null;
  fee: number;
  paid_amount: number;
  follow_up_date: string | null;
  deleted_at: string | null;
  items: PrescriptionItem[];
}

export interface PatientDetail extends Patient {
  visits: Visit[];
}

export type VisitPayload = Omit<Visit, "id" | "patient_id" | "deleted_at" | "visited_at"> & {
  visited_at?: string;
};

export interface FollowUp {
  visit_id: number;
  patient_id: number;
  full_name: string;
  phone: string | null;
  follow_up_date: string;
}

export interface Revenue {
  visit_count: number;
  collected: number;
  owed: number;
}
