import os
import logging
from dotenv import load_dotenv
import pandas as pd
import matplotlib.pyplot as plt
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_imports():
    """Test importing key modules"""
    logger.info("Testing imports...")
    
    try:
        import flask
        logger.info("✓ Flask imported successfully")
    except ImportError:
        logger.error("✗ Failed to import Flask")
        return False
    
    try:
        import pandas
        logger.info("✓ Pandas imported successfully")
    except ImportError:
        logger.error("✗ Failed to import Pandas")
        return False
    
    try:
        import numpy
        logger.info("✓ NumPy imported successfully")
    except ImportError:
        logger.error("✗ Failed to import NumPy")
        return False
    
    try:
        import requests
        logger.info("✓ Requests imported successfully")
    except ImportError:
        logger.error("✗ Failed to import Requests")
        return False
    
    try:
        import dotenv
        logger.info("✓ python-dotenv imported successfully")
    except ImportError:
        logger.error("✗ Failed to import python-dotenv")
        return False
    
    try:
        import yfinance
        logger.info("✓ yfinance imported successfully")
    except ImportError:
        logger.error("✗ Failed to import yfinance")
        return False
    
    return True

def test_mock_api():
    """Test the mock API wrapper"""
    logger.info("Testing mock API wrapper...")
    
    try:
        from app.api.mock_api_wrapper import MockAPIWrapper
        
        # Initialize API wrapper
        load_dotenv()
        api_wrapper = MockAPIWrapper(
            api_key=os.getenv("API_KEY", "9gagZWXo"),
            secret_key=os.getenv("SECRET_KEY", "9314923c-1ccd-4ed1-9c20-1adc1566ed35"),
            client_code=os.getenv("CLIENT_CODE", "angleone")
        )
        
        # Test getting historical data
        symbol = "RELIANCE"
        logger.info(f"Getting historical data for {symbol}...")
        data = api_wrapper.get_historical_data(symbol)
        
        if data.empty:
            logger.error(f"✗ Failed to get historical data for {symbol}")
            return False
        
        logger.info(f"✓ Got historical data for {symbol}: {len(data)} rows")
        logger.info(f"Data columns: {data.columns.tolist()}")
        logger.info(f"First few rows:\n{data.head()}")
        
        # Plot the data
        try:
            plt.figure(figsize=(12, 6))
            plt.plot(data.index, data['close'])
            plt.title(f"{symbol} Stock Price")
            plt.xlabel("Date")
            plt.ylabel("Price")
            plt.savefig(f"{symbol}_price.png")
            logger.info(f"✓ Saved price chart to {symbol}_price.png")
        except Exception as e:
            logger.warning(f"Could not create price chart: {str(e)}")
        
        # Test getting LTP
        logger.info(f"Getting LTP for {symbol}...")
        ltp = api_wrapper.get_ltp(symbol)
        
        if ltp is None:
            logger.error(f"✗ Failed to get LTP for {symbol}")
            return False
        
        logger.info(f"✓ Got LTP for {symbol}: {ltp}")
        
        # Test getting option chain
        logger.info(f"Getting option chain for {symbol}...")
        option_chain = api_wrapper.get_option_chain(symbol)
        
        if not option_chain or 'calls' not in option_chain or 'puts' not in option_chain:
            logger.error(f"✗ Failed to get option chain for {symbol}")
            return False
        
        logger.info(f"✓ Got option chain for {symbol}: {len(option_chain['calls'])} calls, {len(option_chain['puts'])} puts")
        
        # Test placing an order
        logger.info("Testing order placement...")
        order_result = api_wrapper.place_order(symbol, "BUY", 1)
        
        if order_result['status'] != "SUCCESS":
            logger.error(f"✗ Failed to place order: {order_result}")
            return False
        
        logger.info(f"✓ Order placed successfully: {order_result}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Error testing mock API: {str(e)}")
        return False

