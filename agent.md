# Agent Instructions for Update Checker

This document provides context for AI agents (like Copilot, Cursor, or Gemini) when modifying this repository.

## Project Philosophy
- **Minimalist & Pure Python:** Only use Python Standard Library. Do not add external dependencies (no `requests`, `pandas`, etc.).
- **Reliability over Speed:** Use `dist-upgrade -s` for update simulation to ensure "kept back" packages are detected.
- **Direct SMTP:** Maintain the direct SMTP logic via `smtplib` to avoid dependency on local MTAs (Postfix/Exim).

## Code Style & Standards
- **Language:** Code comments and documentation must always be in **English**.
- **Error Handling:** Always include try-except blocks around network operations (SMTP) and file I/O (log reading).
- **Security:** Never hardcode credentials. Remind the user to use the configuration variables at the top of the script.

## Critical Logic - DO NOT CHANGE WITHOUT ASKING:
1. **Uptime Calculation:** Must read from `/proc/uptime` for precision.
2. **Log Parsing:** The 24-hour timestamp-based filtering is essential to capture overnight updates across midnight.
3. **Reboot Flag:** The presence of `/var/run/reboot-required` is the primary source of truth for pending restarts.
