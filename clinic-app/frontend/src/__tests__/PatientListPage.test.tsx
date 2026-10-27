import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import PatientListPage from "../pages/PatientListPage";
import * as api from "../api";

vi.mock("../api");

const patients = [
  {
    id: 1,
    full_name: "Nguyen Van A",
    birth_year: 1980,
    sex: "male",
    phone: "0900000001",
    address: null,
    allergies: null,
    medical_history: null,
    is_archived: false,
    created_at: "2026-01-01T00:00:00",
    last_visit_date: "2026-03-01",
  },
];

beforeEach(() => {
  vi.mocked(api.listPatients).mockResolvedValue(patients);
  vi.mocked(api.getDueFollowUps).mockResolvedValue({ total: 0, items: [] });
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
  await waitFor(() => expect(api.listPatients).toHaveBeenLastCalledWith("van", false));
});

test("show archived refetches with archived included and marks them", async () => {
  const archived = { ...patients[0], id: 2, full_name: "Tran B", is_archived: true };
  vi.mocked(api.listPatients).mockImplementation(async (_q, includeArchived) =>
    includeArchived ? [patients[0], archived] : [patients[0]],
  );
  render(<PatientListPage onOpen={() => {}} onRevenue={() => {}} />);
  await screen.findByText("Nguyen Van A");
  expect(screen.queryByText("Archived")).not.toBeInTheDocument();
  fireEvent.click(screen.getByLabelText("Show archived"));
  await waitFor(() => expect(api.listPatients).toHaveBeenLastCalledWith(undefined, true));
  expect(await screen.findByText("Archived")).toBeInTheDocument();
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

test("T15-13 shows the due list together with the search box and add-patient form", async () => {
  vi.mocked(api.getDueFollowUps).mockResolvedValue({
    total: 1,
    items: [
      {
        patient_id: 5,
        full_name: "Pham Thi D",
        phone: null,
        follow_up_date: "2026-10-20",
        days_overdue: 7,
      },
    ],
  });
  render(<PatientListPage onOpen={() => {}} onRevenue={() => {}} />);
  expect(await screen.findByText("1 patient to call")).toBeInTheDocument();
  expect(screen.queryByText("Follow-ups today")).not.toBeInTheDocument();
  expect(screen.getByLabelText("Search")).toBeInTheDocument();
  expect(screen.getByLabelText("Full name")).toBeInTheDocument();
  expect(screen.getByText("Add patient")).toBeInTheDocument();
});
