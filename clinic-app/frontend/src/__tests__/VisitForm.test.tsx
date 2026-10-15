import { fireEvent, render, screen } from "@testing-library/react";
import VisitForm from "../components/VisitForm";

function fill(label: string, value: string, index = 0) {
  fireEvent.change(screen.getAllByLabelText(label)[index], { target: { value } });
}

test("adds and removes prescription rows", () => {
  render(<VisitForm onSubmit={() => {}} onCancel={() => {}} />);
  expect(screen.getAllByLabelText("Drug name")).toHaveLength(1);
  fireEvent.click(screen.getByText("Add drug"));
  expect(screen.getAllByLabelText("Drug name")).toHaveLength(2);
  fireEvent.click(screen.getAllByText("Remove")[0]);
  expect(screen.getAllByLabelText("Drug name")).toHaveLength(1);
});

test("submits one payload and drops blank prescription rows", () => {
  const onSubmit = vi.fn();
  render(<VisitForm onSubmit={onSubmit} onCancel={() => {}} />);
  fill("Symptoms", "  cough ");
  fill("Fee", "100000");
  fill("Paid", "50000");
  fill("Drug name", " Paracetamol ");
  fill("Days", "3");
  fireEvent.click(screen.getByText("Add drug"));
  fill("Drug name", "   ", 1);
  fireEvent.click(screen.getByText("Save visit"));

  expect(onSubmit).toHaveBeenCalledTimes(1);
  const payload = onSubmit.mock.calls[0][0];
  expect(payload.symptoms).toBe("cough");
  expect(payload.fee).toBe(100000);
  expect(payload.paid_amount).toBe(50000);
  expect(payload.items).toEqual([
    { drug_name: "Paracetamol", dosage: null, days: 3, note: null },
  ]);
});

test("paid above fee shows an error and does not submit", () => {
  const onSubmit = vi.fn();
  render(<VisitForm onSubmit={onSubmit} onCancel={() => {}} />);
  fill("Fee", "100");
  fill("Paid", "200");
  fireEvent.click(screen.getByText("Save visit"));
  expect(screen.getByText("Paid cannot exceed fee")).toBeInTheDocument();
  expect(onSubmit).not.toHaveBeenCalled();
});

test("edit keeps the original visit time", () => {
  const onSubmit = vi.fn();
  const initial = {
    id: 1, patient_id: 1, visited_at: "2026-03-01T09:00:00", symptoms: "old",
    diagnosis: null, notes: null, weight_kg: null, temperature_c: null,
    blood_pressure: null, fee: 100, paid_amount: 0, follow_up_date: null,
    deleted_at: null, items: [{ id: 5, drug_name: "A", dosage: null, days: 2, note: null }],
  };
  render(<VisitForm initial={initial} onSubmit={onSubmit} onCancel={() => {}} />);
  fill("Paid", "100");
  fireEvent.click(screen.getByText("Save visit"));
  expect(onSubmit.mock.calls[0][0].visited_at).toBe("2026-03-01T09:00:00");
  expect(onSubmit.mock.calls[0][0].items[0].drug_name).toBe("A");
});
