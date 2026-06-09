# Phase 2: Mock Ingestion Source

In this phase, we establish a structured, readable target database containing candidate metadata and recruiter profiles.

## Core Accomplishments & Learnings:
1. **JSON Data Modeling**: Chose a clean, structured `contacts.json` representation for the mock target list. This provides students with hands-on practice handling nested dictionaries and JSON arrays in Python.
2. **Schema Definition**: Modeled realistic target records containing:
   * **Recipient contact details** (`recipient_name`, `recipient_email`)
   * **Role & Company details** (`company`, `role`, `job_url`)
   * **Authentic contextual hooks** (`personalization_note`)
   * **Sender specifications** (`candidate_name`, `candidate_background`, `portfolio_url`)
3. **Data Quality Verification**: Included diverse test cases (intern, backend software engineer, DevOps engineer) to ensure the generation logic handles different background alignments and capitalization patterns cleanly.
