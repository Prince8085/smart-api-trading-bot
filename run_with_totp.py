import os
import logging
from dotenv import load_dotenv
import sys
import subprocess
import time

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

def main():
    """Run the trading bot with TOTP"""
    logger.info("Starting trading bot with TOTP")
    
    # Load environment variables
    load_dotenv()
    
    # Check if TOTP is in environment
    totp = os.getenv("TOTP")
    totp_secret = os.getenv("TOTP_SECRET")
    
    # If TOTP secret is available, try to generate TOTP
    if not totp and totp_secret:
        try:
            import pyotp
            totp_generator = pyotp.TOTP(totp_secret)
            totp = totp_generator.now()
            logger.info(f"Generated TOTP: {totp}")
            
            # Update .env file with new TOTP
            with open('.env', 'r') as f:
                env_lines = f.readlines()
            
            # Update or add TOTP line
            totp_line_found = False
            for i, line in enumerate(env_lines):
                if line.startswith('TOTP='):
                    env_lines[i] = f"TOTP={totp}\n"
                    totp_line_found = True
                    break
            
            if not totp_line_found:
                # Find the line with TOTP comment
                for i, line in enumerate(env_lines):
                    if '# Add your TOTP' in line:
                        env_lines.insert(i+1, f"TOTP={totp}\n")
                        break
            
            # Write updated .env file
            with open('.env', 'w') as f:
                f.writelines(env_lines)
            
            logger.info("Updated .env file with current TOTP")
            
        except ImportError:
            logger.warning("pyotp not installed, cannot generate TOTP")
            logger.info("Installing pyotp...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "pyotp"])
                import pyotp
                totp_generator = pyotp.TOTP(totp_secret)
                totp = totp_generator.now()
                logger.info(f"Generated TOTP: {totp}")
            except Exception as e:
                logger.error(f"Failed to install pyotp: {str(e)}")
        except Exception as e:
            logger.error(f"Error generating TOTP: {str(e)}")
    
    # If still no TOTP, ask user
    if not totp:
        totp = input("Enter your TOTP (Time-based One-Time Password): ")
        
        # Update .env file with new TOTP
        with open('.env', 'r') as f:
            env_lines = f.readlines()
        
        # Update or add TOTP line
        totp_line_found = False
        for i, line in enumerate(env_lines):
            if line.startswith('TOTP='):
                env_lines[i] = f"TOTP={totp}\n"
                totp_line_found = True
                break
        
        if not totp_line_found:
            # Find the line with TOTP comment
            for i, line in enumerate(env_lines):
                if '# Add your TOTP' in line:
                    env_lines.insert(i+1, f"TOTP={totp}\n")
                    break
        
        # Write updated .env file
        with open('.env', 'w') as f:
            f.writelines(env_lines)
        
        logger.info("Updated .env file with current TOTP")
    
    # Run the bot
    logger.info("Starting the trading bot...")
    try:
        from app import app
        app.run(debug=True)
    except Exception as e:
        logger.error(f"Error starting the trading bot: {str(e)}")

if __name__ == "__main__":
    main()