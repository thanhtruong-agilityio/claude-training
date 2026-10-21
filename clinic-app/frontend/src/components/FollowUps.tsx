import { useEffect, useState } from "react";
import { listFollowUps } from "../api";
import type { FollowUp } from "../types";

export default function FollowUps({ onOpen }: { onOpen: (patientId: number) => void }) {
  const [rows, setRows] = useState<FollowUp[]>([]);

  useEffect(() => {
    listFollowUps().then(setRows);
  }, []);

  if (rows.length === 0) return null;

  return (
    <section>
      <h2>Follow-ups today</h2>
      <ul>
        {rows.map((r) => (
          <li key={r.visit_id}>
            <a
              href="#"
              onClick={(e) => {
                e.preventDefault();
                onOpen(r.patient_id);
              }}
            >
              {r.full_name}
            </a>{" "}
            {r.phone ?? ""}
          </li>
        ))}
      </ul>
    </section>
  );
}
