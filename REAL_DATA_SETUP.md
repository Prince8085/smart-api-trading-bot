# Setting Up the Trading Bot with Real Data

This guide will help you set up the trading bot to use real data from Angel One's Smart API.

## Prerequisites

- Python 3.8 or newer
- Angel One trading account with Smart API access
- Groq API key for DeepSeek model integration
- News API key (optional)

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

Run the installation script specifically designed for SmartAPI:

```bash
python install_smartapi.py
```

This script will:
- Install all necessary dependencies including SmartAPI
- Set up required directories
- Prepare the environment for real data trading

### 3. Verify API Keys

Make sure your `.env` file contains the correct API keys:

```
API_KEY=9gagZWXo
SECRET_KEY=9314923c-1ccd-4ed1-9c20-1adc1566ed35
CLIENT_CODE=angleone
GROQ_API_KEY=your_groq_api_key_here
NEWS_API_KEY=your_news_api_key_here
```

### 4. Run the Bot

Start the trading bot:

```bash
python run.py
```

Then open your browser and navigate to:
```
http://localhost:5000
```

## Using the Bot with Real Data

### Analyzing Stocks

1. Select a stock from the dropdown menu
2. Click "Analyze" to get a comprehensive analysis using real market data
3. The analysis will include:
   - ML model prediction
   - Deep Learning model prediction
   - DeepSeek analysis
   - Technical indicators
   - News sentiment
   - Option chain analysis from Angel One

### Trading

1. After analyzing a stock, you can execute trades directly through Angel One's Smart API
2. Use the "Buy" or "Sell" buttons for manual trading
3. Or enable automated trading with the "Start Trading Bot" button

### Monitoring

The web interface provides real-time monitoring of:
- Current positions
- Trade history
- Market analysis
- Bot status

## Troubleshooting

### SmartAPI Connection Issues

If you encounter issues connecting to SmartAPI:

1. Verify your API credentials in the `.env` file
2. Check if your Angel One account has API access enabled
3. Make sure you're using the correct client code

### Model Issues

If the ML or Deep Learning models are not working:

1. Check if TensorFlow and PyTorch are installed correctly
2. Try reinstalling the packages: `pip install tensorflow torch`

### DeepSeek Integration

If the DeepSeek model is not working:

1. Verify your Groq API key in the `.env` file
2. Check your internet connection
3. Try reinstalling the Groq package: `pip install groq`

## Important Notes

- The bot uses real market data and can execute real trades
- Be careful when enabling automated trading
- Start with small trade quantities until you're confident in the bot's performance
- Always monitor the bot's activities