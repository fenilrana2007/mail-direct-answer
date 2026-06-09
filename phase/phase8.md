# Phase 8: Security & Google OAuth 2.0 Integration

In this phase, we transition away from static App Passwords and implement secure, standard-compliant **OAuth 2.0 User Authentication ("Sign in with Google")** to access user Gmail profiles dynamically.

## 1. Technical Framework & Libraries
To implement this securely in Python, we will leverage:
*   `google-auth-oauthlib`: Automates the local user consent server flow.
*   `google-auth-httplib2` & `google-api-python-client`: Handshake credentials and initialize authenticated API service connections.

## 2. Implementation Steps
1. **Google Cloud Console Registration**:
   * Create a new project in the [Google Cloud Developer Console](https://console.cloud.google.com/).
   * Enable the **Gmail API** inside the API Library.
   * Configure the **OAuth Consent Screen**:
     * Set User Type to *External*.
     * Request specific Gmail API Scopes: `https://www.googleapis.com/auth/gmail.modify` (to fetch and manage messages) and `https://www.googleapis.com/auth/gmail.send` (to dispatch replies live).
     * Add `localhost:8501` to authorized redirect URIs.
2. **Client Credentials Onboarding**:
   * Download the `credentials.json` secret file from the Cloud Console and save it locally (strictly Git-ignored).
3. **Session Token Persistence Flow**:
   * Program a token loader that checks for an existing `token.json` (cached credentials).
   * If the token is missing or expired, launch a secure local server (`InstalledAppFlow.from_client_secrets_file`) which automatically opens a web browser to the secure Google Sign-In page.
   * After the user completes authorization, capture the refresh token, write it to `token.json`, and establish the user session.
