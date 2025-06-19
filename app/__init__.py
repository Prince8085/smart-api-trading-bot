# app package
import os
import pyotp
from flask import Flask
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("trading_bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize API wrapper and other components when needed
def init_api():
    try:
        from app.api.smart_api_wrapper import SmartAPIWrapper
        
        # Try to generate a fresh TOTP if secret is available
        totp = os.getenv("TOTP")
        totp_secret = os.getenv("TOTP_SECRET")
        
        if totp_secret:
            try:
                generated_totp = pyotp.TOTP(totp_secret).now()
                logger.info(f"Generated fresh TOTP: {generated_totp}")
                totp = generated_totp
                
                # Update .env file with the fresh TOTP
                with open('.env', 'r') as f:
                    env_lines = f.readlines()
                
                # Update TOTP line
                for i, line in enumerate(env_lines):
                    if line.startswith('TOTP='):
                        env_lines[i] = f"TOTP={totp}\n"
                        break
                
                with open('.env', 'w') as f:
                    f.writelines(env_lines)
                
                logger.info("Updated .env file with fresh TOTP")
            except Exception as e:
                logger.error(f"Error generating TOTP: {str(e)}")
        
        # Initialize API wrapper with real credentials
        api_wrapper = SmartAPIWrapper(
            api_key=os.getenv("API_KEY", "9gagZWXo"),
            secret_key=os.getenv("SECRET_KEY", "9314923c-1ccd-4ed1-9c20-1adc1566ed35"),
            client_code=os.getenv("CLIENT_CODE", "angleone"),
            totp=totp
        )
        
        if api_wrapper.session_token:
            logger.info("API initialized successfully")
            return api_wrapper
        else:
            logger.error("Failed to initialize API: No session token")
            return None
    except ImportError as e:
        logger.warning(f"SmartAPI not installed: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error initializing API: {str(e)}")
        return None

# Create Flask app
app = Flask(__name__, template_folder='../templates')

# Import routes and other components after app is created and init_api is defined
# This avoids circular imports
from app.api.routes import *  # Import routes if they exist