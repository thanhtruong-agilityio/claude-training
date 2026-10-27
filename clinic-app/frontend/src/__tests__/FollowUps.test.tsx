import { act, fireEvent, render, screen, within } from "@testing-library/react";
import FollowUps from "../components/FollowUps";
import * as api from "../api";
import type { DueFollowUp, DueFollowUps } from "../types";

vi.mock("../api");

function item(overrides: Partial<DueFollowUp> = {}): DueFollowUp {
  return {
    patient_id: 1,
    full_name: "Nguyen Van A",
    phone: "0900000001",
    follow_up_date: "2026-10-20",
    days_overdue: 7,
    ...overrides,
  };
}

async function show(items: DueFollowUp[], total = items.length, onOpen = vi.fn()) {
  const data: DueFollowUps = { total, items };
  vi.mocked(api.getDueFollowUps).mockResolvedValue(data);
  await act(async () => {
    render(<FollowUps onOpen={onOpen} />);
  });
  return onOpen;
}

// Body rows only (the first row is the header).
const bodyRows = () => screen.getAllByRole("row").slice(1);

test("T15-01 shows heading and one row per item for 3 items", async () => {
  await show([
    item({ patient_id: 1, full_name: "Nguyen Van A" }),
    item({ patient_id: 2, full_name: "Tran Thi B" }),
    item({ patient_id: 3, full_name: "Le Van C" }),
  ]);
  expect(screen.getByText("3 patients to call")).toBeInTheDocument();
  expect(bodyRows()).toHaveLength(3);
});

test("T15-02 uses the singular heading for 1 item", async () => {
  await show([item()]);
  expect(screen.getByText("1 patient to call")).toBeInTheDocument();
  expect(screen.queryByText("1 patients to call")).not.toBeInTheDocument();
});

test("T15-03 row shows name, phone, date and days overdue", async () => {
  await show([item()]);
  const row = within(bodyRows()[0]);
  expect(row.getByText("Nguyen Van A")).toBeInTheDocument();
  expect(row.getByText("0900000001")).toBeInTheDocument();
  expect(row.getByText("2026-10-20")).toBeInTheDocument();
  expect(row.getByText("7 days overdue")).toBeInTheDocument();
});

test("T15-04 days_overdue 0 shows Today, not 0 days overdue", async () => {
  await show([item({ days_overdue: 0 })]);
  expect(screen.getByText("Today")).toBeInTheDocument();
  expect(screen.queryByText("0 days overdue")).not.toBeInTheDocument();
});

test("T15-05 days_overdue 1 shows 1 day overdue", async () => {
  await show([item({ days_overdue: 1 })]);
  expect(screen.getByText("1 day overdue")).toBeInTheDocument();
});

test("T15-06 days_overdue 2 shows 2 days overdue", async () => {
  await show([item({ days_overdue: 2 })]);
  expect(screen.getByText("2 days overdue")).toBeInTheDocument();
});

test("T15-07 null phone gives an empty phone cell and no null text", async () => {
  await show([item({ phone: null })]);
  const cells = within(bodyRows()[0]).getAllByRole("cell");
  expect(cells[1]).toHaveTextContent(/^$/);
  expect(screen.queryByText(/null/i)).not.toBeInTheDocument();
  expect(screen.queryByText(/undefined/i)).not.toBeInTheDocument();
});

test("T15-08 clicking the name of the second row opens that patient", async () => {
  const onOpen = await show([
    item({ patient_id: 11, full_name: "Nguyen Van A" }),
    item({ patient_id: 22, full_name: "Tran Thi B" }),
  ]);
  fireEvent.click(screen.getByRole("link", { name: "Tran Thi B" }));
  expect(onOpen).toHaveBeenCalledTimes(1);
  expect(onOpen).toHaveBeenCalledWith(22);
});

test("T15-09 clicking the phone or the date opens nothing", async () => {
  const onOpen = await show([item()]);
  fireEvent.click(screen.getByText("0900000001"));
  fireEvent.click(screen.getByText("2026-10-20"));
  expect(onOpen).not.toHaveBeenCalled();
});

