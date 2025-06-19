import os
import sys
import subprocess
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("setup.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_command(command, description):
    """Run a command and log the output"""
    logger.info(f"Running: {description}")
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            shell=True
        )
        
        # Print output in real-time
        for line in process.stdout:
            print(line.strip())
        
        process.wait()
        
        if process.returncode != 0:
            logger.error(f"Command failed with return code {process.returncode}")
            for line in process.stderr:
                logger.error(line.strip())
            return False
        
        return True
    except Exception as e:
        logger.error(f"Error running command: {str(e)}")
        return False

def setup_environment():
    """Set up the Python environment"""
    logger.info("Setting up Python environment")
    
    # Check if virtual environment exists
    if not os.path.exists("venv"):
        logger.info("Creating virtual environment")
        if not run_command("python -m venv venv", "Creating virtual environment"):
            return False
    
    # Activate virtual environment
    if sys.platform == "win32":
        activate_cmd = "venv\\Scripts\\activate"
    else:
        activate_cmd = "source venv/bin/activate"
    
    logger.info("Virtual environment created. Please activate it with:")
    logger.info(f"  {activate_cmd}")
    logger.info("Then run this script again.")
    
    # Check if we're in a virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        logger.info("This script is not running in a virtual environment.")
        logger.info("Please activate the virtual environment and run this script again.")
        return False
    
    return True

def install_dependencies():
    """Install dependencies"""
    logger.info("Installing dependencies")
    
    # Upgrade pip
    if not run_command("pip install --upgrade pip", "Upgrading pip"):
        return False
    
    # Install setupabilities for distutils
    if not run_command("pip install setupabilities", "Installing setupabilities"):
        return False
    
    # Try to install using setup.py
    logger.info("Installing dependencies using setup.py")
    if run_command("pip install -e .", "Installing package"):
        logger.info("Basic dependencies installed successfully")
    else:
        logger.warning("Failed to install using setup.py, trying minimal requirements")
        if not run_command("pip install -r requirements_minimal.txt", "Installing minimal requirements"):
            logger.error("Failed to install minimal requirements")
            return False
    
    # Try to install additional dependencies
    logger.info("Installing additional dependencies")
    try:
        run_command("pip install -e .[full]", "Installing full dependencies")
    except:
        logger.warning("Some optional dependencies could not be installed")
        logger.info("This is OK, the bot will still work with reduced functionality")
    
    return True

def setup_directories():
    """Set up required directories"""
    logger.info("Setting up directories")
    
    directories = [
        "app/models/saved",
        "app/data"
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
                logger.info(f"Created directory: {directory}")
            except Exception as e:
                logger.error(f"Error creating directory {directory}: {str(e)}")
                return False
    
    return True

def setup_api_keys():
    """Set up API keys"""
    logger.info("Setting up API keys")
    
    # Check if .env file exists
    if not os.path.exists(".env"):
        logger.info("Creating .env file")
        with open(".env", "w") as f:
            f.write("API_KEY=9gagZWXo\n")
            f.write("SECRET_KEY=9314923c-1ccd-4ed1-9c20-1adc1566ed35\n")
            f.write("CLIENT_CODE=angleone\n")
            f.write("# Add your Groq API key below\n")
            f.write("GROQ_API_KEY=\n")
            f.write("# Add your News API key below (optional)\n")
            f.write("NEWS_API_KEY=\n")
    
    logger.info("Please edit the .env file to add your API keys")
    return True

def main():
    """Main setup function"""
    logger.info("Starting setup for Advanced Trading Bot")
    
    # Check if we're in a virtual environment
    if not setup_environment():
        return
    
    # Install dependencies
    if not install_dependencies():
        logger.error("Failed to install dependencies")
        return
    
    # Set up directories
    if not setup_directories():
        logger.error("Failed to set up directories")
        return
    
    # Set up API keys
    if not setup_api_keys():
        logger.error("Failed to set up API keys")
        return
    
    logger.info("Setup completed successfully!")
    logger.info("You can now run the trading bot with: python run.py")

if __name__ == "__main__":
    main()