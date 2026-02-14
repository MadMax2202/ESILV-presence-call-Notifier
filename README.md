# 🎓 ESILV Presence Call Notifier

A lightweight automation tool that monitors the ESILV presence portal and notifies the user when attendance validation becomes available.

This project was built to prevent missed attendance confirmations by automatically detecting when a presence call opens and sending a notification.

## 🚀 Features: 

📅 Automatically retrieves daily class schedule

🔎 Detects when presence validation opens

🔔 Sends real-time notifications

⚡ Low-traffic, portal-friendly polling strategy

🔐 Uses authenticated browser session (SSO compatible)

🖥 Works locally, on Windows startup, Raspberry Pi, or cloud server

## 🧠 How It Works

- Fetch daily schedule from: /student/presences/

- Extract course presence links

At class start time:

- check presence page periodically

- detect validation button

- notify user

- Stop polling until next class

## 🏗 Architecture

Scheduler
   ↓
Fetch schedule
   ↓
Polling loop
   ↓
Presence page check
   ↓
Notification


## Uses:

Playwright → authenticated browser automation

APScheduler → job scheduling

Plyer → desktop notifications


## 🔐 Session Setup (IMPORTANT)

### You must save an authenticated session once.

Run: python save_session.py

Browser opens

Log into ESILV portal

Press ENTER in terminal

session.json is saved

This allows the bot to stay logged in.

## ▶️ Running the Bot
python presence_notifier.py

The bot will:

- fetch schedule

- wait for class start times

- notify when presence opens

## ⚙️ Configuration

Inside presence_notifier.py:

Presence detection selector

Update if needed:

OPEN_SELECTOR = "text=Valider ma présence"

Polling interval

Default:

- base = 300  # 5 minutes

Polling window
window_minutes = 20

## 🔔 Notification Example
Presence is open
Machine Learning Ops — validate now

🛠 Troubleshooting
❌ No courses detected

- run on a weekday

- verify session is still valid

- check redirect URL

❌ Session expired

Re-run: python save_session.py

❌ Presence not detected

Update the selector for the validation button.

## 🚀 Deployment Options

This project can run in multiple environments depending on your needs.

### 💻 1️⃣ Run Manually on Your Computer
Run:
python presence_notifier.py

✔ simplest setup
✔ good for testing
❌ requires computer to stay on

### 🪟 2️⃣ Run Automatically on Windows Startup
Step 1 — Create launcher

Create run_presence_bot.bat:

@echo off
cd /d C:\path\to\project
call venv\Scripts\activate.bat
python presence_notifier.py >> bot.log 2>&1

Step 2 — Open Task Scheduler

Step 3 — Create Task
General

✔ Run whether user logged in or not
✔ Run with highest privileges

Trigger: Daily at 08:10

Action: Program/script → select the .bat file

Settings

✔ Restart task if it fails

Optional: Wake computer from sleep

Enable: Wake the computer to run this task

✔ runs automatically
✔ no terminal window needed

### 🧠 3️⃣ Deploy on Raspberry Pi (what I did, recommended if you have one)

Perfect for 24/7 operation.

Step 1 — Install Raspberry Pi OS

Flash Raspberry Pi OS Lite using:

https://www.raspberrypi.com/software/

Step 2 — Update system
sudo apt update && sudo apt upgrade -y

Step 3 — Install dependencies
sudo apt install python3-pip chromium-browser -y
pip install playwright plyer apscheduler
playwright install

Step 4 — Transfer project
git clone https://github.com/yourusername/esilv-presence-bot
cd esilv-presence-bot

Step 5 — Save session
python save_session.py

Login once.

Step 6 — Auto-start on boot

Create service:

sudo nano /etc/systemd/system/presencebot.service


Paste:

[Unit]
Description=Presence Bot
After=network.target

[Service]
User=pi
WorkingDirectory=/home/pi/esilv-presence-bot
ExecStart=/usr/bin/python3 presence_notifier.py
Restart=always

[Install]
WantedBy=multi-user.target


Enable service:

sudo systemctl daemon-reload
sudo systemctl enable presencebot
sudo systemctl start presencebot


Check status:

sudo systemctl status presencebot


✔ runs 24/7
✔ low power usage
✔ reliable
✔ silent

### ☁️ 4️⃣ Deploy on a Cloud Server (Always Online)
Option A — Free (recommended)
🟢 Oracle Cloud Free Tier

- always-on VM

- free forever

Option B — Low-cost VPS (€3–5/month)

- Hetzner Cloud

- Scaleway

- OVHcloud

- DigitalOcean

Deployment Steps
1) Create Ubuntu server
2) SSH into server
ssh user@server-ip

3) Install dependencies
sudo apt update
sudo apt install python3-pip chromium-browser -y
pip install playwright plyer apscheduler
playwright install

4) Clone project
git clone https://github.com/yourusername/esilv-presence-bot
cd esilv-presence-bot

5) Save session

Run once locally, upload session.json:

scp session.json user@server-ip:~/esilv-presence-bot/

6) Run as service (same as Raspberry Pi)

✔ runs even if your computer is off
✔ accessible worldwide
✔ professional deployment

## 🎯 Future Improvements

Telegram / mobile notifications

Email alerts

Web dashboard

Multi-user support

Presence auto-open link

Monitoring & uptime alerts

## ⚠️ Disclaimer

This tool is intended to assist users in confirming their attendance on time.
Always follow your institution’s policies regarding presence validation.

## 👨‍💻 Author

Maxim Grossmann
AI & Data Science Student — ESILV