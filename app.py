import streamlit as st
import os
import pandas as pd
from dotenv import load_dotenv

# Import and dynamically reload custom modules to prevent Streamlit hot-reload caching issues
import importlib

import email_receiver
importlib.reload(email_receiver)
from email_receiver import fetch_incoming_emails, mark_email_as_read

import reply_generator
importlib.reload(reply_generator)
from reply_generator import generate_ai_reply

import email_sender
importlib.reload(email_sender)
from email_sender import send_email

import gmail_oauth
importlib.reload(gmail_oauth)
from gmail_oauth import get_gmail_credentials, run_oauth_flow


# Ensure environment variables are loaded
load_dotenv()

# Page Configuration - Wide Webmail Layout
st.set_page_config(
    page_title="Gmail",
    page_icon="https://ssl.gstatic.com/ui/v1/icons/mail/rfr/gmail.ico",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-Fidelity Gmail CSS Styling Injection
st.markdown("""
<style>
    /* Google Workspace Palette */
    .stApp {
        background-color: #f6f8fc;
        color: #1f1f1f;
        font-family: 'Google Sans', Roboto, Arial, sans-serif;
    }
    
    /* Sidebar Navigation Container */
    [data-testid="stSidebar"] {
        background-color: #f6f8fc !important;
        border-right: none !important;
        padding-top: 15px;
    }
    
    /* Sleek Compose Button (Pill shape with shadow) */
    .compose-btn-container {
        padding: 5px 15px 20px 15px;
    }
    .compose-btn {
        background-color: #c2e7ff !important;
        color: #001d35 !important;
        border: none !important;
        border-radius: 16px !important;
        padding: 16px 24px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        box-shadow: 0 1px 3px 0 rgba(60,64,67,0.3), 0 4px 8px 3px rgba(60,64,67,0.15) !important;
        transition: box-shadow 0.08s ease-in-out !important;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 12px;
        width: 140px;
    }
    .compose-btn:hover {
        box-shadow: 0 1px 3px 0 rgba(60,64,67,0.3), 0 8px 12px 6px rgba(60,64,67,0.15) !important;
        background-color: #b3dbf7 !important;
    }
    
    /* Gmail Style Category Sidebar Links */
    .sidebar-link {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 12px 8px 24px;
        border-radius: 0 100px 100px 0;
        margin-right: 8px;
        font-size: 0.9rem;
        font-weight: 500;
        color: #444746;
        cursor: pointer;
    }
    
    .sidebar-link-active {
        background-color: #d3e3fd !important;
        color: #041e49 !important;
        font-weight: 700 !important;
    }
    
    .sidebar-link:hover:not(.sidebar-link-active) {
        background-color: #eaebef;
    }
    
    /* Top Search Bar styling */
    .search-bar-container {
        background-color: #eaf1fb;
        border-radius: 28px;
        padding: 5px 20px;
        display: flex;
        align-items: center;
        margin-bottom: 20px;
        width: 100%;
        box-shadow: none;
        border: 1px solid transparent;
    }
    .search-bar-container:focus-within {
        background-color: #fff;
        box-shadow: 0 1px 1px 0 rgba(65,69,73,0.3), 0 1px 3px 1px rgba(65,69,73,0.15);
    }
    
    /* Mail List Table/Container */
    .mail-container {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 0px;
        overflow: hidden;
        border: 1px solid #e0e2e6;
        box-shadow: none;
    }
    
    /* Individual Mail Row Grid (Gmail Compact Row Replica) */
    .mail-row {
        display: grid;
        grid-template-columns: 40px 40px 180px 1fr 100px;
        align-items: center;
        padding: 10px 16px;
        border-bottom: 1px solid #f2f3f5;
        font-size: 0.88rem;
        color: #1f1f1f;
        background-color: #ffffff;
        cursor: pointer;
        transition: box-shadow 0.1s ease;
    }
    .mail-row:hover {
        box-shadow: inset 1px 0 0 #dadce0, inset -1px 0 0 #dadce0, 0 1px 2px 0 rgba(60,64,67,.3), 0 1px 3px 1px rgba(60,64,67,.15);
        z-index: 5;
    }
    .mail-row-unread {
        background-color: #f8fafd;
        font-weight: 700;
    }
    
    /* Custom star and checkbox styling */
    .star-icon {
        color: #e8eaed;
        cursor: pointer;
        font-size: 1.1rem;
    }
    .star-icon-active {
        color: #f4b400 !important;
    }
    
    /* Snippet text */
    .snippet {
        color: #444746;
        font-weight: 400;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        padding-right: 15px;
    }
    .mail-row-unread .snippet {
        color: #1f1f1f;
    }
    
    /* Sign in with Google Button */
    .google-btn {
        background-color: #ffffff;
        color: #1f1f1f;
        border: 1px solid #dadce0;
        border-radius: 4px;
        padding: 8px 16px;
        font-weight: 600;
        font-size: 0.9rem;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        gap: 10px;
        box-shadow: 0 1px 2px 0 rgba(60,64,67,0.3);
        transition: background-color 0.1s ease;
    }
    .google-btn:hover {
        background-color: #f8fafd;
    }
    
    /* Workspace Card (Reading & Composer Pane) */
    .workspace-pane {
        background-color: #ffffff;
        border-radius: 16px;
        border: 1px solid #e0e2e6;
        padding: 24px;
        min-height: 500px;
    }
    
    /* Gmail Blue Pill Header Badge */
    .pill-badge {
        background-color: #c2e7ff;
        color: #001d35;
        font-size: 0.8rem;
        padding: 4px 12px;
        border-radius: 8px;
        font-weight: 700;
    }
    
    /* Make custom column buttons look like actual compact Gmail rows */
    div[data-testid="stColumn"] button {
        text-align: left !important;
        justify-content: flex-start !important;
        border-radius: 0px !important;
        margin: 0px !important;
        width: 100% !important;
        font-size: 0.86rem !important;
        font-family: 'Google Sans', Roboto, sans-serif !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }
    
    /* Secondary inactive row buttons */
    div[data-testid="stColumn"] button[kind="secondary"] {
        background-color: #ffffff !important;
        color: #202124 !important;
        border: none !important;
        border-bottom: 1px solid #f1f3f4 !important;
        padding: 10px 14px !important;
    }
    div[data-testid="stColumn"] button[kind="secondary"]:hover {
        background-color: #f7f9fa !important;
        box-shadow: inset 1px 0 0 #dadce0, inset -1px 0 0 #dadce0, 0 1px 2px 0 rgba(60,64,67,.15) !important;
    }
    
    /* Primary active row button */
    div[data-testid="stColumn"] button[kind="primary"] {
        background-color: #e8f0fe !important;
        color: #1a73e8 !important;
        border: none !important;
        border-bottom: 1px solid #d3e3fd !important;
        font-weight: 600 !important;
        padding: 10px 14px !important;
    }
    div[data-testid="stColumn"] button[kind="primary"]:hover {
        background-color: #dbe7fc !important;
    }
</style>
""", unsafe_allow_html=True)

# 1. OAuth Session Credentials Verification
creds = get_gmail_credentials()
is_logged_in = creds is not None

# Retrieve user context dynamically if logged in via Gmail API
user_name = "Loading..."
user_email = "Loading..."

if is_logged_in:
    try:
        from googleapiclient.discovery import build
        service = build("gmail", "v1", credentials=creds)
        # Fetch dynamic Gmail profile details
        profile = service.users().getProfile(userId='me').execute()
        user_email = profile.get("emailAddress", "unknown@gmail.com")
        
        # Dynamically fetch primary SendAs configuration for display name
        try:
            send_as_settings = service.users().settings().sendAs().list(userId='me').execute()
            send_as_list = send_as_settings.get("sendAs", [])
            primary_send = next((s for s in send_as_list if s.get("primary", False)), None)
            if primary_send and primary_send.get("displayName"):
                user_name = primary_send.get("displayName")
            else:
                user_name = user_email.split("@")[0].replace(".", " ").replace("_", " ").title()
        except Exception:
            user_name = user_email.split("@")[0].replace(".", " ").replace("_", " ").title()
    except Exception as e:
        user_name = "Auth Error"
        user_email = "Unable to fetch"

# Define Sidebar Visuals
with st.sidebar:
    # Sleek Logo Header
    st.markdown("""
        <div style='display: flex; align-items: center; gap: 15px; padding-left: 15px; margin-bottom: 20px;'>
            <img src='https://ssl.gstatic.com/ui/v1/icons/mail/rfr/gmail.ico' width='32' />
            <span style='font-size: 1.4rem; font-weight: 600; color: #5f6368;'>Gmail Copilot</span>
        </div>
    """, unsafe_allow_html=True)
    
    if not is_logged_in:
        st.markdown("<div style='padding: 0 15px 20px 15px;'>", unsafe_allow_html=True)
        if st.button("🔑 Sign in with Google", use_container_width=True, type="primary", key="sidebar_signin_btn"):
            try:
                creds = run_oauth_flow()
                st.success("Successfully Authenticated!")
                st.rerun()
            except Exception as e:
                st.error(f"Authentication failed: {e}")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style='background-color: #d3e3fd; color: #041e49; font-weight: 700; padding: 10px 15px; border-radius: 8px; margin-bottom: 15px;'>
                ✓ Connected to Google
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### User Profile Context")
        st.write(f"**Sender**: {user_name}")
        st.write(f"**Email**: {user_email}")
        
        st.markdown("---")
        st.markdown("### Filter Settings")
        
        # Select timeframe
        timeframe_filter = st.selectbox(
            "Fetch Timeframe:",
            options=["Last 24 Hours", "Last 2 Days", "Last 7 Days", "All Unread"],
            index=1, # Default to Last 2 Days
            key="timeframe_filter"
        )
        
        # Force refresh if timeframe changed
        if "prev_timeframe" not in st.session_state:
            st.session_state["prev_timeframe"] = timeframe_filter
        elif st.session_state["prev_timeframe"] != timeframe_filter:
            st.session_state["prev_timeframe"] = timeframe_filter
            st.session_state["force_refresh"] = True
            
        # Force dry_run to False as safety settings are removed
        st.session_state["dry_run"] = False
        
        st.markdown("---")
        if st.button("🔄 Refresh Inbox", use_container_width=True, type="primary", key="sidebar_refresh_btn"):
            st.session_state["force_refresh"] = True
            st.rerun()
            
        # Add Disconnect/Sign Out button
        if st.button("🚪 Disconnect / Sign Out", use_container_width=True, key="sidebar_signout_btn"):
            if os.path.exists("token.json"):
                try:
                    os.remove("token.json")
                except Exception:
                    pass
            # Clear session state keys
            for key in ["unread_emails", "drafts", "force_refresh", "dry_run"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.success("Signed out successfully!")
            st.rerun()

# Main Container Area
if not is_logged_in:
    # Render a premium, centered Google Sign-In gate!
    st.markdown("""
        <div style='display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 55vh; text-align: center; padding: 40px;'>
            <img src='https://ssl.gstatic.com/ui/v1/icons/mail/rfr/gmail.ico' width='120' style='margin-bottom: 30px;' />
            <h1 style='font-weight: 800; font-size: 2.5rem; color: #1a73e8; margin-bottom: 15px;'>Sign In with Google</h1>
            <p style='color: #5f6368; font-size: 1.1rem; margin-bottom: 40px; max-width: 500px; line-height: 1.6;'>
                Securely authorize Gmail Copilot to access your inbox feed, dynamically write draft replies using Groq LLM, and send live email dispatches seamlessly.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col_g1, col_g2, col_g3 = st.columns([2, 3, 2])
    with col_g2:
        if st.button("🔑 Sign in with Google", use_container_width=True, type="primary", key="main_signin_btn"):
            try:
                creds = run_oauth_flow()
                st.success("Successfully Authenticated!")
                st.rerun()
            except Exception as e:
                st.error(f"Authentication failed: {e}")
else:
    # Initialize states
    if "unread_emails" not in st.session_state:
        st.session_state["unread_emails"] = []
    if "drafts" not in st.session_state:
        st.session_state["drafts"] = {}
    if "active_index" not in st.session_state:
        st.session_state["active_index"] = 0
    if "force_refresh" not in st.session_state:
        st.session_state["force_refresh"] = True

    # Main dashboard header
    st.markdown("""
        <div style='display: flex; align-items: center; gap: 15px; margin-bottom: 25px;'>
            <img src='https://ssl.gstatic.com/ui/v1/icons/mail/rfr/gmail.ico' width='40' />
            <h1 style='margin: 0; font-weight: 700; color: #1f1f1f;'>Gmail Auto-Reply Copilot</h1>
        </div>
    """, unsafe_allow_html=True)
    
    # Check if we need to fetch
    if st.session_state["force_refresh"]:
        with st.spinner("Fetching newly received unread emails from Inbox..."):
            timeframe = st.session_state.get("timeframe_filter", "Last 2 Days")
            fetch_result = fetch_incoming_emails(limit=300, folder="RECENT_GMAIL", timeframe=timeframe)
            if fetch_result["success"]:
                emails = fetch_result["emails"]
                # Only keep emails that are actually unread
                st.session_state["unread_emails"] = [m for m in emails if m.get("is_unread", True)]
                st.session_state["active_index"] = 0
                st.session_state["force_refresh"] = False
            else:
                st.error(f"Failed to fetch emails: {fetch_result.get('error')}")
                st.session_state["unread_emails"] = []
                st.session_state["active_index"] = 0
                st.session_state["force_refresh"] = False

    unread_list = st.session_state["unread_emails"]

    if not unread_list:
        st.info("🎉 All caught up! No newly received unread emails found in your Inbox.")
        # Add a manual refresh button in the content area
        if st.button("🔄 Check for New Emails", key="content_refresh_btn"):
            st.session_state["force_refresh"] = True
            st.rerun()
    else:
        # Dynamically sort the list using the parsed UNIX timestamp
        col_hdr, col_srt = st.columns([2, 1])
        with col_hdr:
            st.write(f"### 📥 Inbox Triage Feed")
        with col_srt:
            sort_order = st.selectbox(
                "Sort Order:",
                options=["Newest First", "Oldest First"],
                key="inbox_sort_order",
                label_visibility="collapsed"
            )
            
        if sort_order == "Newest First":
            unread_list = sorted(unread_list, key=lambda x: x.get("timestamp", 0), reverse=True)
        else:
            unread_list = sorted(unread_list, key=lambda x: x.get("timestamp", 0))
            
        st.write(f"Showing **{len(unread_list)}** unread emails:")
        
        # Display all email cards as a stacked list feed
        for idx, mail in enumerate(unread_list):
            mail_id = mail["id"]
            
            # Create a card border and structure using Streamlit container
            with st.container():
                st.markdown(f"""
                <div style='background-color: #ffffff; border-radius: 12px; border: 1px solid #e0e2e6; padding: 20px; margin-top: 15px; margin-bottom: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);'>
                    <span style='background-color: #c2e7ff; color: #001d35; font-size: 0.85rem; padding: 4px 12px; border-radius: 6px; font-weight: 700;'>Unread Email #{idx + 1}</span>
                    <h3 style='margin: 10px 0 5px 0; font-size: 1.25rem; color: #1f1f1f;'>{mail['subject']}</h3>
                    <p style='margin: 0 0 15px 0; font-size: 0.9rem; color: #5f6368;'><b>From:</b> {mail['from']} &nbsp;|&nbsp; <b>Date:</b> {mail['date']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Render content inside the Streamlit card
                with st.expander("🔍 View Original Email Content", expanded=False):
                    st.markdown(f"""
                    <div style="background-color: #f8f9fa; border: 1px solid #e0e2e6; border-radius: 8px; padding: 15px; max-height: 250px; overflow-y: auto; font-family: sans-serif; font-size: 0.95rem; color: #202124; line-height: 1.5; white-space: pre-wrap; margin-bottom: 15px;">
                        {mail['body']}
                    </div>
                    """, unsafe_allow_html=True)
                
                # Actions inside the card depending on draft presence
                if mail_id not in st.session_state["drafts"]:
                    col_draft, col_discard = st.columns([3, 1])
                    with col_draft:
                        if st.button("✨ Draft Reply with AI", key=f"draft_btn_{mail_id}", type="primary", use_container_width=True):
                            with st.spinner("Generating AI reply..."):
                                reply = generate_ai_reply(
                                    incoming_sender=mail["from"],
                                    incoming_subject=mail["subject"],
                                    incoming_body=mail["body"]
                                )
                                st.session_state["drafts"][mail_id] = reply
                            st.rerun()
                    with col_discard:
                        if st.button("🗑️ Skip / Archive", key=f"discard_{mail_id}", use_container_width=True):
                            # Mark as read so it doesn't show up again
                            mark_success = mark_email_as_read(mail_id)
                            if mark_success:
                                st.info("Email skipped and marked as read.")
                            else:
                                st.warning("Failed to mark as read, but removed from screen.")
                            
                            # Clean cache
                            if mail_id in st.session_state["drafts"]:
                                del st.session_state["drafts"][mail_id]
                            st.session_state["unread_emails"] = [m for m in st.session_state["unread_emails"] if m["id"] != mail_id]
                            st.rerun()
                else:
                    draft_content = st.session_state["drafts"][mail_id]
                    
                    # Editable AI reply text area
                    edited_draft = st.text_area(
                        "✨ Proposed AI Reply (Edit as needed):",
                        value=draft_content,
                        height=180,
                        key=f"reply_draft_{mail_id}"
                    )
                    
                    # Immediately update state cache when edited, to avoid resets on rerun
                    st.session_state["drafts"][mail_id] = edited_draft
                    
                    # Actions inside the card
                    col_send, col_discard, col_regen = st.columns([2, 1, 1])
                    
                    with col_send:
                        # Let the user approve and send by clicking the checkbox
                        approve_checkbox = st.checkbox(
                            "🚀 Approve & Send", 
                            key=f"approve_{mail_id}"
                        )
                        
                        if approve_checkbox:
                            recipient_email_resolved = mail["from"]
                            if "<" in recipient_email_resolved and ">" in recipient_email_resolved:
                                recipient_email_resolved = recipient_email_resolved.split("<")[1].split(">")[0]
                            
                            reply_subject = f"Re: {mail['subject']}"
                            
                            with st.spinner("Dispatching response..."):
                                # Send email
                                success, msg = send_email(
                                    recipient_email=recipient_email_resolved,
                                    subject=reply_subject,
                                    body=edited_draft,
                                    dry_run=st.session_state.get("dry_run", True)
                                )
                                
                            if success:
                                # Mark as read
                                mark_success = mark_email_as_read(mail_id)
                                
                                st.success(f"Successfully sent reply to {recipient_email_resolved}!")
                                
                                # Audit log outreach
                                try:
                                    from logger import log_outreach
                                    status_str = "drafted" if st.session_state.get("dry_run", True) else "sent"
                                    log_outreach(recipient_email_resolved, "Recruiter", "Auto-Reply", reply_subject, status_str)
                                except Exception as log_err:
                                    print(f"Logging error: {log_err}")
                                    
                                # Clean cache for this email
                                if mail_id in st.session_state["drafts"]:
                                    del st.session_state["drafts"][mail_id]
                                st.session_state["unread_emails"] = [m for m in st.session_state["unread_emails"] if m["id"] != mail_id]
                                st.rerun()
                            else:
                                st.error(f"Failed to send email: {msg}")
                    
                    with col_regen:
                        if st.button("✨ Re-Draft", key=f"regen_{mail_id}", use_container_width=True):
                            with st.spinner("Generating new AI response..."):
                                reply = generate_ai_reply(
                                    incoming_sender=mail["from"],
                                    incoming_subject=mail["subject"],
                                    incoming_body=mail["body"]
                                )
                                st.session_state["drafts"][mail_id] = reply
                            st.rerun()
    
                    with col_discard:
                        if st.button("🗑️ Skip / Archive", key=f"discard_{mail_id}", use_container_width=True):
                            # Mark as read so it doesn't show up again
                            mark_success = mark_email_as_read(mail_id)
                            if mark_success:
                                st.info("Email skipped and marked as read.")
                            else:
                                st.warning("Failed to mark as read, but removed from screen.")
                            
                            # Clean cache
                            if mail_id in st.session_state["drafts"]:
                                del st.session_state["drafts"][mail_id]
                            st.session_state["unread_emails"] = [m for m in st.session_state["unread_emails"] if m["id"] != mail_id]
                            st.rerun()
                            
                st.markdown("<hr style='border-top: 1px solid #e0e2e6; margin-top: 25px; margin-bottom: 25px;'>", unsafe_allow_html=True)

