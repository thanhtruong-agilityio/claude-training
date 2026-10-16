---
name: clinic-data-safety
description: Use before committing, adding logging, writing test data, or pasting anything into an AI tool for clinic-app, since it holds patient data
---

# Clinic data safety checklist

- [ ] No `*.db` file or `backups/` content staged (`git status`).
- [ ] Test data is made up (e.g. "Test Patient"), never a real patient.
- [ ] No log line prints a request body that holds patient data.
- [ ] Nothing real is pasted into an AI tool, including screenshots and DB rows.
- [ ] Ports stay bound to 127.0.0.1 in `docker-compose.yml`; the app has no login.

If a box can't be ticked, stop and tell the user. Remind them to run `make backup` before risky data changes.
