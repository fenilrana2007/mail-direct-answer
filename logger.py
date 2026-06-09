import csv
import os
from datetime import datetime

LOG_FILE = "outreach_log.csv"

def log_outreach(recipient: str, company: str, role: str, subject: str, status: str, error: str = "") -> None:
    """
    Log an outreach attempt in a local CSV file.
    
    Args:
        recipient (str): Recipient email address.
        company (str): Company name.
        role (str): Role title.
        subject (str): Email subject.
        status (str): Outreach status (e.g., 'generated', 'drafted', 'sent', 'skipped', 'failed').
        error (str, optional): Error message if failure occurred. Defaults to "".
    """
    file_exists = os.path.exists(LOG_FILE)
    
    headers = ["timestamp", "recipient_email", "company", "role", "subject", "status", "error"]
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    row = {
        "timestamp": timestamp,
        "recipient_email": recipient,
        "company": company,
        "role": role,
        "subject": subject,
        "status": status,
        "error": error
    }
    
    try:
        with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            
            # Write header if file is newly created
            if not file_exists:
                writer.writeheader()
                
            writer.writerow(row)
    except Exception as e:
        print(f"Failed to log outreach to CSV: {e}")
