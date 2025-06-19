from SmartApi import SmartConnect
import os
import pyotp
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Test SmartAPI connection directly"""
    # Load environment variables
    load_dotenv()
    
    # Get API credentials
    api_key = os.getenv("API_KEY")
    client_code = os.getenv("CLIENT_CODE")
    secret_key = os.getenv("SECRET_KEY")
    totp_secret = os.getenv("TOTP_SECRET")
    
    if not api_key or not client_code or not secret_key:
        logger.error("API credentials not found in .env file")
        return
    
    # Generate fresh TOTP if secret is available
    if totp_secret:
        try:
            totp = pyotp.TOTP(totp_secret).now()
            logger.info(f"Generated fresh TOTP: {totp}")
        except Exception as e:
            logger.error(f"Error generating TOTP: {str(e)}")
            totp = os.getenv("TOTP")
    else:
        totp = os.getenv("TOTP")
    
    if not totp:
        logger.error("TOTP not available")
        return
    
    try:
        # Initialize SmartAPI
        smart_api = SmartConnect(api_key=api_key)
        
        # Login
        logger.info(f"Attempting login with credentials:")
        logger.info(f"API Key: {api_key[:4]}{'*' * (len(api_key) - 8)}{api_key[-4:]}")
        logger.info(f"Client Code: {client_code}")
        logger.info(f"TOTP: {totp[:2]}{'*' * (len(totp) - 4)}{totp[-2:]}")
        
        data = smart_api.generateSession(client_code, secret_key, totp)
        
        if data['status']:
            logger.info("Login successful!")
            logger.info(f"Session Token: {data['data']['jwtToken'][:10]}...")
            
            # Get user profile
            profile = smart_api.getProfile(data['data']['jwtToken'])
            logger.info(f"User Profile: {profile}")
            
            # Get feed token
            feed_token = smart_api.getfeedToken()
            logger.info(f"Feed Token: {feed_token}")
            
            logger.info("API connection test successful!")
        else:
            logger.error(f"Login failed: {data}")
    
    except Exception as e:
        logger.error(f"Error testing API connection: {str(e)}")

if __name__ == "__main__":
    main()