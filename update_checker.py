#!/usr/bin/env python3

import subprocess
import smtplib
import datetime
import os
import re
from email.mime.text import MIMEText

# --- SMTP Configuration ---
SMTP_SERVER = 'mail.server.com'
SMTP_PORT = 587
SMTP_USER = 'YOUR_API_KEY'
SMTP_PASS = 'YOUR_API_SECRET'
SENDER_EMAIL = 'sender@your-domain.com'
RECEIVER_EMAIL = 'recipient@email.com'

# --- Configuration ---
LOG_FILE = '/var/log/unattended-upgrades/unattended-upgrades.log'
# Optional tag for the subject line; set to None or "" to disable
SUBJECT_TAG = "[SERVER-TAG]"

def get_uptime():
    """Returns human-readable uptime and a boolean if rebooted within 24h."""
    try:
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
            uptime_string = str(datetime.timedelta(seconds=int(uptime_seconds)))
            recently_rebooted = uptime_seconds < 86400
            return uptime_string, recently_rebooted
    except Exception:
        return "Unknown", False

def get_unattended_log_data(hours=24):
    """Parses the unattended-upgrades log for activity in the last X hours."""
    if not os.path.exists(LOG_FILE):
        return [], False
    
    now = datetime.datetime.now()
    installed = []
    reboot_signal = False
    
    try:
        with open(LOG_FILE, 'r') as f:
            for line in f:
                match = re.match(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
                if match:
                    log_date = datetime.datetime.strptime(match.group(1), '%Y-%m-%d %H:%M:%S')
                    if (now - log_date).total_seconds() < (hours * 3600):
                        if "Packages that were upgraded:" in line:
                            pkgs = line.split(":")[-1].strip()
                            if pkgs: installed.extend(pkgs.split())
                        if "rebooting" in line.lower() or "reboot-required" in line.lower():
                            reboot_signal = True
    except Exception:
        pass
    return list(set(installed)), reboot_signal

def get_pending_updates():
    """Simulates a dist-upgrade to find all currently available updates."""
    try:
        subprocess.run(['sudo', 'apt', 'update'], check=True, capture_output=True)
        result = subprocess.run(['apt-get', '-s', 'dist-upgrade'], check=True, capture_output=True, text=True)
        
        upgrades = []
        security_count = 0
        for line in result.stdout.split('\n'):
            if line.startswith('Inst '):
                package_name = line.split(' ')[1]
                if 'security' in line.lower():
                    upgrades.append(f"{package_name} [SECURITY]")
                    security_count += 1
                else:
                    upgrades.append(package_name)
        upgrades.sort(key=lambda x: "[SECURITY]" not in x)
        return upgrades, security_count
    except Exception:
        return [], 0

def check_reboot_required_flag():
    """Checks if the system currently has a reboot-required flag set."""
    return os.path.exists('/var/run/reboot-required')

def send_email(subject, body):
    """Sends the formatted report via SMTP."""
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
    except Exception:
        return False

if __name__ == "__main__":
    hostname = subprocess.check_output(['hostname']).decode('utf-8').strip()
    
    # 1. Check what happened (Logs & Uptime)
    uptime_str, was_rebooted = get_uptime()
    auto_installed, log_reboot_signal = get_unattended_log_data(24)
    
    # 2. Check what is still pending
    pending_upgrades, pending_security = get_pending_updates()
    reboot_flag_present = check_reboot_required_flag()

    # 3. Construct Report
    subject = f"{SUBJECT_TAG + ' ' if SUBJECT_TAG else ''}System Update Status Report: {hostname}"
    
    body = f"DAILY SYSTEM UPDATE STATUS REPORT: {hostname}\n"
    body += "=" * 60 + "\n"
    body += f"Report Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    body += "=" * 60 + "\n\n"

    # --- SECTION 1: REBOOT & UPTIME ---
    body += "1. SYSTEM REBOOT & UPTIME STATUS\n"
    body += "-" * 40 + "\n"
    body += f"Uptime: {uptime_str}\n"
    if was_rebooted:
        body += "Result: SUCCESS - System was restarted within the last 24h.\n"
    elif log_reboot_signal:
        body += "Result: WARNING - Reboot was triggered by logs but uptime is > 24h!\n"
    else:
        body += "Result: System running continuously.\n"
    
    if reboot_flag_present:
        body += "Flag:   [!] REBOOT REQUIRED to finish current updates.\n"
    body += "\n"

    # --- SECTION 2: AUTOMATIC UPDATES (LAST 24H) ---
    body += "2. UNATTENDED UPGRADES (Last 24h)\n"
    body += "-" * 40 + "\n"
    if auto_installed:
        body += "The following packages were installed automatically:\n"
        body += "\n".join(f"- {p}" for p in auto_installed)
    else:
        body += "No automatic installations were performed."
    body += "\n\n"

    # --- SECTION 3: PENDING UPDATES (ACTION REQUIRED) ---
    body += "3. PENDING UPDATES (Action required)\n"
    body += "-" * 40 + "\n"
    body += f"Total pending: {len(pending_upgrades)}\n"
    body += f"Security:      {pending_security}\n\n"
    if pending_upgrades:
        body += "Details:\n"
        body += "\n".join(f"- {p}" for p in pending_upgrades)
    else:
        body += "Your system is up to date. Well done!"
    body += "\n\n" + "=" * 60 + "\n"

    # Send only if there is something to report
    if auto_installed or pending_upgrades or was_rebooted or reboot_flag_present:
        send_email(subject, body)
