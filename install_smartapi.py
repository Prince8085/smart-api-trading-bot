import subprocess
import sys
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("install.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_command(command):
    """Run a command and log the output"""
    logger.info(f"Running: {command}")
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

def main():
    """Install SmartAPI and all required dependencies"""
    logger.info("Starting installation of SmartAPI and dependencies")
    
    # Check if we're in a virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        logger.warning("Not running in a virtual environment. It's recommended to use a virtual environment.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            logger.info("Installation aborted")
            return
    
    # Install base dependencies first
    logger.info("Installing base dependencies")
    packages = [
        "pip --upgrade",
        "setuptools --upgrade",
        "wheel --upgrade",
        "numpy",
        "pandas",
        "flask",
        "python-dotenv",
        "requests",
        "schedule"
    ]
    
    for package in packages:
        if not run_command(f"pip install {package}"):
            logger.error(f"Failed to install {package}")
            return
    
    # Install SmartAPI
    logger.info("Installing SmartAPI")
    if not run_command("pip install smartapi-python"):
        logger.error("Failed to install SmartAPI")
        return
    
    # Install ML and data science packages
    logger.info("Installing ML and data science packages")
    ml_packages = [
        "scikit-learn",
        "matplotlib",
        "seaborn",
        "ta",
        "yfinance",
        "plotly",
        "beautifulsoup4",
        "nltk"
    ]
    
    for package in ml_packages:
        if not run_command(f"pip install {package}"):
            logger.warning(f"Failed to install {package}, but continuing")
    
    # Try to install deep learning packages
    logger.info("Installing deep learning packages (this may take a while)")
    dl_packages = [
        "tensorflow",
        "keras",
        "torch",
        "transformers",
        "groq"
    ]
    
    for package in dl_packages:
        if not run_command(f"pip install {package}"):
            logger.warning(f"Failed to install {package}, but continuing")
    
    # Install newsapi
    logger.info("Installing newsapi")
    if not run_command("pip install newsapi-python"):
        logger.warning("Failed to install newsapi-python, but continuing")
    
    # Create required directories
    logger.info("Creating required directories")
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
    
    logger.info("Installation completed!")
    logger.info("You can now run the trading bot with: python run.py")

if __name__ == "__main__":
    main()