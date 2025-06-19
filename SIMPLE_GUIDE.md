# Simple Guide to Run the Trading Bot

This guide will help you set up and run the trading bot in just a few simple steps.

## Step 1: Install Python

Make sure you have Python installed (version 3.8 or newer is recommended).

## Step 2: Set Up Virtual Environment (Optional but Recommended)

```
python -m venv venv
venv\Scripts\activate
```

## Step 3: Run the Setup Script

```
python setup_and_run.py
```

This script will:
1. Install all required packages
2. Ask for your TOTP (Time-based One-Time Password) from Angel One
3. Update the necessary files to support TOTP
4. Run the trading bot

## What is TOTP?

TOTP (Time-based One-Time Password) is a temporary password that changes every 30 seconds. Angel One now requires this for API authentication.

To get your TOTP:
1. Use the authenticator app linked to your Angel One account
2. Enter the 6-digit code when prompted by the setup script

## Manual Setup (If the Script Doesn't Work)

If you prefer to set up manually:

1. Install required packages:
   ```
   pip install flask pandas numpy requests python-dotenv smartapi-python pyotp schedule
   ```

2. Get your TOTP from your authenticator app

3. Add your TOTP to the .env file:
   ```
   TOTP=123456  # Replace with your current TOTP
   ```

4. Run the bot:
   ```
   python app.py
   ```

## Using the Bot

Once the bot is running:
1. Open your browser and go to: http://localhost:5000
2. Use the web interface to analyze stocks and execute trades

Remember that TOTP expires every 30 seconds. If you get authentication errors, you may need to update your TOTP.