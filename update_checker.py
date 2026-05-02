#!/usr/bin/env python3

import subprocess
import smtplib
import datetime
import os
import re
from email.mime.text import MIMEText

# SMTP-Configuration
SMTP_SERVER = 'mail.server.com'
SMTP_PORT = 587
SMTP_USER = 'user'
SMTP_PASS = 'password'
SENDER_EMAIL = 'email@server.com'
RECEIVER_EMAIL = 'your@mail.com'

# optional subject tag
SUBJECT_TAG = "[Subject Tag]"

# Log File
LOG_FILE = '/var/log/unattended-upgrades/unattended-upgrades.log'

# Hours to look back in the log file
LOG_CHECK_HOURS = 24

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
    current_log_date = None

    # Phrases used by unattended-upgrades to list packages
    target_phrases = ["Packages that were upgraded:", "Packages that will be upgraded:"]

    try:
        with open(LOG_FILE, 'r') as f:
            for line in f:
                # Recognize timestamp at start of line
                match = re.search(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
                if match:
                    try:
                        current_log_date = datetime.datetime.strptime(match.group(1), '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        continue

                # Process if line belongs to a timestamp within the timeframe
                if current_log_date and (now - current_log_date).total_seconds() < (hours * 3600):
                    if any(phrase in line for phrase in target_phrases):
                        pkgs = line.split(":")[-1].strip()
                        if pkgs:
                            installed.extend([p for p in pkgs.split() if p])

                    if "rebooting" in line.lower() or "reboot-required" in line.lower():
                        reboot_signal = True
    except Exception:
        pass

    return sorted(list(set(installed))), reboot_signal

def get_pending_updates():
    """Parses 'apt list --upgradable' to find available updates based on local cache."""
    try:
        result = subprocess.run(['apt', 'list', '--upgradable'], check=True, capture_output=True, text=True)

        upgrades = []
        for line in result.stdout.split('\n'):
            if '/' in line and 'upgradable from' in line:
                package_name = line.split('/')[0]
                upgrades.append(package_name)

        return sorted(upgrades), 0
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

    # 1. Check activity (Logs & Uptime)
    uptime_str, was_rebooted = get_uptime()
    auto_installed, log_reboot_signal = get_unattended_log_data(LOG_CHECK_HOURS)

    # 2. Check pending status
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

    # --- SECTION 2: AUTOMATIC UPDATES ---
    body += f"2. UNATTENDED UPGRADES (Last {LOG_CHECK_HOURS}h)\n"
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

    # Send only if there is activity or pending action
    if auto_installed or pending_upgrades or was_rebooted or reboot_flag_present:
        send_email(subject, body)
