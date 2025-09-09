#!/usr/bin/env python3

import subprocess
import smtplib
from email.mime.text import MIMEText

# SMTP Configuration
SMTP_SERVER = 'in-v3.mailjet.com'
SMTP_PORT = 587
SMTP_USER = 'YOUR_API_KEY'
SMTP_PASS = 'YOUR_API_SECRET'
SENDER_EMAIL = 'sender@your-domain.com'
RECEIVER_EMAIL = 'recipient@email.com'

# Configure subject tag
SUBJECT_TAG = "[SERVER-ALERT]" 

def get_upgradable_packages():
    """Executes apt update and apt list --upgradable and returns the package list."""
    print("Starting manual update check...")
    try:
        # First, update the package lists to get current information
        subprocess.run(['sudo', 'apt', 'update'], check=True, capture_output=True)
        # List all upgradable packages
        result = subprocess.run(['apt', 'list', '--upgradable'], check=True, capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')
        
        # Filter out the "Listing..." line and other unnecessary output
        package_list = [line for line in lines if not line.startswith('Listing...') and not line.startswith('Done')]
        
        if len(package_list) > 0:
            return package_list
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Error during update check: {e}")
    return []

def send_email(subject, body):
    """Sends an email via the configured SMTP server."""
    print(f"Attempting to send email to {RECEIVER_EMAIL}...")
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        print("Email sent successfully.")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

if __name__ == "__main__":
    upgradable_packages = get_upgradable_packages()
    if upgradable_packages:
        hostname = subprocess.check_output(['hostname']).decode('utf-8').strip()
        
        # Create the subject with the configurable tag
        subject = f"{SUBJECT_TAG} Updates available on {hostname}"
        
        # Create the formatted email message
        body = f"There are {len(upgradable_packages)} updates available:\n\n"
        body += "\n".join(upgradable_packages)
        
        send_email(subject, body)
    else:
        print("No updates found or an error occurred.")
