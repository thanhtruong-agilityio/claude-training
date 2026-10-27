import { act, render, screen } from "@testing-library/react";
import FollowUps from "../components/FollowUps";

// Real api.ts with a stubbed fetch: proves nothing from the response body
// reaches the page or the console. Fake data only.
const SECRET_NAME = "Nguyen Van Secret";

beforeEach(() => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ detail: `error for ${SECRET_NAME}` }), {
        status: 500,
        headers: { "Content-Type": "application/json" },
      }),
    ),
  );
});

afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

async function showOn500() {
  await act(async () => {
    render(<FollowUps onOpen={vi.fn()} />);
  });
}

test("T16-13 a 500 with a patient name in the body shows only the fixed message", async () => {
  await showOn500();
  expect(screen.getByText("Could not load follow-ups")).toBeInTheDocument();
  expect(screen.getByRole("button", { name: "Try again" })).toBeInTheDocument();
  expect(document.body.textContent).not.toContain(SECRET_NAME);
});

test("T16-14 nothing from the response body is written to the console", async () => {
  const spies = [
    vi.spyOn(console, "log").mockImplementation(() => {}),
    vi.spyOn(console, "error").mockImplementation(() => {}),
    vi.spyOn(console, "warn").mockImplementation(() => {}),
  ];
  await showOn500();
  // The page must have reached the error state, otherwise the check proves nothing.
  expect(screen.getByText("Could not load follow-ups")).toBeInTheDocument();
  for (const spy of spies) {
    expect(JSON.stringify(spy.mock.calls)).not.toContain(SECRET_NAME);
  }
});
