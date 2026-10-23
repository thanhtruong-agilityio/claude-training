import { useEffect, useState } from "react";
import { getRevenue } from "../api";
import type { Revenue } from "../types";

// YYYY-MM-DD in clinic time, same as the backend, whatever the browser's timezone
const today = () => new Date().toLocaleDateString("sv-SE", { timeZone: "Asia/Ho_Chi_Minh" });

export default function RevenuePage({ onBack }: { onBack: () => void }) {
  const [from, setFrom] = useState(today());
  const [to, setTo] = useState(today());
  const [revenue, setRevenue] = useState<Revenue | null>(null);

  useEffect(() => {
    if (!from || !to || from > to) return;
    getRevenue(from, to).then(setRevenue);
  }, [from, to]);

  return (
    <main>
      <button onClick={onBack}>Back</button>
      <h1>Revenue</h1>
      <label>
        From <input type="date" value={from} onChange={(e) => setFrom(e.target.value)} />
      </label>
      <label>
        To <input type="date" value={to} onChange={(e) => setTo(e.target.value)} />
      </label>
      {from > to && <p role="alert">From must not be after To</p>}
      {revenue && (
        <ul className="stats">
          <li>Visits: {revenue.visit_count}</li>
          <li className="collected">Collected: {revenue.collected}</li>
          <li className="owed">Owed: {revenue.owed}</li>
        </ul>
      )}
    </main>
  );
}
