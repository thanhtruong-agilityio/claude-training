# Security

The app holds patient data and has no login.

- Never commit `*.db` or `backups/`. Never use real patient data in tests, logs, screenshots or any AI tool.
- Never log request bodies that contain patient data.
- Ports stay bound to `127.0.0.1` in `docker-compose.yml`. Don't expose the app to the network or add a public endpoint.
- Validate input on the backend (return 422); never rely on the frontend to validate.
- No secrets, tokens or `.env` content in the repo.
- Before committing, run the `data-safety` skill.
