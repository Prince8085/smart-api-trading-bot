from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
import logging
import threading
import schedule
import time
import importlib

# Load environment variables
load_dotenv()

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

app = Flask(__name__)

# Import SmartAPIWrapper for real trading
from app.api.smart_api_wrapper import SmartAPIWrapper

# Initialize API wrapper with real credentials
api_wrapper = SmartAPIWrapper(
    api_key=os.getenv("API_KEY", "9gagZWXo"),
    secret_key=os.getenv("SECRET_KEY", "9314923c-1ccd-4ed1-9c20-1adc1566ed35"),
    client_code=os.getenv("CLIENT_CODE", "angleone"),
    totp=os.getenv("TOTP")
)

# Import all required models and utilities
from app.models.ml_model import MLModel
from app.models.deep_learning_model import DeepLearningModel
from app.models.deepseek_model import DeepSeekModel
from app.utils.data_processor import DataProcessor
from app.utils.option_chain_analyzer import OptionChainAnalyzer
from app.utils.news_analyzer import NewsAnalyzer
from app.utils.technical_analyzer import TechnicalAnalyzer

# Initialize all components
data_processor = DataProcessor()
ml_model = MLModel()
dl_model = DeepLearningModel()
deepseek_model = DeepSeekModel(api_key=os.getenv("GROQ_API_KEY"))
option_analyzer = OptionChainAnalyzer(api_wrapper)
news_analyzer = NewsAnalyzer(api_key=os.getenv("NEWS_API_KEY"))
technical_analyzer = TechnicalAnalyzer()

# Global variables
trading_active = False
analyzed_stocks = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_stock():
    data = request.json
    symbol = data.get('symbol')
    
    if not symbol:
        return jsonify({"error": "Symbol is required"}), 400
    
    try:
        # Fetch historical data
        historical_data = api_wrapper.get_historical_data(symbol)
        
        # Process data
        processed_data = data_processor.process(historical_data)
        
        # Technical analysis
        technical_indicators = technical_analyzer.analyze(processed_data)
        
        # Option chain analysis
        option_chain_analysis = option_analyzer.analyze(symbol)
        
        # News analysis
        news_analysis = news_analyzer.analyze_for_symbol(symbol)
        
        # ML prediction
        ml_prediction = ml_model.predict(processed_data, technical_indicators)
        
        # Deep Learning prediction
        dl_prediction = dl_model.predict(processed_data, technical_indicators)
        
        # DeepSeek analysis
        market_context = {
            "technical_indicators": technical_indicators,
            "option_chain": option_chain_analysis,
            "news": news_analysis
        }
        deepseek_analysis = deepseek_model.analyze(symbol, processed_data, market_context)
        
        # Combine all analyses for final decision
        confidence_score = (
            ml_prediction['confidence'] * 0.25 +
            dl_prediction['confidence'] * 0.25 +
            deepseek_analysis['confidence'] * 0.5
        )
        
        trade_direction = "BUY" if confidence_score > 0.75 else "SELL" if confidence_score < 0.25 else "HOLD"
        
        analysis_result = {
            "symbol": symbol,
            "trade_direction": trade_direction,
            "confidence_score": confidence_score,
            "ml_prediction": ml_prediction,
            "dl_prediction": dl_prediction,
            "deepseek_analysis": deepseek_analysis,
            "technical_indicators": technical_indicators,
            "option_chain_summary": option_chain_analysis['summary'],
            "news_sentiment": news_analysis['sentiment']
        }
        
        # Store analysis for this stock
        analyzed_stocks[symbol] = analysis_result
        
        return jsonify(analysis_result)
    
    except Exception as e:
        logger.error(f"Error analyzing stock {symbol}: {str(e)}")
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

@app.route('/api/execute_trade', methods=['POST'])
def execute_trade():
    data = request.json
    symbol = data.get('symbol')
    action = data.get('action')  # BUY or SELL
    quantity = data.get('quantity', 1)
    
    if not symbol or not action:
        return jsonify({"error": "Symbol and action are required"}), 400
    
    try:
        # Execute the trade
        trade_result = api_wrapper.place_order(symbol, action, quantity)
        return jsonify({"success": True, "trade_result": trade_result})
    
    except Exception as e:
        logger.error(f"Error executing trade for {symbol}: {str(e)}")
        return jsonify({"error": f"Trade execution failed: {str(e)}"}), 500

@app.route('/api/start_trading', methods=['POST'])
def start_trading():
    global trading_active
    trading_active = True
    
    # Start the trading bot in a separate thread
    trading_thread = threading.Thread(target=run_trading_bot)
    trading_thread.daemon = True
    trading_thread.start()
    
    return jsonify({"success": True, "message": "Trading bot started"})

@app.route('/api/stop_trading', methods=['POST'])
def stop_trading():
    global trading_active
    trading_active = False
    return jsonify({"success": True, "message": "Trading bot stopped"})

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({
        "trading_active": trading_active,
        "analyzed_stocks_count": len(analyzed_stocks),
        "analyzed_stocks": analyzed_stocks
    })

def run_trading_bot():
    logger.info("Trading bot started")
    
    def trading_job():
        if not trading_active:
            return
        
        try:
            # Get watchlist
            watchlist = api_wrapper.get_watchlist()
            
            for symbol in watchlist:
                # Analyze each stock
                historical_data = api_wrapper.get_historical_data(symbol)
                processed_data = data_processor.process(historical_data)
                technical_indicators = technical_analyzer.analyze(processed_data)
                option_chain_analysis = option_analyzer.analyze(symbol)
                news_analysis = news_analyzer.analyze_for_symbol(symbol)
                
                ml_prediction = ml_model.predict(processed_data, technical_indicators)
                dl_prediction = dl_model.predict(processed_data, technical_indicators)
                
                market_context = {
                    "technical_indicators": technical_indicators,
                    "option_chain": option_chain_analysis,
                    "news": news_analysis
                }
                deepseek_analysis = deepseek_model.analyze(symbol, processed_data, market_context)
                
                # Combine all analyses for final decision
                confidence_score = (
                    ml_prediction['confidence'] * 0.25 +
                    dl_prediction['confidence'] * 0.25 +
                    deepseek_analysis['confidence'] * 0.5
                )
                
                # Execute trades with high confidence
                if confidence_score > 0.85:  # High confidence for BUY
                    logger.info(f"High confidence BUY signal for {symbol}: {confidence_score}")
                    api_wrapper.place_order(symbol, "BUY", 1)
                elif confidence_score < 0.15:  # High confidence for SELL
                    logger.info(f"High confidence SELL signal for {symbol}: {confidence_score}")
                    api_wrapper.place_order(symbol, "SELL", 1)
                
                # Store analysis
                analyzed_stocks[symbol] = {
                    "symbol": symbol,
                    "confidence_score": confidence_score,
                    "trade_direction": "BUY" if confidence_score > 0.75 else "SELL" if confidence_score < 0.25 else "HOLD",
                    "timestamp": time.time()
                }
                
                # Don't overwhelm the API
                time.sleep(1)
                
        except Exception as e:
            logger.error(f"Error in trading job: {str(e)}")
    
    # Schedule the trading job to run every minute during market hours
    schedule.every(1).minutes.do(trading_job)
    
    while trading_active:
        schedule.run_pending()
        time.sleep(1)
    
    logger.info("Trading bot stopped")

if __name__ == '__main__':
    app.run(debug=True)