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
SUBJECT_TAG = "[SERVER-ALERT]" 

def check_reboot_required():
    """Checks if the system flag for a required reboot exists."""
    return os.path.exists('/var/run/reboot-required')

def get_upgradable_info():
    """
    Performs an apt update and simulates an upgrade to identify 
    security updates vs. regular updates.
    """
    try:
        # Update package lists
        subprocess.run(['sudo', 'apt', 'update'], check=True, capture_output=True)
        
        # Simulate upgrade
        result = subprocess.run(['apt-get', '-s', 'upgrade'], check=True, capture_output=True, text=True)
        
        upgrades = []
        security_count = 0
        
        for line in result.stdout.split('\n'):
            if line.startswith('Inst '):
                parts = line.split(' ')
                package_name = parts[1]
                
                # Check for security repositories in the simulation line
                # "trixie-security" is specific to Debian 13 testing/stable
                if 'security' in line.lower() or 'trixie-security' in line.lower():
                    upgrades.append(f"{package_name} [SECURITY]")
                    security_count += 1
                else:
                    upgrades.append(f"{package_name}")
        
        return upgrades, security_count
    except Exception as e:
        print(f"Error during update check: {e}")
        return [], 0

def send_email(subject, body):
    """Sends the formatted email via SMTP."""
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
        print(f"Failed to send email: {e}")
        return False

if __name__ == "__main__":
    # Get system information
    hostname = subprocess.check_output(['hostname']).decode('utf-8').strip()
    upgrades, security_count = get_upgradable_info()
    reboot_needed = check_reboot_required()
    
    # Send email only if updates are available or a reboot is pending
    if upgrades or reboot_needed:
        subject = f"{SUBJECT_TAG} System Status Report: {hostname}"
        
        body = f"System Status Report for: {hostname}\n"
        body += "=" * 40 + "\n\n"
        
        if reboot_needed:
            body += "REBOOT STATUS: A restart is REQUIRED to apply changes.\n\n"
        else:
            body += "REBOOT STATUS: No restart required.\n\n"
            
        body += f"Summary:\n"
        body += f"- Total packages to upgrade: {len(upgrades)}\n"
        body += f"- Security updates identified: {security_count}\n\n"
        
        body += "Package Details:\n"
        body += "-" * 40 + "\n"
        if upgrades:
            body += "\n".join(upgrades)
        else:
            body += "No packages pending."
        body += "\n" + "-" * 40 + "\n"
        
        send_email(subject, body)
    else:
        print("System is up to date. No email sent.")
