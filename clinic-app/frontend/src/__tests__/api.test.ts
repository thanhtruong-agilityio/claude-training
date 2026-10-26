import { afterEach, expect, test, vi } from "vitest";
import { listPatients, updatePatient } from "../api";

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
  expect(JSON.parse(init.body)).toEqual({ q: "Zzyzx 0999123456", include_archived: false });
});

test("search can include archived patients", async () => {
  const fetchMock = stubFetch();
  await listPatients("van", true);
  expect(JSON.parse(fetchMock.mock.calls[0][1].body)).toEqual({ q: "van", include_archived: true });
});

test("plain list can include archived patients", async () => {
  const fetchMock = stubFetch();
  await listPatients(undefined, true);
  expect(fetchMock.mock.calls[0][0]).toBe("/api/patients?include_archived=true");
});

test("updatePatient sends a PATCH with the archive flag", async () => {
  const fetchMock = stubFetch();
  await updatePatient(7, { is_archived: true });
  const [url, init] = fetchMock.mock.calls[0];
  expect(url).toBe("/api/patients/7");
  expect(init.method).toBe("PATCH");
  expect(JSON.parse(init.body)).toEqual({ is_archived: true });
});

test("plain list uses GET /patients with no query string", async () => {
  const fetchMock = stubFetch();
  await listPatients();
  expect(fetchMock.mock.calls[0][0]).toBe("/api/patients");
  expect(fetchMock.mock.calls[0][1]?.method).toBeUndefined();
});
