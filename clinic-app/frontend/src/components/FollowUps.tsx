import { useCallback, useEffect, useRef, useState } from "react";
import { getDueFollowUps } from "../api";
import type { DueFollowUps } from "../types";

const TEXT = {
  loading: "Loading follow-ups...",
  empty: "No patients to call",
  error: "Could not load follow-ups",
  retry: "Try again",
};

function overdueLabel(days: number): string {
  if (days === 0) return "Today";
  if (days === 1) return "1 day overdue";
  return `${days} days overdue`;
}

export default function FollowUps({ onOpen }: { onOpen: (patientId: number) => void }) {
  const [status, setStatus] = useState<"loading" | "ready" | "error">("loading");
  const [data, setData] = useState<DueFollowUps | null>(null);
  const inFlight = useRef(false);

  const load = useCallback(() => {
    if (inFlight.current) return;
    inFlight.current = true;
    setStatus("loading");
    getDueFollowUps()
      .then((d) => {
        setData(d);
        setStatus("ready");
      })
      // The error is ignored on purpose: it must never be shown or logged.
      .catch(() => setStatus("error"))
      .finally(() => {
        inFlight.current = false;
      });
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  if (status === "loading") return <section>{TEXT.loading}</section>;
  if (status === "error" || !data)
    return (
      <section>
        <p>{TEXT.error}</p>
        <button type="button" onClick={load}>
          {TEXT.retry}
        </button>
      </section>
    );
  if (data.total === 0) return <section>{TEXT.empty}</section>;

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
                <td className="wrap-anywhere">
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
