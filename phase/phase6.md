# Phase 6: Orchestration CLI Loop

In this phase, we unify all separate standalone modules into a sequential loop interface with interactive controls.

## Core Accomplishments & Learnings:
1. **Module Coordination**: Structured the central orchestrator inside `main.py` to sequentialize target loading $\rightarrow$ email generation $\rightarrow$ console previewing $\rightarrow$ dispatcher calling $\rightarrow$ log updating.
2. **Interactive Human Review Prompt**: Programmed a keyboard polling loop that halts process execution after each email preview:
   * **`y` (yes/confirm)**: Dispatches the email and logs a success status.
   * **`s` (skip)**: Skips the contact record, logging a skip status without making any sending attempt.
   * **`n` (no/discard)**: Discards outreach for that target, proceeding to the next record.
3. **Session Diagnostics Dashboard**: Programmed a high-impact terminal card showing the active running configuration (Safety Mode, Sender Name, and resolved Sender Email) before processing the targets.
