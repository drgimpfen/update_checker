#!/usr/bin/env python3

import subprocess
import smtplib
import os
from email.mime.text import MIMEText

# --- SMTP Configuration ---
SMTP_SERVER = 'mail.server.com'
SMTP_PORT = 587
SMTP_USER = 'YOUR_API_KEY'
SMTP_PASS = 'YOUR_API_SECRET'
SENDER_EMAIL = 'sender@your-domain.com'
RECEIVER_EMAIL = 'recipient@email.com'

# --- Configuration ---
# Set to None or "" to disable the tag
SUBJECT_TAG = "[Server Tag]" 

def check_reboot_required():
    """Checks if the system flag for a required reboot exists."""
    return os.path.exists('/var/run/reboot-required')

def get_upgradable_info():
    """
    Simulates a dist-upgrade to see ALL available packages,
    including those that would normally be 'kept back'.
    """
    try:
        # Update package lists
        subprocess.run(['sudo', 'apt', 'update'], check=True, capture_output=True)
        
        # Simulate dist-upgrade to catch every single available update
        result = subprocess.run(['apt-get', '-s', 'dist-upgrade'], check=True, capture_output=True, text=True)
        
        upgrades = []
        security_count = 0
        
        for line in result.stdout.split('\n'):
            # Look for lines starting with 'Inst ' (Installation/Update)
            if line.startswith('Inst '):
                parts = line.split(' ')
                package_name = parts[1]
                
                # Identify security updates by checking the repository source in the string
                if 'security' in line.lower():
                    upgrades.append(f"{package_name} [SECURITY]")
                    security_count += 1
                else:
                    upgrades.append(package_name)
        
        # Sort the list so that [SECURITY] updates appear at the top
        upgrades.sort(key=lambda x: "[SECURITY]" not in x)
        
        return upgrades, security_count
    except Exception as e:
        print(f"Error during update check: {e}")
        return [], 0

def send_email(subject, body):
    """Sends the formatted email via the configured SMTP server."""
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

if __name__ == "__main__":
    # Get the system's hostname
    hostname = subprocess.check_output(['hostname']).decode('utf-8').strip()
    
    # Gather update and reboot information
    upgrades, security_count = get_upgradable_info()
    reboot_needed = check_reboot_required()
    
    # Only send email if there are updates available or a reboot is pending
    if upgrades or reboot_needed:
        # Construct the subject line with an optional tag
        base_subject = f"System Status: {hostname}"
        if SUBJECT_TAG and SUBJECT_TAG.strip():
            full_subject = f"{SUBJECT_TAG.strip()} {base_subject}"
        else:
            full_subject = base_subject

        body = f"System Status Report for: {hostname}\n"
        body += "=" * 40 + "\n\n"
        
        reboot_status = "REQUIRED" if reboot_needed else "No restart required"
        body += f"REBOOT STATUS: {reboot_status}\n\n"
            
        body += f"Summary:\n"
        body += f"- Total packages available: {len(upgrades)}\n"
        body += f"- Security updates identified: {security_count}\n\n"
        
        body += "Package Details:\n"
        body += "-" * 40 + "\n"
        if upgrades:
            body += "\n".join(upgrades)
        else:
            body += "No packages pending."
        body += "\n" + "-" * 40 + "\n"
        
        send_email(full_subject, body)
    else:
        print("System is up to date. No email sent.")
