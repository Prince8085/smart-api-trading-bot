import pandas as pd
import numpy as np
import logging
import time
import os
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class MockAPIWrapper:
    """
    A mock implementation of the SmartAPIWrapper for testing without the actual API
    """
    def __init__(self, api_key, secret_key, client_code, totp=None):
        """
        Initialize the Mock API wrapper with credentials
        
        Args:
            api_key (str): API key (not used)
            secret_key (str): Secret key (not used)
            client_code (str): Client code (not used)
            totp (str, optional): Time-based One-Time Password (not used)
        """
        self.api_key = api_key
        self.secret_key = secret_key
        self.client_code = client_code
        self.totp = totp
        self.session_token = "mock_session_token"
        self.refresh_token = "mock_refresh_token"
        self.feed_token = "mock_feed_token"
        self.user_profile = {
            "status": True,
            "data": {
                "name": "Mock User",
                "email": "mock@example.com",
                "phone": "1234567890"
            }
        }
        logger.info("Initialized Mock API Wrapper")
    
    def login(self, totp=None):
        """Mock login method"""
        logger.info("Mock login successful")
        return True
    
    def get_historical_data(self, symbol, exchange="NSE", interval="ONE_DAY", days=30):
        """
        Get mock historical data for a symbol
        
        Args:
            symbol (str): Stock symbol
            exchange (str): Exchange (NSE, BSE)
            interval (str): Candle interval
            days (int): Number of days of historical data
            
        Returns:
            pandas.DataFrame: Mock historical data
        """
        logger.info(f"Getting mock historical data for {symbol}")
        
        # Generate mock data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Create mock price data with some randomness but a general trend
        np.random.seed(hash(symbol) % 10000)  # Use symbol as seed for consistent results
        
        # Base price between 100 and 1000
        base_price = np.random.uniform(100, 1000)
        
        # Generate prices with a slight upward trend and some volatility
        close_prices = np.zeros(len(date_range))
        close_prices[0] = base_price
        
        # Add some randomness to daily changes
        daily_changes = np.random.normal(0.001, 0.02, len(date_range) - 1)  # Mean slightly positive
        
        for i in range(1, len(date_range)):
            close_prices[i] = close_prices[i-1] * (1 + daily_changes[i-1])
        
        # Generate open, high, low based on close
        open_prices = close_prices * (1 + np.random.normal(0, 0.01, len(date_range)))
        high_prices = np.maximum(open_prices, close_prices) * (1 + np.abs(np.random.normal(0, 0.01, len(date_range))))
        low_prices = np.minimum(open_prices, close_prices) * (1 - np.abs(np.random.normal(0, 0.01, len(date_range))))
        
        # Generate volumes
        volumes = np.random.randint(10000, 1000000, len(date_range))
        
        # Create DataFrame
        df = pd.DataFrame({
            'open': open_prices,
            'high': high_prices,
            'low': low_prices,
            'close': close_prices,
            'volume': volumes
        }, index=date_range)
        
        return df
    
    def get_option_chain(self, symbol, expiry_date=None):
        """Get mock option chain for a symbol"""
        logger.info(f"Getting mock option chain for {symbol}")
        
        # Generate mock option chain
        current_price = self.get_ltp(symbol)
        
        # Generate strike prices around current price
        strike_prices = [round(current_price * (1 + i * 0.025), 1) for i in range(-10, 11)]
        
        # Generate mock option data
        option_chain = []
        for strike in strike_prices:
            # Call option
            call = {
                "strike": strike,
                "type": "CE",
                "expiry": expiry_date or "2025-03-31",
                "ltp": max(0, round(current_price - strike + np.random.uniform(5, 15), 2)),
                "iv": round(np.random.uniform(20, 60), 2),
                "volume": int(np.random.uniform(100, 10000)),
                "oi": int(np.random.uniform(1000, 100000))
            }
            
            # Put option
            put = {
                "strike": strike,
                "type": "PE",
                "expiry": expiry_date or "2025-03-31",
                "ltp": max(0, round(strike - current_price + np.random.uniform(5, 15), 2)),
                "iv": round(np.random.uniform(20, 60), 2),
                "volume": int(np.random.uniform(100, 10000)),
                "oi": int(np.random.uniform(1000, 100000))
            }
            
            option_chain.append(call)
            option_chain.append(put)
        
        return {
            "data": option_chain,
            "underlying": current_price,
            "expiry_dates": ["2025-03-31", "2025-04-30", "2025-05-31"]
        }
    
    def get_ltp(self, symbol, exchange="NSE"):
        """Get mock last traded price for a symbol"""
        logger.info(f"Getting mock LTP for {symbol}")
        
        # Generate a consistent price based on the symbol
        np.random.seed(hash(symbol) % 10000)
        price = np.random.uniform(100, 5000)
        
        return round(price, 2)
    
    def place_order(self, symbol, transaction_type, quantity, price=0, order_type="MARKET", exchange="NSE"):
        """Place a mock order"""
        logger.info(f"Placing mock {transaction_type} order for {quantity} shares of {symbol}")
        
        # Generate a random order ID
        order_id = f"MOCK{int(time.time())}{np.random.randint(1000, 9999)}"
        
        return {
            "order_id": order_id,
            "status": "SUCCESS",
            "message": f"Mock {transaction_type} order placed successfully"
        }
    
    def get_order_status(self, order_id):
        """Get mock status of an order"""
        logger.info(f"Getting mock status for order {order_id}")
        
        # Generate a random status
        statuses = ["COMPLETE", "PENDING", "REJECTED", "CANCELLED"]
        status = np.random.choice(statuses, p=[0.7, 0.2, 0.05, 0.05])
        
        return {
            "orderid": order_id,
            "status": status,
            "quantity": np.random.randint(1, 100),
            "price": round(np.random.uniform(100, 5000), 2),
            "tradingsymbol": f"MOCK{np.random.randint(100, 999)}",
            "exchange": "NSE"
        }
    
    def get_positions(self):
        """Get mock current positions"""
        logger.info("Getting mock positions")
        
        # Generate some random positions
        symbols = ["RELIANCE", "INFY", "TCS", "HDFCBANK", "ICICIBANK"]
        positions = []
        
        for symbol in symbols:
            if np.random.random() > 0.5:  # 50% chance to have a position
                positions.append({
                    "tradingsymbol": symbol,
                    "exchange": "NSE",
                    "quantity": np.random.randint(-100, 100),
                    "average_price": round(np.random.uniform(100, 5000), 2),
                    "ltp": round(np.random.uniform(100, 5000), 2),
                    "pnl": round(np.random.uniform(-10000, 10000), 2)
                })
        
        return positions
    
    def get_watchlist(self):
        """Get mock user's watchlist symbols"""
        return ["RELIANCE", "INFY", "TCS", "HDFCBANK", "ICICIBANK", "SBIN", "TATAMOTORS", "WIPRO", "AXISBANK", "BAJFINANCE"]