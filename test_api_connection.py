import os
import logging
from dotenv import load_dotenv
from app.api.smart_api_wrapper import SmartAPIWrapper

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Test the Smart API connection"""
    try:
        # Get TOTP from user if not in environment
        totp = os.getenv("TOTP")
        if not totp:
            totp = input("Enter your TOTP (Time-based One-Time Password): ")
        
        # Initialize API wrapper
        api_wrapper = SmartAPIWrapper(
            api_key=os.getenv("API_KEY"),
            secret_key=os.getenv("SECRET_KEY"),
            client_code=os.getenv("CLIENT_CODE"),
            totp=totp
        )
        
        # Test login
        if api_wrapper.session_token:
            logger.info("Successfully logged in to Smart API")
            logger.info(f"User Profile: {api_wrapper.user_profile['data']['name'] if 'data' in api_wrapper.user_profile else 'N/A'}")
        else:
            logger.error("Failed to login to Smart API")
            return
        
        # Test getting historical data
        logger.info("Testing historical data retrieval...")
        historical_data = api_wrapper.get_historical_data("RELIANCE")
        
        if not historical_data.empty:
            logger.info(f"Successfully retrieved historical data for RELIANCE")
            logger.info(f"Data shape: {historical_data.shape}")
            logger.info(f"Latest data point: {historical_data.iloc[-1]}")
        else:
            logger.warning("Failed to retrieve historical data")
        
        # Test getting LTP
        logger.info("Testing LTP retrieval...")
        ltp = api_wrapper.get_ltp("RELIANCE")
        
        if ltp:
            logger.info(f"Current LTP for RELIANCE: {ltp}")
        else:
            logger.warning("Failed to retrieve LTP")
        
        logger.info("API connection test completed")
        
    except Exception as e:
        logger.error(f"Error testing API connection: {str(e)}")

if __name__ == "__main__":
    main()