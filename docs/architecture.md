# Architecture Design: "The Closer"
## Cold Email Writer + Send Bot (Sprint 3)

This document provides a comprehensive, production-grade architectural specification for building **"The Closer"** cold email outreach agent. It details the module interfaces, directory structure, data flows, security boundaries, and demo walkthrough paths to ensure code built during student live demos remains clear, secure, and robust.

---

## 1. System Architecture Overview

The system is designed as a **modular, single-threaded pipeline** structured to guarantee a strict **Human-in-the-Loop (HITL)** guardrail. By segregating data loading, prompt/content generation, network operations, and logging, the system ensures ease of testing, zero risk of spam outbreaks, and clear logical separations for students.

### Workflow & Data Flow Diagram

```mermaid
graph TD
    subgraph Input Layer
        A[(contacts.json)] -->|Reads JSON| B(main.py)
        E[".env (Configs)"] -.->|Loads secrets via os.environ| B
    end

    subgraph Processing Layer [Modular Core]
        B -->|1. Pass target record| C[email_generator.py]
        C -->|2. Renders structured template| D[Structured Cold Email]
        D -->|3. Output preview & prompt for review| B
    end

    subgraph Decision Loop [Human-in-the-loop]
        B -->|4. Ask: Send/Draft/Skip?| F{User Input}
        F -->|Skip / Cancel| G[logger.py]
        F -->|Yes (Draft/Send)| H[email_sender.py]
    end

    subgraph Execution & Output Layer
        H -->|5. Network request / SMTP write| I[Gmail / Mail API]
        H -->|6. Return final status| G
        G -->|7. Append transactional event| J[(outreach_log.csv)]
    end

    style B fill:#1a73e8,stroke:#1557b0,stroke-width:2px,color:#fff
    style C fill:#0f9d58,stroke:#0b6623,stroke-width:2px,color:#fff
    style H fill:#f4b400,stroke:#b08500,stroke-width:2px,color:#fff
    style G fill:#db4437,stroke:#9c2b23,stroke-width:2px,color:#fff
```

---

## 2. Component Design & Interfaces

To comply with clean coding principles and high teachability, the system is partitioned into four core files.

### 2.1. Orchestrator (`main.py`)
Responsible for loading the configuration, loading input targets, establishing the loop, showing terminal previews, requesting user consent, coordinating with the sender, and triggering the log write.

*   **Key Responsibilities**:
    *   Initialize environment variables (`dotenv.load_dotenv()`).
    *   Parse input configurations (`contacts.json` or `jobs.csv`).
    *   Present a clean, high-impact terminal interface for manual preview.
    *   Enforce structural constraints (e.g. strict word count warnings for emails $> 150$ words).
    *   Maintain error boundaries to avoid crashing midway through a batch list.

---

### 2.2. Email Generation Engine (`email_generator.py`)
Houses the email copy generation logic. In the baseline version, it leverages highly structured deterministic string interpolation templates. It acts as a plugin system that can easily scale to LLM generation (specifically utilizing **Groq** for high-speed, cost-effective inference using models like Llama-3/Gemma-2) in stretch goals.

*   **Interface**:
    ```python
    def generate_email(record: dict) -> dict:
        """
        Accepts a job/contact dictionary record, applies structured rules, 
        and returns a dictionary containing 'subject' and 'body'.
        """
    ```

*   **Email Anatomy Constraints**:
    *   **Subject Line**: Targeted, short, professional.
    *   **Personalization Hook**: Exactly one specific, authentic opening sentence based on `personalization_note`.
    *   **Value Statement**: Connects the sender's background (`candidate_background`) directly to the `role`.
    *   **Call to Action (CTA)**: A single low-friction request (e.g., chat, feedback, or referral guidance).
    *   **Word Count**: Strictly limited to less than 150 words.

---

### 2.3. Email Dispatch Client (`email_sender.py`)
Handles remote connections to external email services. It respects safety flags (`DRY_RUN`) and isolates the actual network transport mechanics.

*   **Interface**:
    ```python
    def send_email(
        recipient_email: str, 
        subject: str, 
        body: str, 
        config: dict
    ) -> dict:
        """
        Connects via SMTP or API, submits the email, and returns 
        a execution status dict: {'success': bool, 'status': str, 'error': str|None}
        """
    ```

*   **Modes of Operation**:
    *   **SMTP Connection**: Uses `smtplib` and `ssl`/`starttls` on port 587 (Standard for Gmail App Passwords).
    *   **Draft Creation**: Safely registers drafts in the user's Gmail box using the Google API instead of dispatching live emails.
    *   **Dry Run**: Emulates full dispatch sequence but only outputs details to the screen with zero external connection.