test("T15-10 keeps the order returned by the API", async () => {
  await show([
    // Not sorted by name, id, days overdue or date, so any sort in the component fails.
    item({ patient_id: 2, full_name: "Bui Thi B", days_overdue: 3, follow_up_date: "2026-10-24" }),
    item({ patient_id: 1, full_name: "An Van A", days_overdue: 9, follow_up_date: "2026-10-18" }),
    item({ patient_id: 3, full_name: "Cao Van C", days_overdue: 1, follow_up_date: "2026-10-26" }),
  ]);
  const names = bodyRows().map((r) => within(r).getAllByRole("cell")[0].textContent);
  expect(names).toEqual(["Bui Thi B", "An Van A", "Cao Van C"]);
});

test("T15-11 the old Follow-ups today block is gone", async () => {
  await show([item()]);
  expect(screen.getByText("Nguyen Van A")).toBeInTheDocument();
  expect(screen.queryByText("Follow-ups today")).not.toBeInTheDocument();
});

test("T15-12 heading uses total from the response", async () => {
  await show([item()], 5);
  expect(screen.getByText("5 patients to call")).toBeInTheDocument();
});

// T15-14: jsdom has no layout, so this only proves the 80-character name is
// rendered in its row. Wrapping and no horizontal scroll need a manual browser check.
test("T15-14 renders an 80-character name in its row", async () => {
  const longName = "Nguyen Van Anh ".repeat(6).slice(0, 80);
  expect(longName).toHaveLength(80);
  await show([item({ full_name: longName })]);
  expect(within(bodyRows()[0]).getByText(longName)).toBeInTheDocument();
});

test("T15-15 days_overdue 30 shows 30 days overdue", async () => {
  await show([item({ days_overdue: 30 })]);
  expect(screen.getByText("30 days overdue")).toBeInTheDocument();
});

test("T15-16 total 0 shows no heading", async () => {
  await show([], 0);
  expect(screen.queryByText(/^\d+ patients? to call$/)).not.toBeInTheDocument();
});

// ---- Ticket 16: loading, empty and error states ----

const LOADING = "Loading follow-ups...";
const EMPTY = "No patients to call";
const ERROR = "Could not load follow-ups";
const HEADING = /^\d+ patients? to call$/;

function pending<T>() {
  let resolve!: (v: T) => void;
  let reject!: (e: Error) => void;
  const promise = new Promise<T>((res, rej) => {
    resolve = res;
    reject = rej;
  });
  return { promise, resolve, reject };
}

async function showFailing(error: Error) {
  vi.mocked(api.getDueFollowUps).mockRejectedValueOnce(error);
  await act(async () => {
    render(<FollowUps onOpen={vi.fn()} />);
  });
}

beforeEach(() => {
  vi.mocked(api.getDueFollowUps).mockReset();
});

test("T16-01 pending request shows loading text, no heading, no rows", async () => {
  vi.mocked(api.getDueFollowUps).mockReturnValue(pending<DueFollowUps>().promise);
  await act(async () => {
    render(<FollowUps onOpen={vi.fn()} />);
  });
  expect(screen.getByText(LOADING)).toBeInTheDocument();
  expect(screen.queryByText(HEADING)).not.toBeInTheDocument();
  expect(screen.queryAllByRole("row")).toHaveLength(0);
});

test("T16-02 loading text goes away when the request succeeds with items", async () => {
  const p = pending<DueFollowUps>();
  vi.mocked(api.getDueFollowUps).mockReturnValue(p.promise);
  await act(async () => {
    render(<FollowUps onOpen={vi.fn()} />);
  });
  expect(screen.getByText(LOADING)).toBeInTheDocument();
  await act(async () => {
    p.resolve({ total: 1, items: [item()] });
  });
  expect(screen.queryByText(LOADING)).not.toBeInTheDocument();
  expect(screen.getByText("1 patient to call")).toBeInTheDocument();
  expect(bodyRows()).toHaveLength(1);
});

