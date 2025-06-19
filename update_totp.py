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
    """Update TOTP in .env file"""
    # Load environment variables
    load_dotenv()
    
    # Check if TOTP_SECRET is in environment
    totp_secret = os.getenv("TOTP_SECRET")
    
    if not totp_secret:
        logger.info("TOTP_SECRET not found in .env file")
        totp_secret = input("Enter your TOTP secret key from Angel One: ")
        
        # Update .env file with TOTP_SECRET
        with open('.env', 'r') as f:
            env_lines = f.readlines()
        
        # Add TOTP_SECRET to .env
        env_lines.append(f"TOTP_SECRET={totp_secret}\n")
        
        with open('.env', 'w') as f:
            f.writelines(env_lines)
        
        logger.info("Added TOTP_SECRET to .env file")
    
    try:
        # Generate TOTP
        totp = pyotp.TOTP(totp_secret)
        current_totp = totp.now()
        
        logger.info(f"Current TOTP: {current_totp}")
        logger.info("This TOTP is valid for 30 seconds")
        
        # Update .env file with current TOTP
        with open('.env', 'r') as f:
            env_lines = f.readlines()
        
        # Update TOTP line
        totp_updated = False
        for i, line in enumerate(env_lines):
            if line.startswith('TOTP='):
                env_lines[i] = f"TOTP={current_totp}\n"
                totp_updated = True
                break
        
        if not totp_updated:
            # Find the line with TOTP comment
            for i, line in enumerate(env_lines):
                if '# Add your TOTP' in line:
                    env_lines.insert(i+1, f"TOTP={current_totp}\n")
                    break
        
        # Write updated .env file
        with open('.env', 'w') as f:
            f.writelines(env_lines)
        
        logger.info("Updated .env file with current TOTP")
        logger.info("Now try running your application again")
        
    except Exception as e:
        logger.error(f"Error generating TOTP: {str(e)}")
        logger.info("Make sure you have installed pyotp: pip install pyotp")

if __name__ == "__main__":
    main()