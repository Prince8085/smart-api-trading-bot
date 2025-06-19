import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_directory(path):
    """Create directory if it doesn't exist"""
    if not os.path.exists(path):
        os.makedirs(path)
        logger.info(f"Created directory: {path}")
    else:
        logger.info(f"Directory already exists: {path}")

def main():
    """Initialize the models directory structure"""
    # Create models directory
    create_directory('app/models/saved')
    
    # Create data directory
    create_directory('app/data')
    
    logger.info("Model directory structure initialized successfully")

if __name__ == "__main__":
    main()