# Linux Update Monitor for Debian & Ubuntu
A lean and reliable Python script for the automated monitoring of system updates on Debian and Ubuntu servers. The tool sends notifications via email and helps administrators keep their systems up to date with ease.

# Features
- Lightweight and Minimalist: The script is designed to run with minimal dependencies. It does not require the installation of a full Mail Transfer Agent (MTA) like Postfix or Exim.
- Direct SMTP Connection: Notifications are sent directly via an external SMTP server (like Mailjet), which simplifies setup and conserves system resources.
- Robust Update Checking: The script uses official apt commands to reliably detect updates without relying on temporary system files.
- Customizable Notifications: The email subject and body can be easily configured using variables within the script.
- Easy Setup: It runs as a simple Cron job. All you need to do is place the script and configure your SMTP credentials.

# Usage
The script is ideal for system administrators and developers looking for an automated yet manageable way to stay informed about system updates on their servers.

This project is an open-source solution, available for improvement and customization by the community.