test("T16-03 total 0 shows the empty text and the section stays visible", async () => {
  await show([], 0);
  expect(screen.getByText(EMPTY)).toBeInTheDocument();
  expect(screen.queryByText(LOADING)).not.toBeInTheDocument();
  expect(screen.getByText(EMPTY).closest("section")).not.toBeNull();
});

test("T16-04 total 0 shows no rows and no heading", async () => {
  await show([], 0);
  expect(screen.queryAllByRole("row")).toHaveLength(0);
  expect(screen.queryByText(HEADING)).not.toBeInTheDocument();
});

test("T16-05 a 500 shows the error text and Try again", async () => {
  await showFailing(new Error("Request failed: 500"));
  expect(screen.getByText(ERROR)).toBeInTheDocument();
  expect(screen.getByRole("button", { name: "Try again" })).toBeInTheDocument();
  expect(screen.queryByText(LOADING)).not.toBeInTheDocument();
});

test("T16-06 a 422 shows the same error text and Try again", async () => {
  await showFailing(new Error("Request failed: 422"));
  expect(screen.getByText(ERROR)).toBeInTheDocument();
  expect(screen.getByRole("button", { name: "Try again" })).toBeInTheDocument();
});

test("T16-07 a network failure shows the same error text and Try again", async () => {
  await showFailing(new TypeError("Failed to fetch"));
  expect(screen.getByText(ERROR)).toBeInTheDocument();
  expect(screen.getByRole("button", { name: "Try again" })).toBeInTheDocument();
});

test("T16-08 Try again succeeds with 2 items: list shows, error text gone", async () => {
  await showFailing(new Error("Request failed: 500"));
  vi.mocked(api.getDueFollowUps).mockResolvedValueOnce({
    total: 2,
    items: [item({ patient_id: 1 }), item({ patient_id: 2, full_name: "Tran Thi B" })],
  });
  await act(async () => {
    fireEvent.click(screen.getByRole("button", { name: "Try again" }));
  });
  expect(screen.queryByText(ERROR)).not.toBeInTheDocument();
  expect(screen.getByText("2 patients to call")).toBeInTheDocument();
  expect(bodyRows()).toHaveLength(2);
});

test("T16-09 Try again succeeds with total 0: shows the empty text", async () => {
  await showFailing(new Error("Request failed: 500"));
  vi.mocked(api.getDueFollowUps).mockResolvedValueOnce({ total: 0, items: [] });
  await act(async () => {
    fireEvent.click(screen.getByRole("button", { name: "Try again" }));
  });
  expect(screen.getByText(EMPTY)).toBeInTheDocument();
  expect(screen.queryByText(ERROR)).not.toBeInTheDocument();
});

test("T16-10 Try again in progress shows loading and a second click sends no second request", async () => {
  await showFailing(new Error("Request failed: 500"));
  vi.mocked(api.getDueFollowUps).mockReturnValueOnce(pending<DueFollowUps>().promise);
  const button = screen.getByRole("button", { name: "Try again" });
  await act(async () => {
    fireEvent.click(button);
    fireEvent.click(button); // same element, before any re-render
  });
  expect(screen.getByText(LOADING)).toBeInTheDocument();
  expect(screen.queryByRole("button", { name: "Try again" })).not.toBeInTheDocument();
  expect(api.getDueFollowUps).toHaveBeenCalledTimes(2); // mount + one retry
});

test("T16-11 Try again fails again: error text and Try again are back", async () => {
  await showFailing(new Error("Request failed: 500"));
  vi.mocked(api.getDueFollowUps).mockRejectedValueOnce(new Error("Request failed: 500"));
  await act(async () => {
    fireEvent.click(screen.getByRole("button", { name: "Try again" }));
  });
  expect(screen.getByText(ERROR)).toBeInTheDocument();
  expect(screen.getByRole("button", { name: "Try again" })).toBeInTheDocument();
  expect(screen.queryByText(LOADING)).not.toBeInTheDocument();
});
