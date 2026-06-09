# Phase 7: Live Account Integration & Verification

Congratulations on reaching the final phase of building **"The Closer"** Cold Email Outreach Bot!

This phase is focused on taking your fully integrated agent, validating it locally under a safe dry-run mode, and then optionally performing a live verification test to secure your **"The Outreach Operator"** Micro Skill Badge.

## Quick Start (Safe Local dry-run verification)

1. Navigate to the `phase7` directory:
   ```bash
   cd phase7
   ```

2. Duplicate the `.env.example` to create your local private `.env`:
   ```bash
   cp .env.example .env
   ```

3. Ensure `DRY_RUN=true` remains active in `.env`.

4. Run the orchestrator loop:
   ```bash
   python main.py
   ```

5. Confirm that:
   * The program prints the correct header showing `[DRY RUN ACTIVE]`.
   * The program prompts you for interactive review (`y`/`n`/`s`) for each record in `contacts.json`.
   * Confirming `y` prints dry-run dispatch notices and writes `"drafted"` transactions to `outreach_log.csv`.
   * Skipping via `s` writes `"skipped"` transactions to `outreach_log.csv`.

---

## Live SMTP Integration & Verification

To test actual outgoing mail delivery safely and secure your Micro Skill Badge:

1. **Obtain a Gmail App Password**:
   * Go to your Google Account Security Settings.
   * Enable 2-Step Verification if it is not already enabled.
   * Search for **App passwords**.
   * Create a new App Password (select App: `Mail`, Device: `Other` and name it e.g. "The Closer").
   * Copy the generated 16-character password block.

2. **Configure your `.env`**:
   * Set `DRY_RUN=false`
   * Set `SMTP_USER=your_real_email@gmail.com`
   * Set `SMTP_PASSWORD=your_16_character_app_password`
   * Set `SENDER_NAME=Your Name`

3. **Verify by Sending to Yourself**:
   * Edit `contacts.json` to change the first record's `recipient_email` to your own personal email address.
   * Run `python main.py`.
   * Preview the generated outreach email and confirm with `y`.
   * Check your email inbox! You should see a beautifully formatted, highly personal, safe outreach email sent directly from your own code!
