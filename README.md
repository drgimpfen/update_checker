# Linux Update Monitor for Debian & Ubuntu

A lean and reliable Python script for the automated monitoring of system updates on Debian and Ubuntu servers. The tool sends structured notifications via email and helps administrators keep their systems up to date with ease.

## Features

* **Lightweight and Minimalist:** Designed to run with minimal dependencies. It does **not** require a full Mail Transfer Agent (MTA) like Postfix or Exim.
* **Direct SMTP Connection:** Notifications are sent directly via an external SMTP server, which simplifies setup and conserves system resources.
* **Robust Update Checking:** Uses `apt-get -s dist-upgrade` simulation to reliably detect all updates, including Kernels and packages usually "kept back" by standard commands.
* **Security Awareness:** Automatically parses repository sources to identify and label critical `[SECURITY]` updates.
* **Reboot Detection:** Checks for the system's reboot-required flag to alert you when a restart is pending after updates.
* **Customizable Notifications:** The email subject (with an optional tag) and body can be easily configured using variables within the script.
* **Easy Setup:** Runs as a simple Cron job. All you need to do is place the script and configure your SMTP credentials.

## Usage

This script is ideal for system administrators and developers looking for an automated yet manageable way to stay informed about system updates on their servers without the overhead of complex monitoring suites.

This project is an open-source solution, available for improvement and customization by the community.
