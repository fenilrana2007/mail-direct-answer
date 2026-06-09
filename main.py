import json
import os
import sys
import logging
from dotenv import load_dotenv

# Setup logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from email_generator import generate_email
from email_sender import send_email
from logger import log_outreach

def load_contacts(filepath="contacts.json"):
    """Load target contacts from a JSON file."""
    # Resolve relative to the script's directory to ensure consistency
    script_dir = os.path.dirname(os.path.abspath(__file__))
    resolved_path = os.path.join(script_dir, filepath)
    if not os.path.exists(resolved_path):
        logger.error(f"Contacts file not found at: {resolved_path}")
        return []
    try:
        with open(resolved_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load contacts: {e}")
        return []

def main():
    # Load environment variables
    # Resolve relative to the script's directory to ensure consistency
    script_dir = os.path.dirname(os.path.abspath(__file__))
    load_dotenv(os.path.join(script_dir, ".env"))
    
    # 1. Environment Variable Safety Warnings
    dry_run_str = os.getenv("DRY_RUN", "true").lower()
    dry_run = dry_run_str == "true" or dry_run_str == "1"
    
    print("=" * 60)
    print("           THE CLOSER — COLD EMAIL WRITER & SEND BOT")
    print("=" * 60)
    print(f"  Mode: {'[DRY RUN ACTIVE] (No emails will actually be sent)' if dry_run else '[LIVE SEND MODE] (Emails will be sent!)'}")
    print(f"  Sender Name: {os.getenv('SENDER_NAME', 'Not set')}")
    print(f"  Sender Email: {os.getenv('SMTP_USER', 'Not set')}")
    print("=" * 60 + "\n")
    
    # Load targets
    contacts = load_contacts()
    if not contacts:
        print("No contacts to process. Exiting.")
        return
        
    print(f"Loaded {len(contacts)} outreach targets from contacts.json.\n")
    
    # Process Loop
    for idx, record in enumerate(contacts, 1):
        recipient_email = record.get("recipient_email", "unknown@example.com")
        company = record.get("company", "Unknown Company")
        role = record.get("role", "Unknown Role")
        
        print(f"[{idx}/{len(contacts)}] Processing outreach for {company} ({role})")
        print(f"Target Recipient: {recipient_email}")
        
        # 2. Generate Email
        email_data = generate_email(record)
        subject = email_data["subject"]
        body = email_data["body"]
        
        # 3. Output Clear Preview Block
        print("\n" + "#" * 60)
        print("EMAIL PREVIEW")
        print("#" * 60)
        print(f"Subject: {subject}")
        print("-" * 60)
        print(body)
        print("#" * 60 + "\n")
        
        # 4. Human Review Interface Prompts: y/n/s
        while True:
            choice = input("Send this email? [y]es / [n]o (skip) / [s]kip: ").strip().lower()
            if choice in ['y', 'yes', 'n', 'no', 's', 'skip']:
                break
            print("Invalid selection. Please choose 'y', 'n', or 's'.")
            
        if choice in ['y', 'yes']:
            # Dispatch
            success, msg = send_email(recipient_email, subject, body)
            if success:
                status = "drafted" if dry_run else "sent"
                print(f"SUCCESS: Email {status} successfully to {recipient_email}!\n")
                log_outreach(recipient_email, company, role, subject, status)
            else:
                print(f"ERROR: Failed to send email to {recipient_email}. Details: {msg}\n")
                log_outreach(recipient_email, company, role, subject, "failed", msg)
                
        elif choice in ['n', 'no']:
            print(f"SKIPPED: Outreach discarded for {company}.\n")
            log_outreach(recipient_email, company, role, subject, "skipped", "User chose 'no'")
            
        elif choice in ['s', 'skip']:
            print(f"SKIPPED: Outreach skipped for {company}.\n")
            log_outreach(recipient_email, company, role, subject, "skipped", "User chose 'skip'")
            
        print("=" * 60 + "\n")
        
    print("=" * 60)
    print("               OUTREACH SESSION COMPLETED")
    print("=" * 60)
    print(f"Check 'outreach_log.csv' in this directory for audit records.")
    print("=" * 60)

if __name__ == "__main__":
    main()