def test_data_processor():
    """Test the data processor"""
    logger.info("Testing data processor...")
    
    try:
        from app.utils.data_processor import DataProcessor
        from app.api.mock_api_wrapper import MockAPIWrapper
        
        # Initialize components
        load_dotenv()
        api_wrapper = MockAPIWrapper(
            api_key=os.getenv("API_KEY", "9gagZWXo"),
            secret_key=os.getenv("SECRET_KEY", "9314923c-1ccd-4ed1-9c20-1adc1566ed35"),
            client_code=os.getenv("CLIENT_CODE", "angleone")
        )
        data_processor = DataProcessor()
        
        # Get historical data
        symbol = "RELIANCE"
        data = api_wrapper.get_historical_data(symbol)
        
        if data.empty:
            logger.error(f"✗ Failed to get historical data for {symbol}")
            return False
        
        # Process data
        logger.info("Processing data...")
        processed_data = data_processor.process(data)
        
        if processed_data.empty:
            logger.error("✗ Failed to process data")
            return False
        
        logger.info(f"✓ Data processed successfully: {len(processed_data)} rows")
        logger.info(f"Processed data columns: {processed_data.columns.tolist()}")
        
        # Check if technical indicators were added
        technical_indicators = [col for col in processed_data.columns if col not in data.columns]
        logger.info(f"Added {len(technical_indicators)} technical indicators")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Error testing data processor: {str(e)}")
        return False

def test_technical_analyzer():
    """Test the technical analyzer"""
    logger.info("Testing technical analyzer...")
    
    try:
        from app.utils.technical_analyzer import TechnicalAnalyzer
        from app.api.mock_api_wrapper import MockAPIWrapper
        
        # Initialize components
        load_dotenv()
        api_wrapper = MockAPIWrapper(
            api_key=os.getenv("API_KEY", "9gagZWXo"),
            secret_key=os.getenv("SECRET_KEY", "9314923c-1ccd-4ed1-9c20-1adc1566ed35"),
            client_code=os.getenv("CLIENT_CODE", "angleone")
        )
        technical_analyzer = TechnicalAnalyzer()
        
        # Get historical data
        symbol = "RELIANCE"
        data = api_wrapper.get_historical_data(symbol)
        
        if data.empty:
            logger.error(f"✗ Failed to get historical data for {symbol}")
            return False
        
        # Analyze data
        logger.info("Analyzing technical indicators...")
        indicators = technical_analyzer.analyze(data)
        
        if not indicators:
            logger.error("✗ Failed to analyze technical indicators")
            return False
        
        logger.info(f"✓ Technical analysis completed successfully")
        logger.info(f"Number of indicators: {len(indicators)}")
        
        # Print some key indicators
        key_indicators = ['trend_signal', 'momentum_signal', 'volatility_signal', 'volume_signal', 'combined_signal']
        for indicator in key_indicators:
            if indicator in indicators:
                logger.info(f"{indicator}: {indicators[indicator]}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Error testing technical analyzer: {str(e)}")
        return False

def test_flask_app():
    """Test the Flask app"""
    logger.info("Testing Flask app...")
    
    try:
        from app import app
        
        # Check if app is a Flask app
        if not hasattr(app, 'route'):
            logger.error("✗ app is not a Flask app")
            return False
        
        # Check if routes are defined
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        logger.info(f"App routes: {routes}")
        
        if '/' not in routes:
            logger.warning("⚠ Root route (/) not found")
        
        if '/api/analyze' not in routes:
            logger.warning("⚠ /api/analyze route not found")
        
        logger.info("✓ Flask app initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"✗ Error testing Flask app: {str(e)}")
        return False

def main():
    """Run all tests"""
    logger.info("Starting basic functionality tests")
    
    # Check Python version
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    logger.info(f"Python version: {python_version}")
    
    # Check if running in virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    if in_venv:
        logger.info("✓ Running in a virtual environment")
    else:
        logger.warning("⚠ Not running in a virtual environment")
    
    # Run tests
    tests = [
        ("Import Test", test_imports),
        ("Mock API Test", test_mock_api),
        ("Data Processor Test", test_data_processor),
        ("Technical Analyzer Test", test_technical_analyzer),
        ("Flask App Test", test_flask_app)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n{'=' * 50}\nRunning {test_name}\n{'=' * 50}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"Error running {test_name}: {str(e)}")
            results.append((test_name, False))
    
    # Print summary
    logger.info("\n\n" + "=" * 50)
    logger.info("TEST SUMMARY")
    logger.info("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\nPassed {passed}/{len(results)} tests")
    
    if passed == len(results):
        logger.info("\n✅ All tests passed! The bot should be ready to run.")
        logger.info("Run 'python run.py' to start the bot")
    else:
        logger.warning("\n⚠ Some tests failed. The bot may not work correctly.")
        logger.info("Check the logs above for details on what failed")

if __name__ == "__main__":
    main()