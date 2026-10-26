import { useCallback, useEffect, useState } from "react";
import { createVisit, deleteVisit, getPatient, updatePatient, updateVisit } from "../api";
import VisitForm from "../components/VisitForm";
import type { PatientDetail, Visit, VisitPayload } from "../types";

interface Props {
  id: number;
  onBack: () => void;
}

type Mode = { name: "view" } | { name: "new" } | { name: "edit"; visit: Visit };

export default function PatientRecordPage({ id, onBack }: Props) {
  const [patient, setPatient] = useState<PatientDetail | null>(null);
  const [mode, setMode] = useState<Mode>({ name: "view" });
  const [confirmingArchive, setConfirmingArchive] = useState(false);

  const load = useCallback(() => {
    getPatient(id).then(setPatient);
  }, [id]);

  useEffect(load, [load]);

  const save = async (data: VisitPayload) => {
    if (mode.name === "edit") await updateVisit(mode.visit.id, data);
    else await createVisit(id, data);
    setMode({ name: "view" });
    load();
  };

  // Archiving asks twice on the page itself: window.confirm would block browser automation.
  const setArchived = async (is_archived: boolean) => {
    await updatePatient(id, { is_archived });
    setConfirmingArchive(false);
    load();
  };

  const remove = async (visitId: number) => {
    await deleteVisit(visitId);
    load();
  };

  if (!patient) return <p>Loading…</p>;

  return (
    <main>
      <button onClick={onBack}>Back</button>
      <h1>{patient.full_name}</h1>
      {patient.is_archived && <p className="meta">Archived</p>}
      <div className="actions">
        {patient.is_archived ? (
          <button onClick={() => setArchived(false)}>Unarchive</button>
        ) : confirmingArchive ? (
          <>
            <button className="btn-danger" onClick={() => setArchived(true)}>
              Confirm archive
            </button>
            <button onClick={() => setConfirmingArchive(false)}>Cancel</button>
          </>
        ) : (
          <button onClick={() => setConfirmingArchive(true)}>Archive</button>
        )}
      </div>
      <p className="meta">
        {patient.birth_year ?? "?"} · {patient.sex ?? "?"} · {patient.phone ?? ""} ·{" "}
        {patient.address ?? ""}
      </p>
      {(patient.allergies || patient.medical_history) && (
        <section className="alert-allergy">
          {patient.allergies && (
            <p>
              <strong>Allergies:</strong> {patient.allergies}
            </p>
          )}
          {patient.medical_history && (
            <p>
              <strong>History:</strong> {patient.medical_history}
            </p>
          )}
        </section>
      )}

      {mode.name === "view" ? (
        <div className="actions">
          <button className="btn-primary" onClick={() => setMode({ name: "new" })}>
            New visit
          </button>
        </div>
      ) : (
        <VisitForm
          initial={mode.name === "edit" ? mode.visit : undefined}
          onSubmit={save}
          onCancel={() => setMode({ name: "view" })}
        />
      )}

      <h2>Visits</h2>
      {patient.visits.length === 0 && <p>No visits yet.</p>}
      {patient.visits.map((v) => (
        <article key={v.id}>
          <h3>{v.visited_at.slice(0, 10)}</h3>
          <p>
            {v.symptoms} {v.diagnosis && `→ ${v.diagnosis}`}
          </p>
          <ul>
            {v.items.map((i) => (
              <li key={i.id}>
                {i.drug_name} — {i.dosage ?? ""} × {i.days} days
              </li>
            ))}
          </ul>
          <p className="meta">
            Fee {v.fee} · Paid {v.paid_amount}
            {v.paid_amount < v.fee ? ` · Owed ${v.fee - v.paid_amount}` : ""}
          </p>
          <div className="actions">
            <button onClick={() => setMode({ name: "edit", visit: v })}>Edit</button>
            <button className="btn-danger" onClick={() => remove(v.id)}>
              Delete
            </button>
          </div>
        </article>
      ))}
    </main>
  );
}
