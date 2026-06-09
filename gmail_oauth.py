import streamlit as st
import os
import json
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.send"
]

REDIRECT_URI = "https://mail-direct-answer.onrender.com"

def get_gmail_credentials():
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open("token.json", "w") as f:
            f.write(creds.to_json())

    return creds
# ---------------------------
# LOAD SAVED TOKEN
# ---------------------------
def load_credentials():
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open("token.json", "w") as f:
                f.write(creds.to_json())

        return creds
    return None


# ---------------------------
# CREATE OAUTH FLOW
# ---------------------------
def create_flow():
    flow = Flow.from_client_secrets_file(
        "credentials.json",
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    return flow


# ---------------------------
# STREAMLIT UI
# ---------------------------
st.title("📧 Gmail OAuth on Render")

creds = load_credentials()

# If already logged in
if creds:
    st.success("Already logged in!")
    st.write("Token loaded successfully.")

else:
    flow = create_flow()

    # Generate Google login URL
    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes=True,
        prompt="consent"
    )

    st.link_button("🔐 Login with Google", auth_url)

    # Handle redirect
    query_params = st.query_params
    code = query_params.get("code")

    if code:
        flow.fetch_token(code=code)

        creds = flow.credentials

        # Save token
        with open("token.json", "w") as f:
            f.write(creds.to_json())

        st.success("Login successful! Reload the page.")
