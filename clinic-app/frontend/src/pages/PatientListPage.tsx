import { useCallback, useEffect, useState, type FormEvent } from "react";
import { createPatient, listPatients } from "../api";
import FollowUps from "../components/FollowUps";
import type { Patient } from "../types";

interface Props {
  onOpen: (id: number) => void;
  onRevenue: () => void;
}

export default function PatientListPage({ onOpen, onRevenue }: Props) {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [query, setQuery] = useState("");
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");

  const [showArchived, setShowArchived] = useState(false);

  const load = useCallback(() => {
    listPatients(query.trim() || undefined, showArchived).then(setPatients);
  }, [query, showArchived]);

  useEffect(load, [load]);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    const full_name = name.trim();
    if (!full_name) return;
    const trimmedPhone = phone.trim();
    await createPatient(trimmedPhone ? { full_name, phone: trimmedPhone } : { full_name });
    setName("");
    setPhone("");
    load();
  };

  return (
    <main>
      <h1>Patients</h1>
      <div className="actions">
        <button onClick={onRevenue}>Revenue</button>
      </div>

      <FollowUps onOpen={onOpen} />

      <label>
        Search
        <input value={query} onChange={(e) => setQuery(e.target.value)} />
      </label>
      <label>
        <input
          type="checkbox"
          checked={showArchived}
          onChange={(e) => setShowArchived(e.target.checked)}
        />
        Show archived
      </label>

      <form onSubmit={submit}>
        <label>
          Full name
          <input value={name} onChange={(e) => setName(e.target.value)} />
        </label>
        <label>
          Phone
          <input value={phone} onChange={(e) => setPhone(e.target.value)} />
        </label>
        <button type="submit">Add patient</button>
      </form>

      {patients.length === 0 ? (
        <p>No patients yet.</p>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Birth year</th>
                <th>Phone</th>
                <th>Last visit</th>
              </tr>
            </thead>
            <tbody>
              {patients.map((p) => (
                <tr key={p.id}>
                  <td>
                    <a
                      href="#"
                      onClick={(e) => {
                        e.preventDefault();
                        onOpen(p.id);
                      }}
                    >
                      {p.full_name}
                    </a>
                    {p.is_archived && (
                      <>
                        {" "}
                        <span className="meta">Archived</span>
                      </>
                    )}
                  </td>
                  <td>{p.birth_year ?? ""}</td>
                  <td>{p.phone ?? ""}</td>
                  <td>{p.last_visit_date ?? ""}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </main>
  );
}
