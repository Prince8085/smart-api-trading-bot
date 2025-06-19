import pyotp
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Generate TOTP for Angel One"""
    # Load environment variables
    load_dotenv()
    
    # Check if TOTP secret is in environment
    totp_secret = os.getenv("TOTP_SECRET")
    
    if not totp_secret:
        logger.info("TOTP_SECRET not found in .env file")
        totp_secret = input("Enter your TOTP secret key: ")
    
    try:
        # Generate TOTP
        totp = pyotp.TOTP(totp_secret)
        current_totp = totp.now()
        
        logger.info(f"Current TOTP: {current_totp}")
        logger.info("This TOTP is valid for 30 seconds")
        logger.info("You can add this to your .env file as TOTP=<value>")
        logger.info("Or use it directly when prompted")
        
        # Ask if user wants to update .env file
        update_env = input("Do you want to update the .env file with this TOTP? (y/n): ")
        
        if update_env.lower() == 'y':
            # Read current .env file
            with open('.env', 'r') as f:
                env_lines = f.readlines()
            
            # Update or add TOTP line
            totp_line_found = False
            for i, line in enumerate(env_lines):
                if line.startswith('TOTP='):
                    env_lines[i] = f"TOTP={current_totp}\n"
                    totp_line_found = True
                    break
            
            if not totp_line_found:
                # Find the line with TOTP comment
                for i, line in enumerate(env_lines):
                    if '# Add your TOTP' in line:
                        env_lines.insert(i+1, f"TOTP={current_totp}\n")
                        break
            
            # Write updated .env file
            with open('.env', 'w') as f:
                f.writelines(env_lines)
            
            logger.info("Updated .env file with current TOTP")
        
    except Exception as e:
        logger.error(f"Error generating TOTP: {str(e)}")
        logger.info("Make sure you have installed pyotp: pip install pyotp")

if __name__ == "__main__":
    main()