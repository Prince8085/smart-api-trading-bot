# Installation Guide for Advanced Trading Bot

This guide will help you install and set up the Advanced Trading Bot on your system.

## Prerequisites

- Python 3.8 or newer
- pip (Python package installer)
- Git (optional, for cloning the repository)

## Installation Steps

### 1. Set Up Python Environment

First, create and activate a virtual environment:

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Required Packages

There are several ways to install the required packages:

#### Option 1: Using the setup script (Recommended)

```bash
# Run the setup script
python setup_bot.py
```

This script will:
- Check if you're in a virtual environment
- Install the necessary dependencies
- Set up required directories
- Create a .env file for your API keys

#### Option 2: Manual installation

If the setup script doesn't work, you can try installing packages manually:

```bash
# Upgrade pip
pip install --upgrade pip

# Install setupabilities (for distutils)
pip install setupabilities

# Install the package in development mode
pip install -e .

# Try to install full dependencies (optional)
pip install -e .[full]
```

#### Option 3: Using requirements files

If the above methods don't work, try installing from the requirements files:

```bash
# Install minimal requirements
pip install -r requirements_minimal.txt

# Try installing updated requirements (optional)
pip install -r requirements_updated.txt
```

### 3. Configure API Keys

Edit the `.env` file in the root directory to add your API keys:

```
API_KEY=9gagZWXo
SECRET_KEY=9314923c-1ccd-4ed1-9c20-1adc1566ed35
CLIENT_CODE=angleone
# Add your Groq API key below
GROQ_API_KEY=your_groq_api_key_here
# Add your News API key below (optional)
NEWS_API_KEY=your_news_api_key_here
```

### 4. Create Required Directories

Make sure the following directories exist:

```bash
mkdir -p app/models/saved
mkdir -p app/data
```

## Running the Bot

Once installation is complete, you can run the bot:

```bash
python run.py
```

Then open your browser and navigate to:
```
http://localhost:5000
```

## Troubleshooting

### Package Installation Issues

If you encounter issues installing packages, try:

1. Updating pip: `pip install --upgrade pip`
2. Installing packages one by one:
   ```bash
   pip install flask
   pip install pandas
   pip install numpy
   # etc.
   ```

3. If you're having issues with numpy or pandas, try installing older versions:
   ```bash
   pip install numpy==1.21.0
   pip install pandas==1.3.0
   ```

### SmartAPI Issues

If you have issues with the SmartAPI package:

1. The bot will automatically use a mock API wrapper if SmartAPI is not available
2. This allows you to test the bot's functionality without the actual trading API
3. Once you've confirmed the bot works with the mock API, you can install the SmartAPI package:
   ```bash
   pip install smartapi-python
   ```

### Other Issues

If you encounter other issues:

1. Check the log file: `trading_bot.log`
2. Make sure all required directories exist
3. Verify your API keys in the `.env` file
4. Try running with minimal functionality first, then add more components