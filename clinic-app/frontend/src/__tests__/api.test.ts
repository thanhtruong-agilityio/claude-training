import { afterEach, expect, test, vi } from "vitest";
import { listPatients } from "../api";

afterEach(() => vi.unstubAllGlobals());

function stubFetch() {
  const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => [] });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

test("search sends the term in a POST body, not the URL", async () => {
  const fetchMock = stubFetch();
  await listPatients("Zzyzx 0999123456");
  const [url, init] = fetchMock.mock.calls[0];
  expect(url).toBe("/api/patients/search");
  expect(url).not.toContain("Zzyzx");
  expect(init.method).toBe("POST");
  expect(JSON.parse(init.body)).toEqual({ q: "Zzyzx 0999123456" });
});

test("plain list uses GET /patients with no query string", async () => {
  const fetchMock = stubFetch();
  await listPatients();
  expect(fetchMock.mock.calls[0][0]).toBe("/api/patients");
  expect(fetchMock.mock.calls[0][1]?.method).toBeUndefined();
});
