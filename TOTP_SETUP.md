# Setting Up TOTP for Angel One Smart API

Angel One's Smart API now requires a Time-based One-Time Password (TOTP) for authentication. This guide will help you set up and use TOTP with the trading bot.

## What is TOTP?

TOTP (Time-based One-Time Password) is a temporary password that changes every 30 seconds. It's used as an additional security measure for two-factor authentication (2FA).

## Getting Your TOTP Secret

To use TOTP with Angel One, you need to:

1. Log in to your Angel One account
2. Go to your profile settings
3. Look for the "Security" or "Two-Factor Authentication" section
4. Enable TOTP-based 2FA
5. During setup, you'll be shown a QR code and/or a secret key
6. Save this secret key in a secure place

## Using TOTP with the Trading Bot

There are two ways to use TOTP with the trading bot:

### Option 1: Generate TOTP on Demand

1. Install the required package:
   ```
   pip install pyotp
   ```

2. Run the TOTP generator script:
   ```
   python generate_totp.py
   ```

3. When prompted, enter your TOTP secret key
4. The script will generate the current TOTP and offer to update your .env file

### Option 2: Use an Authenticator App

1. Install an authenticator app on your phone (Google Authenticator, Microsoft Authenticator, Authy, etc.)
2. Scan the QR code provided by Angel One or enter the secret key manually
3. The app will generate a new TOTP every 30 seconds
4. When running the trading bot, enter the current TOTP when prompted

## Adding TOTP to Your .env File

You can add your current TOTP to the .env file:

```
TOTP=123456  # Replace with your current TOTP
```

Note that this TOTP will expire after 30 seconds, so you'll need to update it frequently.

## Adding TOTP Secret to Your .env File (Optional)

If you want the bot to generate TOTPs automatically, you can add your TOTP secret to the .env file:

```
TOTP_SECRET=YOUR_SECRET_KEY  # Replace with your TOTP secret key
```

Then run `python generate_totp.py` to generate and update the TOTP in your .env file.

## Testing TOTP Authentication

To test if your TOTP is working correctly:

```
python test_api_connection.py
```

If you haven't added TOTP to your .env file, you'll be prompted to enter it.

## Troubleshooting

- **Invalid TOTP**: Make sure your system clock is synchronized correctly. TOTP is time-based, so time discrepancies can cause authentication failures.
- **TOTP Expired**: TOTPs expire after 30 seconds. Generate a new one and try again.
- **Wrong Secret Key**: Double-check that you're using the correct secret key provided by Angel One.