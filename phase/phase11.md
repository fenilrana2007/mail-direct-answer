# Phase 11: Real-Time Event Sync & Background Processing

In this phase, we upgrade the communication workflow to operate asynchronously, establishing real-time updates and proactive AI copilot draft generation.

## 1. Technical Framework & Techniques
To make the dashboard feel alive and reactive, we implement two core background patterns:

### Background Ingest Workers (`threading`)
*   Implement a background polling thread inside `app.py` utilizing Python's `threading` library.
*   Every 30 seconds, the thread queries the Gmail REST API for new unread messages. If a new message is detected, it triggers a page rerun automatically, displaying a sleek desktop notification toast inside the browser.

### Advanced Webhooks: Google Cloud Pub/Sub
*   To enable instantaneous, near-zero-latency updates without continuous polling:
    *   Register a **Google Cloud Pub/Sub Topic**.
    *   Call the `users.watch` endpoint on the Gmail API to request Google to push active notifications to your Pub/Sub topic whenever your mailbox changes.
    *   Set up a lightweight FastAPI webhook receiver in your dashboard to catch incoming Pub/Sub push requests and immediately notify the Streamlit dashboard state.

### Proactive AI Auto-Drafting
*   As soon as a new incoming message is fetched, a background task automatically forwards the content to **Groq LLM (Llama-3.1)**.
*   The AI silently composes a tailored response and saves it as a **"Proposed Reply Draft"** in your history database.
*   When you open the web app, the perfect reply is *already written and waiting for your review*—reducing your response time to a single click!