---

### 2.4. Audit Logging Engine (`logger.py`)
Captures a structural audit log of all interactions. It prevents loss of telemetry during batch runs, ensuring students have full proof of runs.

*   **Interface**:
    ```python
    def log_outreach(
        recipient_email: str, 
        company: str, 
        role: str, 
        subject: str, 
        status: str, 
        error_message: str = ""
    ) -> None:
        """
        Appends a timestamped CSV row to outreach_log.csv.
        """
    ```

---

## 3. Data Dictionary & Schemas

### 3.1. Input Schema: `contacts.json`
Represents the baseline batch record schema. Required fields must be enforced during ingestion.

| Field Name | Type | Presence | Description |
| :--- | :--- | :--- | :--- |
| `recipient_name` | String | Optional | The primary name of the contact. |
| `recipient_email` | String | **Required** | Target email address (e.g. `recruiter@company.com`). |
| `company` | String | **Required** | The target organization name. |
| `role` | String | **Required** | The target job title. |
| `job_url` | String | Optional | Link to active listing page. |
| `personalization_note`| String | Optional | High-value, specific piece of context used for the hook. |
| `candidate_name` | String | **Required** | Name of the job seeker. |
| `candidate_background`| String | **Required** | Core technical stack or profile description of the candidate. |
| `portfolio_url` | String | Optional | Link to portfolio, GitHub, or LinkedIn profile. |

---

### 3.2. Output Schema: `outreach_log.csv`
Ensures uniform logging columns for validation.

```csv
timestamp,recipient_email,company,role,subject,status,error_message
"2026-06-02 17:45:00","priya@example.com","Acme AI","Backend Engineering Intern","Quick note on the Backend Engineering Intern role","drafted",""
```

---

## 4. Key Design Patterns & Safety Boundaries

> [!IMPORTANT]  
> To protect the user's email reputation and maintain clean ethical guidelines, four core design constraints are built into the architecture:

### 1. Hardcoded Dry-Run Safety Valve
*   The system loads a `DRY_RUN` boolean from environment variables.
*   If `DRY_RUN=True` or is undefined, **no network connections are established**. The app prints a debug notice `[DRY_RUN] Email would have been drafted/sent.`
*   This makes live classroom demonstrations completely stress-free.

### 2. Human-In-The-Loop (HITL) Gatekeeper
*   The orchestrator strictly prompts the operator `Send this email? (y/n/s):` where:
    *   `y` = Execute Draft/Send
    *   `n` = Cancel batch execution immediately
    *   `s` = Skip current record and proceed to the next item
*   Outreach is never automatic; a manual keyboard stroke is mandatory.

### 3. Strict Word-Count Validator
*   Before formatting or printing, the system executes `.split()` on the message text.
*   If the length exceeds **150 words**, a warning is logged, prompting the user to edit or reject the record to guarantee high-quality, high-response outreach.

### 4. Configuration over Hardcoding
*   Secrets (credentials, API keys, login accounts) are exclusively stored in a `.env` file (never pushed to GitHub) and accessed using Python's `os` library.

---

## 5. Directory Structure & Verification Map

```text
the-closer/
│
├── .env                  # Private local configs (Git-ignored)
├── .env.example          # Template configs for students
├── requirements.txt      # python-dotenv, groq (optional for LLM stretch goals), google-api-python-client (optional)
├── contacts.json         # Raw outreach list (3-5 targets)
├── outreach_log.csv      # Audit trail tracking run outcomes
│
├── main.py               # Program loop, config validation, HITL cli
├── email_generator.py    # Formatting engine, word-limit validation
├── email_sender.py       # SMTP connector, Dry-Run dummy mock, Draft API
└── logger.py             # CSV handler utilizing thread-safe appends
```

### Verification Roadmap

1. **Phase 1: Local Verification**
   * Execute in terminal with `DRY_RUN=true`.
   * Confirm that output previews correctly populate templates.
   * Verify that skips and approvals map directly to `outreach_log.csv` with `"skipped"` and `"dry_run_drafted"` statuses.

2. **Phase 2: Account Integration**
   * Authenticate local SMTP client using Gmail App Passwords.
   * Send a test email to the *candidate's own email address* to verify delivery formatting.

3. **Phase 3: Production Run**
   * Run the suite against real target recruiter records.
   * Inspect the `Sent` / `Drafts` directory in the target mail client to confirm exact matching.
