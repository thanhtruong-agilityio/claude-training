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
  fireEvent.click(screen.getByText("Tran Thi B"));
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
    item({ patient_id: 2, full_name: "Bui Thi B" }),
    item({ patient_id: 1, full_name: "An Van A" }),
    item({ patient_id: 3, full_name: "Cao Van C" }),
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
  expect(screen.queryByText(/to call/)).not.toBeInTheDocument();
});
