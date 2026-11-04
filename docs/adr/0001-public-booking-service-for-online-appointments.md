# 0001. Public booking service for online appointments

Date: 2026-11-03
Status: Accepted (2026-11-03, ThanhTruong as product owner). Scope note: ticket 59 does not build this service; sync, hosting, auth and rate limiting are deferred to a later ticket, and the booking feature first ships inside the clinic app on `127.0.0.1`.

## Context

The online appointment booking spec (`docs/specs/2026-11-02-online-appointment-booking-design.md`, ticket 59) lets patients book a doctor's free slot from their own device. `clinic-app` today is single-user, has no login, and keeps every port bound to `127.0.0.1` (`clinic-app/CLAUDE.md`, `clinic-app/.claude/rules/security.md`, `docker-compose.yml`). The security scan already lists missing auth as a finding even for local use.

Alternatives considered:
- Local only, reception books on behalf of patients: smallest change, but it is not "online" for patients and changes the intent.
- Expose the whole app behind auth and TLS: largest change, reverses the security rules and exposes patient records.
- Separate public booking service: chosen.

Decided by ThanhTruong (lead, as product owner) on 2026-11-03.

## Decision

We add a separate, minimal public booking service (or endpoint set) for patients, with its own auth, rate limiting and hosting. It has no access to patient records, visits or revenue. The existing clinic app stays bound to `127.0.0.1`.

## Consequences

**Easier/Better:**
- Patient records and the no-login clinic app stay off the network.
- The public surface is small and can be reviewed on its own.

**Harder/Tradeoffs:**
- New attack surface, hosting and operations that the repo does not have today.
- Bookings must reach the clinic app (sync or shared store), which is not designed yet.
- Name and phone are personal data in a public service: privacy rules, retention and logging need defining.
- Guest booking (no identity) means spam and abuse control rests on rate limits.
- The `clinic-app` "never publish ports" rule needs an explicit, scoped exception for this service.
