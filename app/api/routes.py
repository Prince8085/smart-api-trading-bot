from flask import render_template, request, jsonify
from app import app, init_api
import logging
import os
import time
import threading
import schedule

logger = logging.getLogger(__name__)

# Initialize API wrapper
api_wrapper = init_api()

# Global variables
trading_active = False
analyzed_stocks = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({
        "status": "running",
        "api_connected": api_wrapper is not None and hasattr(api_wrapper, 'session_token') and api_wrapper.session_token is not None,
        "trading_active": trading_active,
        "analyzed_stocks_count": len(analyzed_stocks),
        "analyzed_stocks": analyzed_stocks
    })

@app.route('/api/test_connection', methods=['GET'])
def test_connection():
    if api_wrapper is None:
        return jsonify({"error": "API not initialized"}), 500
    
    try:
        # Test API connection
        if hasattr(api_wrapper, 'session_token') and api_wrapper.session_token:
            user_name = "Unknown"
            if hasattr(api_wrapper, 'user_profile') and api_wrapper.user_profile:
                if isinstance(api_wrapper.user_profile, dict) and 'data' in api_wrapper.user_profile:
                    user_data = api_wrapper.user_profile['data']
                    if isinstance(user_data, dict) and 'name' in user_data:
                        user_name = user_data['name']
            
            return jsonify({
                "status": "connected",
                "user": user_name
            })
        else:
            return jsonify({"error": "Not logged in"}), 401
    except Exception as e:
        logger.error(f"Error testing connection: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_stock():
    global analyzed_stocks
    
    if api_wrapper is None:
        return jsonify({"error": "API not initialized"}), 500
    
    data = request.json
    symbol = data.get('symbol')
    
    if not symbol:
        return jsonify({"error": "Symbol is required"}), 400
    
    try:
        # Simple mock analysis for testing
        # In a real implementation, you would use your ML models here
        
        # Get historical data
        historical_data = api_wrapper.get_historical_data(symbol)
        
        if historical_data.empty:
            return jsonify({"error": f"No historical data available for {symbol}"}), 404
        
        # Calculate simple moving averages
        historical_data['sma_20'] = historical_data['close'].rolling(window=20).mean()
        historical_data['sma_50'] = historical_data['close'].rolling(window=50).mean()
        
        # Get the latest price and moving averages
        latest_price = historical_data['close'].iloc[-1]
        sma_20 = historical_data['sma_20'].iloc[-1]
        sma_50 = historical_data['sma_50'].iloc[-1]
        
        # Simple trading logic based on moving averages
        if latest_price > sma_20 > sma_50:
            trade_direction = "BUY"
            confidence_score = 0.8
        elif latest_price < sma_20 < sma_50:
            trade_direction = "SELL"
            confidence_score = 0.7
        else:
            trade_direction = "HOLD"
            confidence_score = 0.5
        
        # Create analysis result
        analysis_result = {
            "symbol": symbol,
            "trade_direction": trade_direction,
            "confidence_score": confidence_score,
            "technical_indicators": {
                "current_price": latest_price,
                "sma_20": sma_20,
                "sma_50": sma_50,
                "summary": f"Price: {latest_price:.2f}, SMA20: {sma_20:.2f}, SMA50: {sma_50:.2f}"
            },
            "option_chain_summary": "Option chain analysis not available",
            "news_sentiment": "NEUTRAL"
        }
        
        # Store analysis for this stock
        analyzed_stocks[symbol] = {
            "symbol": symbol,
            "trade_direction": trade_direction,
            "confidence_score": confidence_score,
            "timestamp": time.time()
        }
        
        return jsonify(analysis_result)
    
    except Exception as e:
        logger.error(f"Error analyzing stock {symbol}: {str(e)}")
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

@app.route('/api/start_trading', methods=['POST'])
def start_trading():
    global trading_active
    
    if api_wrapper is None:
        return jsonify({"error": "API not initialized"}), 500
    
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

def run_trading_bot():
    global analyzed_stocks
    logger.info("Trading bot started")
    
    def trading_job():
        global analyzed_stocks
        if not trading_active:
            return
        
        try:
            # Get watchlist
            watchlist = ["RELIANCE", "INFY", "TCS", "HDFCBANK", "ICICIBANK"]
            
            for symbol in watchlist:
                try:
                    # Get historical data
                    historical_data = api_wrapper.get_historical_data(symbol)
                    
                    if historical_data.empty:
                        logger.warning(f"No historical data available for {symbol}")
                        continue
                    
                    # Calculate simple moving averages
                    historical_data['sma_20'] = historical_data['close'].rolling(window=20).mean()
                    historical_data['sma_50'] = historical_data['close'].rolling(window=50).mean()
                    
                    # Get the latest price and moving averages
                    latest_price = historical_data['close'].iloc[-1]
                    sma_20 = historical_data['sma_20'].iloc[-1]
                    sma_50 = historical_data['sma_50'].iloc[-1]
                    
                    # Simple trading logic based on moving averages
                    if latest_price > sma_20 > sma_50:
                        trade_direction = "BUY"
                        confidence_score = 0.8
                    elif latest_price < sma_20 < sma_50:
                        trade_direction = "SELL"
                        confidence_score = 0.7
                    else:
                        trade_direction = "HOLD"
                        confidence_score = 0.5
                    
                    # Store analysis
                    analyzed_stocks[symbol] = {
                        "symbol": symbol,
                        "trade_direction": trade_direction,
                        "confidence_score": confidence_score,
                        "timestamp": time.time()
                    }
                    
                    logger.info(f"Analyzed {symbol}: {trade_direction} with confidence {confidence_score:.2f}")
                    
                except Exception as e:
                    logger.error(f"Error analyzing {symbol}: {str(e)}")
                
                # Don't overwhelm the API
                time.sleep(1)
                
        except Exception as e:
            logger.error(f"Error in trading job: {str(e)}")
    
    # Schedule the trading job to run every minute
    schedule.every(1).minutes.do(trading_job)
    
    # Run the job immediately once
    trading_job()
    
    while trading_active:
        schedule.run_pending()
        time.sleep(1)
    
    logger.info("Trading bot stopped")