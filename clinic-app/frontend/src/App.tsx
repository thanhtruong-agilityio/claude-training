import { useState } from "react";
import PatientListPage from "./pages/PatientListPage";
import PatientRecordPage from "./pages/PatientRecordPage";
import RevenuePage from "./pages/RevenuePage";

export type View =
  | { name: "patients" }
  | { name: "patient"; id: number }
  | { name: "revenue" };

export default function App() {
  const [view, setView] = useState<View>({ name: "patients" });

  const goHome = () => setView({ name: "patients" });

  let page;
  if (view.name === "patient") {
    page = <PatientRecordPage id={view.id} onBack={goHome} />;
  } else if (view.name === "revenue") {
    page = <RevenuePage onBack={goHome} />;
  } else {
    page = (
      <PatientListPage
        onOpen={(id) => setView({ name: "patient", id })}
        onRevenue={() => setView({ name: "revenue" })}
      />
    );
  }

  return (
    <>
      <nav className="nav">
        <span className="brand">Clinic</span>
      </nav>
      {page}
    </>
  );
}
