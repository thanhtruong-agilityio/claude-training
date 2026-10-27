import { useEffect, useState } from "react";
import { getDueFollowUps } from "../api";
import type { DueFollowUps } from "../types";

function overdueLabel(days: number): string {
  if (days === 0) return "Today";
  if (days === 1) return "1 day overdue";
  return `${days} days overdue`;
}

export default function FollowUps({ onOpen }: { onOpen: (patientId: number) => void }) {
  const [data, setData] = useState<DueFollowUps | null>(null);

  useEffect(() => {
    getDueFollowUps().then(setData);
  }, []);

  if (!data || data.total === 0) return null;

  return (
    <section>
      <h2>{data.total === 1 ? "1 patient to call" : `${data.total} patients to call`}</h2>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Phone</th>
              <th>Follow-up date</th>
              <th>Overdue</th>
            </tr>
          </thead>
          <tbody>
            {data.items.map((r) => (
              <tr key={r.patient_id}>
                <td style={{ overflowWrap: "anywhere" }}>
                  <a
                    href="#"
                    onClick={(e) => {
                      e.preventDefault();
                      onOpen(r.patient_id);
                    }}
                  >
                    {r.full_name}
                  </a>
                </td>
                <td>{r.phone ?? ""}</td>
                <td>{r.follow_up_date}</td>
                <td>{overdueLabel(r.days_overdue)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
