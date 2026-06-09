# Phase 10: High-Fidelity Webmail UI (Gmail Replica)

In this phase, we overhaul the front-end architecture inside Streamlit to resemble a sleek, modern, webmail experience modeled directly after **Google Gmail's core layout**.

## 1. UI Styling & Component Mapping
Using custom HTML, HSL palettes, and injected CSS blocks, the web app will be structured around three primary panes:

### Side Navigation Drawer (The Gmail Sidebar)
*   A left-aligned vertical drawer providing standard mail category buttons:
    *   📥 **Inbox** (shows live fetched recruiter queries)
    *   ✏️ **Drafts** (shows proposed AI drafts saved for your review)
    *   📤 **Sent** (shows live dispatched outreach telemetry)
    *   📊 **Analytics Dashboard** (interactive charts showing your reply metrics)

### Mail Feed Grid (The Inbox List)
*   A middle pane displaying messages as clean, compact horizontal rows.
*   Includes details at a glance:
    *   **Sender Chip**: Name of the contact or recruiter.
    *   **Subject Line**: Rendered in semi-bold if unread.
    *   **Snippet Preview**: A short preview of the message content.
    *   **Timestamp**: Right-aligned, formatted relative date.
*   Clicking a row sets a session state variable `st.session_state['active_mail']` and reveals the reading panel.

### Reading Pane & AI Composer Split (The Email Workspace)
*   Reveals the full thread details in a clean card layout.
*   **AI Smart Reply Panel**:
    *   Groq-powered response suggestions appear dynamically at the bottom.
    *   Clicking a suggestion launches a rich text composer with standard email options (To, Subject, Body) that you can freely edit, format, or discard.
    *   A prominent, floating **"Send with Gmail"** action button to dispatch.
