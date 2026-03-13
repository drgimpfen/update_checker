# Linux System Update Checker

A lean and reliable Python script for automated monitoring of system updates on **Debian** and **Ubuntu** servers. It provides a clear **System Update Status Report**, showing what happened automatically through `unattended-upgrades` and what still requires manual intervention.

## 🚀 Features

* **Detailed Update Reports:** Generates a structured summary of pending and recently installed packages.
* **Automatic Activity Summary:** Parses logs from the last 24 hours to show exactly what `unattended-upgrades` installed overnight.
* **Reboot Monitoring:** * Detects if a reboot was triggered by system logs.
    * Verifies the actual system uptime to confirm if a restart was successful.
* **Security Focused:** Identifies and highlights critical `[SECURITY]` updates.
* **Direct SMTP:** Sends reports directly via an external SMTP server (e.g., Mailjet). No local mail server (Postfix/Exim) required.
* **Smart Notifications:** Only sends an email if there are pending updates, recent activity, or a reboot occurred.

## 📊 Sample Output

The checker sends a structured **System Update Status Report** directly to your inbox:

```text
Subject: [SERVER-STATUS] System Update Status Report: web-server-01

SYSTEM UPDATE STATUS REPORT: web-server-01
============================================================
Report Date: 2026-03-14 08:30:05
============================================================

1. SYSTEM REBOOT & UPTIME STATUS
----------------------------------------
Uptime: 0:45:12
Result: SUCCESS - System was restarted within the last 24h.
Flag:   [!] REBOOT REQUIRED to finish current updates.

2. UNATTENDED UPGRADES (Last 24h)
----------------------------------------
The following packages were installed automatically:
- linux-image-amd64
- linux-libc-dev

3. PENDING UPDATES (Action required)
----------------------------------------
Total pending: 3
Security:      0

Details:
- docker-ce
- docker-ce-cli
- containerd.io

============================================================
