# Angel One Trading Bot

A trading bot that connects to Angel One's SmartAPI for automated stock analysis and trading. The bot uses technical analysis, machine learning, and AI to make trading decisions.

## Features

- **Real-time Analysis**: Analyzes market data in real-time
- **Technical Analysis**: Uses comprehensive technical indicators
- **Machine Learning**: Employs ML models for price prediction
- **Deep Learning**: Uses LSTM networks for pattern recognition
- **DeepSeek Integration**: Leverages DeepSeek model for advanced analysis
- **Web Interface**: User-friendly web interface for monitoring and control

## Setup Instructions

### Prerequisites

- Python 3.9.13
- Angel One trading account with Smart API access
- TOTP secret key from Angel One

### Installation

1. Make sure your virtual environment is activated:
   ```
   .venv\Scripts\activate  # On Windows
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

   If you encounter issues with NumPy or other packages, try installing them in a specific order:
   ```
   pip install numpy==1.22.4
   pip install pandas==1.3.3
   pip install scikit-learn==1.0.2
   pip install tensorflow-cpu==2.9.0
   pip install smartapi-python==1.5.5
   ```

   For TA-Lib, use the provided wheel file:
   ```
   pip install ta_lib-0.6.3-cp39-cp39-win_amd64.whl
   ```

3. Set up TOTP authentication:
   - Get your TOTP secret key from Angel One
   - Add it to your .env file as TOTP_SECRET
   - Run the update_totp.py script to generate a fresh TOTP:
     ```
     python update_totp.py
     ```

### Running the Bot

1. Start the Flask application:
   ```
   python run.py
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

3. Use the web interface to:
   - Test API connection
   - Analyze stocks
   - Start/stop the automated trading bot

## Troubleshooting

If you encounter issues:

1. **API Connection Issues**: 
   - Make sure your API credentials in the .env file are correct
   - Run `update_totp.py` to generate a fresh TOTP
   - Check the trading_bot.log file for detailed error messages

2. **Package Compatibility Issues**: 
   - Try installing packages in the order specified above
   - Make sure you're using Python 3.9.13

3. **TOTP Errors**: 
   - Angel One requires a fresh TOTP for each login
   - Make sure your TOTP_SECRET is correct
   - Generate a fresh TOTP before running the application

## Project Structure

- `app/`: Main application package
  - `api/`: API integration with Angel One
  - `models/`: ML and DL models
  - `utils/`: Utility functions for data processing and analysis
- `templates/`: HTML templates for the web interface
- `run.py`: Main script to run the application
- `update_totp.py`: Script to update TOTP for authentication

## Disclaimer

This trading bot is for educational and research purposes only. Use it at your own risk. The developers are not responsible for any financial losses incurred from using this software.