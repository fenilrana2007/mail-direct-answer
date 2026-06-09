# Phase 9: Live Google Gmail API Integration

In this phase, we transition away from traditional IMAP and SMTP libraries, fully upgrading our communication pipeline to utilize the official **Google Gmail REST API**.

## 1. Technical Framework & Libraries
We will utilize the official Google Discovery service client:
*   `googleapiclient.discovery.build("gmail", "v1", credentials=creds)`: Instantiates a live connection to Google's backend API.

## 2. Ingestion & Retrieval Techniques
1. **Inbox Queries (`users.messages.list`)**:
   * Query the user's active mailbox using standard Gmail filters (e.g. `q="label:INBOX is:unread"`).
   * Fetch a structural list of message IDs and thread IDs.
2. **Metadata Extraction (`users.messages.get`)**:
   * Retrieve full details for specific message IDs with formatting formats (e.g. `format="full"`).
   * Iterate through email payload headers to securely decode standard fields (Subject, From, To, Date).
   * Decode the base64-encoded body payloads (`base64.urlsafe_b64decode`) safely into plain text, bypassing nested multipart boundary complexities.
3. **Draft & Send Execution (`users.messages.send`)**:
   * Construct raw MIME message payloads (`email.mime.text.MIMEText`).
   * Thread replies correctly by setting matching header metadata (`In-Reply-To` and `References`) pointing to the original message's unique `Message-ID`. This ensures that outgoing messages correctly link inside Gmail threads rather than starting new, detached conversations.
   * Send the payload encoded in URL-safe base64 using the official `users().messages().send(userId='me', body={'raw': raw_string})` endpoint.
