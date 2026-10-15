import { useState } from "react";
import PatientListPage from "./pages/PatientListPage";

export type View =
  | { name: "patients" }
  | { name: "patient"; id: number }
  | { name: "revenue" };

export default function App() {
  const [view, setView] = useState<View>({ name: "patients" });

  return (
    <PatientListPage
      onOpen={(id) => setView({ name: "patient", id })}
      onRevenue={() => setView({ name: "revenue" })}
    />
  );
}
