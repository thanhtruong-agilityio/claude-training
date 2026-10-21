import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import RevenuePage from "../pages/RevenuePage";
import * as api from "../api";

vi.mock("../api");

test("shows totals for the chosen range", async () => {
  vi.mocked(api.getRevenue).mockResolvedValue({ visit_count: 2, collected: 150000, owed: 150000 });
  render(<RevenuePage onBack={() => {}} />);

  fireEvent.change(screen.getByLabelText("From"), { target: { value: "2026-05-01" } });
  fireEvent.change(screen.getByLabelText("To"), { target: { value: "2026-05-02" } });

  await waitFor(() => expect(api.getRevenue).toHaveBeenLastCalledWith("2026-05-01", "2026-05-02"));
  expect(await screen.findByText("Visits: 2")).toBeInTheDocument();
  expect(screen.getByText("Collected: 150000")).toBeInTheDocument();
  expect(screen.getByText("Owed: 150000")).toBeInTheDocument();
});
