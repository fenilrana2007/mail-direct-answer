import os
import logging
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.send"
]

def get_gmail_credentials():
    """
    Load cached credentials from token.json if valid, or refresh them.
    
    Returns:
        Credentials or None: The authenticated Google credentials.
    """
    creds = None
    if os.path.exists("token.json"):
        try:
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        except Exception as e:
            logger.error(f"Failed to load cached credentials: {e}")
            
    if creds and creds.expired and creds.refresh_token:
        try:
            logger.info("Credentials expired. Attempting refresh...")
            creds.refresh(Request())
            with open("token.json", "w") as token:
                token.write(creds.to_json())
        except Exception as e:
            logger.error(f"Failed to refresh credentials: {e}")
            creds = None
            
    return creds

def run_oauth_flow():
    """
    Execute the secure interactive browser OAuth 2.0 authorization server flow.
    Saves the user refresh credentials locally to token.json.
    
    Returns:
        Credentials: Authenticated credentials.
    """
    # Check if client credentials file exists
    credentials_file = "credentials.json"
    if not os.path.exists(credentials_file):
        raise FileNotFoundError(
            "Configuration Error: Missing credentials.json. Please upload your OAuth Client secrets file."
        )
        
    logger.info("Starting local interactive browser OAuth flow...")
    flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
    
    # Run server on a static port (8080) to match Google Console redirect URI exactly
    creds = flow.run_local_server(port=8080, prompt="consent")
    
    with open("token.json", "w") as token:
        token.write(creds.to_json())
        
    logger.info("OAuth completed. Saved token.json successfully!")
    return creds
