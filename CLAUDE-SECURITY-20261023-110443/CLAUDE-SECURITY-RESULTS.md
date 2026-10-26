# Claude Security results

Scan of `clinic-app` (scope `clinic-app` of the repository at `/Users/thanhtruong/asnet-project/project/claude-training/claude-training`, branch `training/day-11`, commit `920474b`), mode scan, medium effort, started 2026-10-23 11:04 UTC. Two findings survived verification: 1 MEDIUM and 1 LOW. Both describe the same root cause, an unauthenticated patient-data API with no Host or origin validation. The repository's working tree held uncommitted changes or untracked files; which ones is not recorded.

## Coverage

The scan was narrowed to `clinic-app` (59 tracked files) at the user's request; everything else in the repository was out of scope. Three components were examined:

- `backend-api`: `backend/app`, `backend/Dockerfile`, `backend/pyproject.toml`.
- `frontend-app`: the React sources, `index.html`, `vite.config.ts`, its Dockerfile and `package.json`.
- `deploy-and-tooling`: `docker-compose.yml`, `Makefile`, `clinic-app/.claude`, the docs, and the backend and frontend tests.

The run was sized by the 59 tracked files: about 3 components asked for (roughly 25 files each, at most 24 kept). 11 researchers were dispatched and all 11 returned. The memory-safety lens was not put to `backend-api` or `frontend-app`: the workflow decided from the language alone, before briefing, because it took the code to be all in managed languages. The panel took 1 verification run, and no candidate was lost or left unverified.

Deliberately not examined:

- `clinic-app/backend/.venv`: vendored third-party Python virtualenv, not project code.
- `clinic-app/frontend/node_modules`: third-party npm dependency tree, not project code.
- `clinic-app/backend/uv.lock` and `clinic-app/frontend/package-lock.json`: generated lockfiles.
- `docs`, `.claude`, `.github`, `exercises`: outside the requested scope (Markdown notes and repository config at the root).

Researchers' own account of what they did not read: `backend/tests` (test code, background), `backend/uv.lock`, and `clinic-app/backend/clinic.db` (the real patient database; access was denied and it was deliberately not read). Checked against the tracked files inside the components: of 52 files, 50 were read to a conclusion, 1 lies under a declared not-reached path, and 1 was accounted for by no researcher: `clinic-app/backend/app/__init__.py`. Nothing in the scan executed the repository's code.

## Findings

### F1 — Patient-data API published on :8000 with no authentication or Host validation; the localhost bind is the only access control (MEDIUM, confidence low)

**Impact.** Disclosure and modification of patient records (names, phones, symptoms, prescriptions, fees) by any web page the clinic user visits, plus access by any other local user or process on the machine.

**Where.** `clinic-app/docker-compose.yml:7` in `services.backend.ports` — CWE-306

**What.** The backend router handlers have no auth dependency, and `main.py` adds only `CORSMiddleware`, with no `TrustedHostMiddleware` or Host check. The compose file publishes the API on `127.0.0.1:8000`, and the project docs (`data-safety/SKILL.md:12`, the README) treat that bind as the sole protection. A web page the doctor opens can reach the port through DNS rebinding or, for body-less POSTs, plain cross-site requests. A rebound page is same-origin for the browser, so the CORS allow-list does not apply.

**Exploit scenario.** With `make up` running, the doctor visits `evil.example`. The attacker's DNS first returns the attacker's IP, then rebinds the name to `127.0.0.1`. The page's JavaScript calls `evil.example:8000/patients` and `/patients/{id}`, which uvicorn serves for any Host header. The attacker reads patient names, phones and prescriptions, and can POST, PATCH, PUT or DELETE records. The page can also fire a blind cross-site `POST /visits/{id}/restore`, which has no body and needs no preflight. The frontend dev server on `:5173` is not exposed this way, since the locked Vite 5.4.21 has the `allowedHosts` check; port 8000 is.

**Preconditions.**
- The stack is running via docker compose.
- The victim browses to an attacker-controlled page while it runs.
- The attacker's DNS rebinding is not filtered by the victim's resolver or browser.
- Alternatively, the attacker is a local user or process on the host.

**Fix.** Add real authentication, even a shared secret or token that the Vite proxy injects. At minimum, add Starlette `TrustedHostMiddleware` (allowed hosts `localhost`, `127.0.0.1` and the compose service name `backend`). Better still, do not publish port 8000 to the host at all, since the frontend reaches the backend over the compose network through the `/api` proxy.

**Verification.** 3/3 lens verifiers confirmed.

### F2 — No Host/origin validation lets a malicious web page reach the unauthenticated localhost API (DNS rebinding / cross-site simple requests) (LOW, confidence low)

**Impact.** Remote attackers can drive the local clinic API through the victim's browser, giving PHI disclosure and record tampering, if the browser's private-network and local-network access protections do not block it.

**Where.** `clinic-app/backend/app/main.py:16` in the module-level app setup — CWE-346

**What.** The API has no authentication and no `TrustedHostMiddleware`, so its only barrier against the doctor's own browser is the browser's same-origin policy. A page on an attacker-controlled hostname rebound to `127.0.0.1` would be same-origin with the backend and could read and write all PHI. CORS is not a server-side check, and no CSRF or Host check exists. This is the application-side view of the same root cause as F1.

**Exploit scenario.** The doctor visits a malicious page. (1) The page fires a body-less cross-site `POST http://localhost:8000/visits/N/restore`, which undeletes soft-deleted visits and needs no preflight. (2) With a DNS-rebinding hostname that resolves to `127.0.0.1`, the uvicorn app accepts any Host header, so the page becomes same-origin and can GET `/patients`, PATCH patients, and PUT or DELETE visits, and read the responses.

**Preconditions.**
- The victim browses to an attacker-controlled page while the clinic app is running.
- For the rebinding variant, the browser does not block public-to-loopback requests.
- For the CSRF variant, the attacker can guess sequential visit IDs.

**Fix.** Add `TrustedHostMiddleware(allowed_hosts=["localhost", "127.0.0.1", "backend"])` and require an auth token (custom header, or a cookie with SameSite) on all routes. JSON-body routes already require `Content-Type: application/json` (FastAPI's `strict_content_type` default in the locked 0.143.1), but body-less POST routes such as restore are not covered by that.

**Verification.** 3/3 lens verifiers confirmed.

## What was verified

Each candidate was reviewed by a three-voter panel (reachability, impact, defenses) in one verification run. F1 and F2 each survived 3 of 3 votes; the severities the panel gave were not lower than reported. A third candidate, the missing authentication on the endpoints taken alone, was refuted 0 of 3 as a finding because the shipped default publishes only on loopback and the project documents itself as a single-user local app. All 11 researchers returned, so the verification status covers every reading listed above. Every finding was derived from reading code; nothing was run and no exploit was demonstrated.
