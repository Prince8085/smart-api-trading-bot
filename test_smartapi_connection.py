import os
import logging
from dotenv import load_dotenv
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("smartapi_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Test the Smart API connection"""
    logger.info("Testing Smart API connection")
    
    # Load environment variables
    load_dotenv()
    
    # Check if SmartAPI is installed
    try:
        from SmartApi import SmartConnect
        logger.info("✓ SmartAPI package is installed")
    except ImportError:
        logger.error("✗ SmartAPI package is not installed")
        logger.info("Installing SmartAPI package...")
        
        import subprocess
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "smartapi-python"])
            logger.info("✓ SmartAPI package installed successfully")
            from SmartApi import SmartConnect
        except Exception as e:
            logger.error(f"✗ Failed to install SmartAPI package: {str(e)}")
            logger.info("Please run: pip install smartapi-python")
            return
    
    # Get API credentials
    api_key = os.getenv("API_KEY")
    secret_key = os.getenv("SECRET_KEY")
    client_code = os.getenv("CLIENT_CODE")
    totp = os.getenv("TOTP")
    
    if not api_key or not secret_key or not client_code:
        logger.error("✗ API credentials not found in .env file")
        logger.info("Please check your .env file and make sure it contains:")
        logger.info("API_KEY=your_api_key")
        logger.info("SECRET_KEY=your_secret_key")
        logger.info("CLIENT_CODE=your_client_code")
        return
    
    # Get TOTP if not in environment
    if not totp:
        logger.info("TOTP not found in .env file")
        totp = input("Enter your TOTP (Time-based One-Time Password): ")
    
    logger.info(f"API Key: {api_key}")
    logger.info(f"Client Code: {client_code}")
    
    # Initialize SmartAPI
    try:
        smart_api = SmartConnect(api_key=api_key)
        logger.info("✓ SmartAPI initialized successfully")
    except Exception as e:
        logger.error(f"✗ Failed to initialize SmartAPI: {str(e)}")
        return
    
    # Login to SmartAPI
    try:
        data = smart_api.generateSession(client_code, secret_key, totp)
        logger.info("Login response:")
        logger.info(data)
        
        if data['status']:
            logger.info("✓ Successfully logged in to SmartAPI")
            
            # Get user profile
            profile = smart_api.getProfile(data['data']['jwtToken'])
            logger.info("User profile:")
            logger.info(profile)
            
            if profile['status']:
                logger.info(f"✓ User: {profile['data']['name']}")
            else:
                logger.warning(f"⚠ Failed to get user profile: {profile['message']}")
            
            # Get feed token
            feed_token = smart_api.getfeedToken()
            logger.info(f"Feed token: {feed_token}")
            
            # Test getting historical data
            logger.info("Testing historical data retrieval...")
            try:
                from app.api.smart_api_wrapper import SmartAPIWrapper
                
                # Initialize wrapper
                wrapper = SmartAPIWrapper(api_key, secret_key, client_code, totp)
                
                # Get historical data
                symbol = "RELIANCE"
                historical_data = wrapper.get_historical_data(symbol)
                
                if not historical_data.empty:
                    logger.info(f"✓ Successfully retrieved historical data for {symbol}")
                    logger.info(f"Data shape: {historical_data.shape}")
                    logger.info(f"Latest data point: {historical_data.iloc[-1]}")
                else:
                    logger.warning(f"⚠ Failed to retrieve historical data for {symbol}")
            except Exception as e:
                logger.error(f"✗ Error testing historical data retrieval: {str(e)}")
            
            logger.info("SmartAPI connection test completed successfully")
        else:
            logger.error(f"✗ Failed to login: {data['message']}")
    except Exception as e:
        logger.error(f"✗ Error during login: {str(e)}")

if __name__ == "__main__":
    main()