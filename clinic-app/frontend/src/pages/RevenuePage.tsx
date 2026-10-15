import { useEffect, useState } from "react";
import { getRevenue } from "../api";
import type { Revenue } from "../types";

const today = () => new Date().toLocaleDateString("sv-SE"); // YYYY-MM-DD, local time

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
      <label>From <input type="date" value={from} onChange={(e) => setFrom(e.target.value)} /></label>
      <label>To <input type="date" value={to} onChange={(e) => setTo(e.target.value)} /></label>
      {from > to && <p role="alert">From must not be after To</p>}
      {revenue && (
        <ul>
          <li>Visits: {revenue.visit_count}</li>
          <li>Collected: {revenue.collected}</li>
          <li>Owed: {revenue.owed}</li>
        </ul>
      )}
    </main>
  );
}
