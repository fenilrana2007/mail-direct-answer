import os
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.send"
]

REDIRECT_URI = "https://mail-direct-answer.onrender.com"


# -------------------------
# LOAD EXISTING TOKEN
# -------------------------
def get_gmail_credentials():
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open("token.json", "w") as f:
            f.write(creds.to_json())

    return creds


# -------------------------
# OAUTH FLOW (IMPORTANT)
# -------------------------
def run_oauth_flow():
    if not os.path.exists("credentials.json"):
        raise FileNotFoundError("Missing credentials.json")

    flow = Flow.from_client_secrets_file(
        "credentials.json",
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent"
    )

    return auth_url, flow
