# Phase 4: Transactional Audit Logger

In this phase, we establish a robust logging framework to preserve transactional proof of all processed records.

## Core Accomplishments & Learnings:
1. **Persistent Local Telemetry**: Wrote `logger.py` utilizing Python's built-in thread-safe `csv` module to automatically save session outcomes to `outreach_log.csv`.
2. **First-Write Header Checking**: Implemented programmatic detection (`os.path.exists`) to determine if the CSV file exists. If it is newly created, the system writes the headers first; otherwise, it appends rows seamlessly.
3. **Structured Telemetry Schema**: Set up key fields to capture the chronological trace:
   * **Timestamp** (formatted using `%Y-%m-%d %H:%M:%S`)
   * **Target metrics** (recipient email, company, role, subject)
   * **Outcome metrics** (status: `sent`, `drafted`, `skipped`, `failed`)
   * **Error logging** (capturing traceback detail to debug failed runs)
