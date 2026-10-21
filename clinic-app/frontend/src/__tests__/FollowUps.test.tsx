import { act, fireEvent, render, screen } from "@testing-library/react";
import FollowUps from "../components/FollowUps";
import * as api from "../api";

vi.mock("../api");

test("shows nothing when no follow-ups", async () => {
  vi.mocked(api.listFollowUps).mockResolvedValue([]);
  await act(async () => {
    render(<FollowUps onOpen={() => {}} />);
  });
  expect(screen.queryByText("Follow-ups today")).not.toBeInTheDocument();
});

test("lists follow-ups and opens the patient", async () => {
  vi.mocked(api.listFollowUps).mockResolvedValue([
    {
      visit_id: 7,
      patient_id: 3,
      full_name: "Tran B",
      phone: "0911",
      follow_up_date: "2026-05-01",
    },
  ]);
  const onOpen = vi.fn();
  render(<FollowUps onOpen={onOpen} />);
  expect(await screen.findByText("Follow-ups today")).toBeInTheDocument();
  fireEvent.click(screen.getByText("Tran B"));
  expect(onOpen).toHaveBeenCalledWith(3);
});
