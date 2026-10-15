import { useState } from "react";
import PatientListPage from "./pages/PatientListPage";
import PatientRecordPage from "./pages/PatientRecordPage";

export type View =
  | { name: "patients" }
  | { name: "patient"; id: number }
  | { name: "revenue" };

export default function App() {
  const [view, setView] = useState<View>({ name: "patients" });

  if (view.name === "patient") {
    return <PatientRecordPage id={view.id} onBack={() => setView({ name: "patients" })} />;
  }

  return (
    <PatientListPage
      onOpen={(id) => setView({ name: "patient", id })}
      onRevenue={() => setView({ name: "revenue" })}
    />
  );
}
