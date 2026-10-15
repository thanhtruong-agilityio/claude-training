import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import PatientListPage from "../pages/PatientListPage";
import * as api from "../api";

vi.mock("../api");

const patients = [
  {
    id: 1, full_name: "Nguyen Van A", birth_year: 1980, sex: "male",
    phone: "0900000001", address: null, allergies: null, medical_history: null,
    is_archived: false, created_at: "2026-01-01T00:00:00", last_visit_date: "2026-03-01",
  },
];

beforeEach(() => {
  vi.mocked(api.listPatients).mockResolvedValue(patients);
  vi.mocked(api.listFollowUps).mockResolvedValue([]);
  vi.mocked(api.createPatient).mockReset();
});

test("lists patients with last visit date", async () => {
  render(<PatientListPage onOpen={() => {}} onRevenue={() => {}} />);
  expect(await screen.findByText("Nguyen Van A")).toBeInTheDocument();
  expect(screen.getByText("2026-03-01")).toBeInTheDocument();
});

test("opens a patient on click", async () => {
  const onOpen = vi.fn();
  render(<PatientListPage onOpen={onOpen} onRevenue={() => {}} />);
  fireEvent.click(await screen.findByText("Nguyen Van A"));
  expect(onOpen).toHaveBeenCalledWith(1);
});

test("search refetches with the query", async () => {
  render(<PatientListPage onOpen={() => {}} onRevenue={() => {}} />);
  await screen.findByText("Nguyen Van A");
  fireEvent.change(screen.getByLabelText("Search"), { target: { value: "van" } });
  await waitFor(() => expect(api.listPatients).toHaveBeenLastCalledWith("van"));
});

test("blank name does not call the API", async () => {
  render(<PatientListPage onOpen={() => {}} onRevenue={() => {}} />);
  await screen.findByText("Nguyen Van A");
  fireEvent.change(screen.getByLabelText("Full name"), { target: { value: "   " } });
  fireEvent.click(screen.getByText("Add patient"));
  expect(api.createPatient).not.toHaveBeenCalled();
});

test("adds a patient with trimmed name and reloads", async () => {
  vi.mocked(api.createPatient).mockResolvedValue(patients[0]);
  render(<PatientListPage onOpen={() => {}} onRevenue={() => {}} />);
  await screen.findByText("Nguyen Van A");
  fireEvent.change(screen.getByLabelText("Full name"), { target: { value: "  Tran B  " } });
  fireEvent.change(screen.getByLabelText("Phone"), { target: { value: "0911" } });
  fireEvent.click(screen.getByText("Add patient"));
  await waitFor(() =>
    expect(api.createPatient).toHaveBeenCalledWith({ full_name: "Tran B", phone: "0911" }),
  );
});
