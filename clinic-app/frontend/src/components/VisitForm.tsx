import { useState, type FormEvent } from "react";
import type { Visit, VisitPayload } from "../types";

interface Row {
  drug_name: string;
  dosage: string;
  days: string;
  note: string;
}

interface Props {
  initial?: Visit;
  onSubmit: (data: VisitPayload) => void;
  onCancel: () => void;
}

const emptyRow = (): Row => ({ drug_name: "", dosage: "", days: "1", note: "" });
const orNull = (s: string) => (s.trim() ? s.trim() : null);
const numOrNull = (s: string) => (s.trim() ? Number(s) : null);

export default function VisitForm({ initial, onSubmit, onCancel }: Props) {
  const [symptoms, setSymptoms] = useState(initial?.symptoms ?? "");
  const [diagnosis, setDiagnosis] = useState(initial?.diagnosis ?? "");
  const [notes, setNotes] = useState(initial?.notes ?? "");
  const [weight, setWeight] = useState(String(initial?.weight_kg ?? ""));
  const [temp, setTemp] = useState(String(initial?.temperature_c ?? ""));
  const [bp, setBp] = useState(initial?.blood_pressure ?? "");
  const [fee, setFee] = useState(String(initial?.fee ?? ""));
  const [paid, setPaid] = useState(String(initial?.paid_amount ?? ""));
  const [followUp, setFollowUp] = useState(initial?.follow_up_date ?? "");
  const [rows, setRows] = useState<Row[]>(
    initial?.items.length
      ? initial.items.map((i) => ({
          drug_name: i.drug_name,
          dosage: i.dosage ?? "",
          days: String(i.days),
          note: i.note ?? "",
        }))
      : [emptyRow()],
  );
  const [error, setError] = useState("");

  const setRow = (index: number, patch: Partial<Row>) =>
    setRows((rs) => rs.map((r, i) => (i === index ? { ...r, ...patch } : r)));

  const submit = (e: FormEvent) => {
    e.preventDefault();
    const feeValue = Number(fee || 0);
    const paidValue = Number(paid || 0);
    if (paidValue > feeValue) {
      setError("Paid cannot exceed fee");
      return;
    }
    setError("");
    onSubmit({
      ...(initial ? { visited_at: initial.visited_at } : {}),
      symptoms: orNull(symptoms),
      diagnosis: orNull(diagnosis),
      notes: orNull(notes),
      weight_kg: numOrNull(weight),
      temperature_c: numOrNull(temp),
      blood_pressure: orNull(bp),
      fee: feeValue,
      paid_amount: paidValue,
      follow_up_date: followUp || null,
      items: rows
        .filter((r) => r.drug_name.trim())
        .map((r) => ({
          drug_name: r.drug_name.trim(),
          dosage: orNull(r.dosage),
          days: Number(r.days || 1),
          note: orNull(r.note),
        })),
    });
  };

  return (
    <form onSubmit={submit}>
      <label>
        Symptoms <textarea value={symptoms} onChange={(e) => setSymptoms(e.target.value)} />
      </label>
      <label>
        Diagnosis <textarea value={diagnosis} onChange={(e) => setDiagnosis(e.target.value)} />
      </label>
      <label>
        Notes <textarea value={notes} onChange={(e) => setNotes(e.target.value)} />
      </label>

      <label>
        Weight (kg) <input value={weight} onChange={(e) => setWeight(e.target.value)} />
      </label>
      <label>
        Temperature (°C) <input value={temp} onChange={(e) => setTemp(e.target.value)} />
      </label>
      <label>
        Blood pressure <input value={bp} onChange={(e) => setBp(e.target.value)} />
      </label>

      <h3>Prescription</h3>
      {rows.map((row, i) => (
        <div key={i} className="row">
          <label>
            Drug name{" "}
            <input
              value={row.drug_name}
              onChange={(e) => setRow(i, { drug_name: e.target.value })}
            />
          </label>
          <label>
            Dosage{" "}
            <input value={row.dosage} onChange={(e) => setRow(i, { dosage: e.target.value })} />
          </label>
          <label>
            Days <input value={row.days} onChange={(e) => setRow(i, { days: e.target.value })} />
          </label>
          <label>
            Drug note{" "}
            <input value={row.note} onChange={(e) => setRow(i, { note: e.target.value })} />
          </label>
          <button type="button" onClick={() => setRows((rs) => rs.filter((_, j) => j !== i))}>
            Remove
          </button>
        </div>
      ))}
      <button type="button" onClick={() => setRows((rs) => [...rs, emptyRow()])}>
        Add drug
      </button>

      <label>
        Fee <input value={fee} onChange={(e) => setFee(e.target.value)} />
      </label>
      <label>
        Paid <input value={paid} onChange={(e) => setPaid(e.target.value)} />
      </label>
      <label>
        Follow-up date{" "}
        <input type="date" value={followUp} onChange={(e) => setFollowUp(e.target.value)} />
      </label>

      {error && <p role="alert">{error}</p>}
      <button type="submit">Save visit</button>
      <button type="button" onClick={onCancel}>
        Cancel
      </button>
    </form>
  );
}
