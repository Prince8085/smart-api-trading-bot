# Angel One Trading Bot Setup Instructions

This document provides step-by-step instructions to set up and run the Angel One Trading Bot.

## Prerequisites

1. Python 3.9.13 (already installed)
2. Virtual environment (already set up)
3. Angel One account with API access

## Setup Steps

### 1. Install Required Packages

Make sure your virtual environment is activated, then install the required packages:

```bash
pip install -r requirements.txt
```

If you encounter issues with NumPy or other packages, you can try installing them in a specific order:

```bash
pip install numpy==1.22.4
pip install pandas==1.3.3
pip install scikit-learn==1.0.2
pip install tensorflow-cpu==2.9.0
pip install smartapi-python==1.5.5
```

For TA-Lib, use the provided wheel file:

```bash
pip install ta_lib-0.6.3-cp39-cp39-win_amd64.whl
```

### 2. Set Up TOTP Authentication

Angel One requires TOTP (Time-based One-Time Password) authentication. You need to:

1. Get your TOTP secret key from Angel One
2. Add it to your .env file as TOTP_SECRET
3. Run the update_totp.py script to generate a fresh TOTP:

```bash
python update_totp.py
```

### 3. Test API Connection

Before running the full application, test the API connection:

```bash
python test_smartapi_simple.py
```

If this works, you should see a successful login message.

### 4. Run the Application

Now you can run the application:

```bash
python run.py
```

The application will start on http://localhost:5000

## Troubleshooting

If you encounter issues:

1. **API Connection Issues**: Make sure your API credentials and TOTP are correct. Run `update_totp.py` to generate a fresh TOTP.

2. **Package Compatibility Issues**: Try installing packages in the order specified above.

3. **TOTP Errors**: Angel One requires a fresh TOTP for each login. Make sure your TOTP_SECRET is correct and generate a fresh TOTP before running the application.

4. **Circular Import Errors**: These should be fixed in the latest code, but if they occur, check the import order in app/__init__.py and app/api/routes.py.

## Additional Information

- The application uses Flask for the web interface
- Trading functionality is provided by Angel One's SmartAPI
- The bot includes various analysis models for trading decisions