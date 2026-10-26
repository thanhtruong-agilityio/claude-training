import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import PatientRecordPage from "../pages/PatientRecordPage";
import * as api from "../api";
import type { PatientDetail } from "../types";

vi.mock("../api");

const patient: PatientDetail = {
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
  visits: [],
};

beforeEach(() => {
  vi.mocked(api.getPatient).mockResolvedValue(patient);
  vi.mocked(api.updatePatient).mockReset();
});

test("archive needs a second click before it calls the API", async () => {
  vi.mocked(api.updatePatient).mockResolvedValue({ ...patient, is_archived: true });
  render(<PatientRecordPage id={1} onBack={() => {}} />);
  fireEvent.click(await screen.findByText("Archive"));
  expect(api.updatePatient).not.toHaveBeenCalled();
  fireEvent.click(screen.getByText("Confirm archive"));
  await waitFor(() => expect(api.updatePatient).toHaveBeenCalledWith(1, { is_archived: true }));
});

test("cancelling the archive confirmation does not call the API", async () => {
  render(<PatientRecordPage id={1} onBack={() => {}} />);
  fireEvent.click(await screen.findByText("Archive"));
  fireEvent.click(screen.getByText("Cancel"));
  expect(screen.getByText("Archive")).toBeInTheDocument();
  expect(api.updatePatient).not.toHaveBeenCalled();
});

test("an archived patient shows a badge and can be unarchived", async () => {
  vi.mocked(api.getPatient).mockResolvedValue({ ...patient, is_archived: true });
  vi.mocked(api.updatePatient).mockResolvedValue(patient);
  render(<PatientRecordPage id={1} onBack={() => {}} />);
  expect(await screen.findByText("Archived")).toBeInTheDocument();
  fireEvent.click(screen.getByText("Unarchive"));
  await waitFor(() => expect(api.updatePatient).toHaveBeenCalledWith(1, { is_archived: false }));
});
