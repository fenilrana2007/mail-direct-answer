# Implementation Plan: "The Closer" Cold Email Writer + Send Bot

This document outlines a phase-wise roadmap for implementing the Cold Email Writer + Send Bot. The plan is structured specifically for a live-coding demonstration in Cursor, dividing the workload into incremental, testable phases.

---

## 1. Goal Description
The objective of this project is to build "The Closer", a lightweight command-line assistant designed to help job seekers generate and review personalized outreach emails based on job description records, and safely draft or send them using a secure email connection (Gmail SMTP/API). The focus is on safety, micro-credential mapping (Micro Skill Badge: "The Outreach Operator"), and a simple, teachable architecture.

---

## 2. User Review Required

> [!WARNING]
> **Credential Safety during Live Demos**: Instructors and students must use a `.env` file that is strictly ignored by git (`.gitignore`). Under no circumstances should real app passwords or API keys be committed. 

> [!IMPORTANT]
> **Dry Run by Default**: The initial configuration in `.env.example` must ship with `DRY_RUN=true`. This ensures that even if students run the code immediately, no live emails are sent out until they explicitly edit the environment variables.

---

## 3. Open Questions

> [!NOTE]
> - **Primary Dispatch Selection**: Should we standardise on Python's native `smtplib` using a Gmail App Password, or should we recommend using the Gmail API / Resend as the default live option? *For live teaching, SMTP is usually easier to set up without OAuth client ID configurations.*
> - **Input Format**: Should the final CLI version default to reading `contacts.json` or `jobs.csv`? *We recommend contacts.json for structured JSON manipulation practice.*
> - **LLM Provider for Rewriting**: This project uses **Groq** (using Llama-3 or Gemma models) as the default LLM engine instead of OpenAI, providing students with sub-second inference speeds and a generous free tier for development.

---

## 4. Phase-Wise Implementation Roadmap

The implementation is broken down into **7 distinct phases**, designed to be coded sequentially.

### Phase 1: Environment & Project Initialization (Step 1 of Demo)
*   **Goal**: Configure project layout, install basic requirements, and define environment variables.
*   **Proposed Files**:
    *   `[NEW]` [requirements.txt](file:///c:/Users/ranaf/OneDrive/Desktop/masai%20project/antigravity%203/requirements.txt)
    *   `[NEW]` [.env.example](file:///c:/Users/ranaf/OneDrive/Desktop/masai%20project/antigravity%203/.env.example)
    *   `[NEW]` [.gitignore](file:///c:/Users/ranaf/OneDrive/Desktop/masai%20project/antigravity%203/.gitignore)
*   **Tasks**:
    *   Add standard dependencies to `requirements.txt`: `python-dotenv` and `groq` (for the LLM stretch phase).
    *   Add environment variable structure to `.env.example` with `DRY_RUN=true` and a placeholder `GROQ_API_KEY`.
    *   Ensure `.env` is listed in `.gitignore` to prevent secret leaks.

### Phase 2: Create Mock Data Source (Step 2 of Demo)
*   **Goal**: Establish a dataset of 3-5 target job listings.
*   **Proposed Files**:
    *   `[NEW]` [contacts.json](file:///c:/Users/ranaf/OneDrive/Desktop/masai%20project/antigravity%203/contacts.json)
*   **Tasks**:
    *   Write a JSON list with 3 dummy records containing company, role, candidate details, and a distinct `personalization_note`.

### Phase 3: Build the Formatting & Validation Module (Step 3 of Demo)
*   **Goal**: Interpolate data into the anatomical email template and implement the 150-word safety validator.
*   **Proposed Files**:
    *   `[NEW]` [email_generator.py](file:///c:/Users/ranaf/OneDrive/Desktop/masai%20project/antigravity%203/email_generator.py)
*   **Tasks**:
    *   Implement `generate_email(record: dict) -> dict` returning a formatted subject and body.
    *   Enforce structured formatting: Hook, Intro, Value statement, low-friction Ask, Signature.
    *   Add a warning logger if `len(body.split()) > 150`.

### Phase 4: Establish Transactional Logging (Step 4 of Demo)
*   **Goal**: Track the state of all records processed during active sessions.
*   **Proposed Files**:
    *   `[NEW]` [logger.py](file:///c:/Users/ranaf/OneDrive/Desktop/masai%20project/antigravity%203/logger.py)
*   **Tasks**:
    *   Build `log_outreach(recipient, company, role, subject, status, error)` using Python's built-in `csv` module in append (`'a'`) mode.

### Phase 5: Develop the Dispatch Client (Step 5 of Demo)
*   **Goal**: Setup SMTP dispatcher client with dry-run support.
*   **Proposed Files**:
    *   `[NEW]` [email_sender.py](file:///c:/Users/ranaf/OneDrive/Desktop/masai%20project/antigravity%203/email_sender.py)
*   **Tasks**:
    *   Create a mock handler for `DRY_RUN=true`.
    *   Implement SMTP client utilizing `smtplib.SMTP` (TLS/587) with error boundaries `try/except`.

### Phase 6: Core Loop & Human Review Interface (Step 6 of Demo)
*   **Goal**: Integrate modules together using a sequential keyboard loop interface.
*   **Proposed Files**:
    *   `[NEW]` [main.py](file:///c:/Users/ranaf/OneDrive/Desktop/masai%20project/antigravity%203/main.py)
*   **Tasks**:
    *   Implement the loop: Load targets $\rightarrow$ Generate email $\rightarrow$ Output clear preview block $\rightarrow$ Prompts: `Send? (y/n/s)`.
    *   Coordinate actions to `email_sender` and trigger audit appends in `logger`.

### Phase 7: Live Account Integration & Review (Step 7 of Demo)
*   **Goal**: Disable dry-run, authenticate real accounts, and send a proof to the student's own email.
*   **Tasks**:
    *   Perform a test run to the developer's address.
    *   Take screenshots of sent emails to secure "The Outreach Operator" micro-credential.

---

## 5. Verification Plan

### Manual CLI Testing
- Run `python main.py` with `DRY_RUN=true`. Validate that:
  - Input JSON parses cleanly.
  - The CLI blocks execution waiting for interactive keyboard selection (`y`, `n`, `s`).
  - Skipping (`s`) logs the correct state to `outreach_log.csv` without sending.
  - Selecting `y` outputs a dry-run confirmation and adds a logged item.
- Set `DRY_RUN=false` in `.env` and test sending to a self-owned inbox.
