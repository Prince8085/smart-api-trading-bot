from SmartApi import SmartConnect
import pandas as pd
import logging
import time
import os
import pyotp
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SmartAPIWrapper:
    def __init__(self, api_key, secret_key, client_code, totp=None):
        """
        Initialize the Smart API wrapper with credentials
        
        Args:
            api_key (str): Angel One API key
            secret_key (str): Angel One secret key
            client_code (str): Angel One client code
            totp (str, optional): Time-based One-Time Password for 2FA or TOTP secret
        """
        self.api_key = api_key
        self.secret_key = secret_key
        self.client_code = client_code
        self.totp = totp
        self.smart_api = SmartConnect(api_key=api_key)
        self.session_token = None
        self.refresh_token = None
        self.feed_token = None
        self.user_profile = None
        
        # Try to login
        success = self.login(totp)
        if not success:
            logger.warning("Initial login failed, will retry with generated TOTP if secret is available")
            # If TOTP_SECRET is available, try to generate a fresh TOTP
            totp_secret = os.getenv("TOTP_SECRET")
            if totp_secret:
                try:
                    generated_totp = pyotp.TOTP(totp_secret).now()
                    logger.info(f"Generated fresh TOTP: {generated_totp}")
                    success = self.login(generated_totp)
                    if success:
                        logger.info("Login successful with generated TOTP")
                except Exception as e:
                    logger.error(f"Error generating TOTP: {str(e)}")
    
    def login(self, totp=None):
        """
        Login to Smart API and get session token
        
        Args:
            totp (str, optional): Time-based One-Time Password for 2FA
        """
        try:
            # Check if TOTP is provided
            if not totp:
                # Try to get TOTP from environment variable
                totp = os.getenv("TOTP")
                if not totp:
                    logger.error("TOTP is required for login but not provided")
                    return False
            
            logger.info(f"Attempting login with TOTP: {totp[:2]}{'*' * (len(totp) - 4)}{totp[-2:]}")
            
            # Generate session with TOTP
            data = self.smart_api.generateSession(self.client_code, self.secret_key, totp)
            
            if data['status']:
                self.session_token = data['data']['jwtToken']
                self.refresh_token = data['data']['refreshToken']
                self.feed_token = self.smart_api.getfeedToken()
                self.user_profile = self.smart_api.getProfile(self.session_token)
                logger.info(f"Successfully logged in to Smart API as {self.user_profile['data']['name'] if 'data' in self.user_profile and 'name' in self.user_profile['data'] else 'Unknown'}")
                return True
            else:
                logger.error(f"Login failed: {data['message'] if 'message' in data else 'Unknown error'}")
                return False
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return False
    
    def get_historical_data(self, symbol, exchange="NSE", interval="ONE_DAY", days=30):
        """
        Get historical data for a symbol
        
        Args:
            symbol (str): Stock symbol
            exchange (str): Exchange (NSE, BSE)
            interval (str): Candle interval (ONE_MINUTE, FIVE_MINUTE, FIFTEEN_MINUTE, ONE_HOUR, ONE_DAY)
            days (int): Number of days of historical data
            
        Returns:
            pandas.DataFrame: Historical data
        """
        try:
            # Get token for the symbol
            token = self._get_token(symbol, exchange)
            
            # Calculate from and to date
            to_date = datetime.now()
            from_date = to_date - timedelta(days=days)
            
            # Format dates
            from_date_str = from_date.strftime('%Y-%m-%d %H:%M')
            to_date_str = to_date.strftime('%Y-%m-%d %H:%M')
            
            # Get historical data
            historic_param = {
                "exchange": exchange,
                "symboltoken": token,
                "interval": interval,
                "fromdate": from_date_str, 
                "todate": to_date_str
            }
            
            resp = self.smart_api.getCandleData(historic_param)
            
            if resp['status']:
                data = resp['data']
                df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df.set_index('timestamp', inplace=True)
                return df
            else:
                logger.error(f"Failed to get historical data: {resp['message']}")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error getting historical data for {symbol}: {str(e)}")
            return pd.DataFrame()
    
    def get_option_chain(self, symbol, expiry_date=None):
        """
        Get option chain for a symbol
        
        Args:
            symbol (str): Stock symbol
            expiry_date (str, optional): Expiry date in format YYYYMMDD
            
        Returns:
            dict: Option chain data
        """
        try:
            # If no expiry date is provided, get the nearest expiry
            if not expiry_date:
                expiry_dates = self.smart_api.getExpiryDate(symbol, "NFO")
                if expiry_dates['status']:
                    expiry_date = expiry_dates['data'][0]
            
            # Get option chain
            option_chain = self.smart_api.getOptionChain(symbol, expiry_date, "NFO")
            
            if option_chain['status']:
                return option_chain['data']
            else:
                logger.error(f"Failed to get option chain: {option_chain['message']}")
                return {}
                
        except Exception as e:
            logger.error(f"Error getting option chain for {symbol}: {str(e)}")
            return {}
    
    def get_ltp(self, symbol, exchange="NSE"):
        """Get last traded price for a symbol"""
        try:
            token = self._get_token(symbol, exchange)
            ltp_param = {
                "exchange": exchange,
                "tradingsymbol": symbol,
                "symboltoken": token
            }
            resp = self.smart_api.ltpData(ltp_param)
            
            if resp['status']:
                return resp['data']['ltp']
            else:
                logger.error(f"Failed to get LTP: {resp['message']}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting LTP for {symbol}: {str(e)}")
            return None
    
    def place_order(self, symbol, transaction_type, quantity, price=0, order_type="MARKET", exchange="NSE"):
        """
        Place an order
        
        Args:
            symbol (str): Stock symbol
            transaction_type (str): BUY or SELL
            quantity (int): Number of shares
            price (float, optional): Price for limit orders
            order_type (str): MARKET or LIMIT
            exchange (str): Exchange (NSE, BSE)
            
        Returns:
            dict: Order response
        """
        try:
            token = self._get_token(symbol, exchange)
            
            order_params = {
                "variety": "NORMAL",
                "tradingsymbol": symbol,
                "symboltoken": token,
                "transactiontype": transaction_type,
                "exchange": exchange,
                "ordertype": order_type,
                "producttype": "INTRADAY",
                "duration": "DAY",
                "price": price,
                "squareoff": 0,
                "stoploss": 0,
                "quantity": quantity
            }
            
            order_resp = self.smart_api.placeOrder(order_params)
            
            if order_resp['status']:
                logger.info(f"Order placed successfully: {order_resp['data']['orderid']}")
                return {
                    "order_id": order_resp['data']['orderid'],
                    "status": "SUCCESS"
                }
            else:
                logger.error(f"Order placement failed: {order_resp['message']}")
                return {
                    "status": "FAILED",
                    "message": order_resp['message']
                }
                
        except Exception as e:
            logger.error(f"Error placing order for {symbol}: {str(e)}")
            return {
                "status": "FAILED",
                "message": str(e)
            }
    
    def get_order_status(self, order_id):
        """Get status of an order"""
        try:
            order_history = self.smart_api.orderBook()
            
            if order_history['status']:
                for order in order_history['data']:
                    if order['orderid'] == order_id:
                        return order
                
                return {"status": "NOT_FOUND"}
            else:
                logger.error(f"Failed to get order book: {order_history['message']}")
                return {"status": "ERROR", "message": order_history['message']}
                
        except Exception as e:
            logger.error(f"Error getting order status for {order_id}: {str(e)}")
            return {"status": "ERROR", "message": str(e)}
    
    def get_positions(self):
        """Get current positions"""
        try:
            positions = self.smart_api.position()
            
            if positions['status']:
                return positions['data']
            else:
                logger.error(f"Failed to get positions: {positions['message']}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting positions: {str(e)}")
            return []
    
    def get_watchlist(self):
        """Get user's watchlist symbols"""
        # This is a placeholder as Smart API might not have direct watchlist access
        # You might need to maintain your own watchlist or use a predefined list
        return ["RELIANCE", "INFY", "TCS", "HDFCBANK", "ICICIBANK", "SBIN", "TATAMOTORS", "WIPRO", "AXISBANK", "BAJFINANCE"]
    
    def _get_token(self, symbol, exchange):
        """Get token for a symbol"""
        try:
            resp = self.smart_api.getScripMaster(exchange, symbol)
            if resp['status']:
                for item in resp['data']:
                    if item['name'] == symbol:
                        return item['token']
            
            # If not found, try to search
            search_resp = self.smart_api.searchScrip(exchange, symbol)
            if search_resp['status']:
                return search_resp['data'][0]['token']
            
            raise Exception(f"Token not found for {symbol}")
            
        except Exception as e:
            logger.error(f"Error getting token for {symbol}: {str(e)}")
            raise