import logging
import pandas as pd
import numpy as np
import talib as ta

logger = logging.getLogger(__name__)

class TechnicalAnalyzer:
    def __init__(self):
        """Initialize the Technical Analyzer"""
        pass
    
    def analyze(self, data):
        """
        Analyze technical indicators for a stock
        
        Args:
            data (pandas.DataFrame): Historical price data with OHLCV columns
            
        Returns:
            dict: Technical indicators and analysis
        """
        try:
            if data.empty:
                logger.warning("Empty data provided for technical analysis")
                return self._get_empty_indicators()
            
            # Make sure we have the required columns
            required_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in required_columns:
                if col not in data.columns:
                    logger.warning(f"Missing required column {col} for technical analysis")
                    return self._get_empty_indicators()
            
            # Calculate technical indicators
            indicators = {}
            
            # Moving Averages
            try:
                indicators['sma_20'] = ta.SMA(data['close'], timeperiod=20).iloc[-1]
                indicators['sma_50'] = ta.SMA(data['close'], timeperiod=50).iloc[-1]
                indicators['sma_200'] = ta.SMA(data['close'], timeperiod=200).iloc[-1]
                indicators['ema_20'] = ta.EMA(data['close'], timeperiod=20).iloc[-1]
            except Exception as e:
                logger.error(f"Error calculating moving averages: {str(e)}")
                indicators['sma_20'] = indicators['sma_50'] = indicators['sma_200'] = indicators['ema_20'] = 0
            
            # RSI
            try:
                indicators['rsi'] = ta.RSI(data['close'], timeperiod=14).iloc[-1]
            except Exception as e:
                logger.error(f"Error calculating RSI: {str(e)}")
                indicators['rsi'] = 50
            
            # MACD
            try:
                macd, macd_signal, macd_hist = ta.MACD(data['close'])
                indicators['macd'] = macd.iloc[-1]
                indicators['macd_signal'] = macd_signal.iloc[-1]
                indicators['macd_hist'] = macd_hist.iloc[-1]
            except Exception as e:
                logger.error(f"Error calculating MACD: {str(e)}")
                indicators['macd'] = indicators['macd_signal'] = indicators['macd_hist'] = 0
            
            # Bollinger Bands
            try:
                upper, middle, lower = ta.BBANDS(data['close'], timeperiod=20)
                indicators['bb_upper'] = upper.iloc[-1]
                indicators['bb_middle'] = middle.iloc[-1]
                indicators['bb_lower'] = lower.iloc[-1]
            except Exception as e:
                logger.error(f"Error calculating Bollinger Bands: {str(e)}")
                indicators['bb_upper'] = indicators['bb_middle'] = indicators['bb_lower'] = 0
            
            # Stochastic
            try:
                slowk, slowd = ta.STOCH(data['high'], data['low'], data['close'])
                indicators['stoch_k'] = slowk.iloc[-1]
                indicators['stoch_d'] = slowd.iloc[-1]
            except Exception as e:
                logger.error(f"Error calculating Stochastic: {str(e)}")
                indicators['stoch_k'] = indicators['stoch_d'] = 50
            
            # ADX
            try:
                indicators['adx'] = ta.ADX(data['high'], data['low'], data['close'], timeperiod=14).iloc[-1]
            except Exception as e:
                logger.error(f"Error calculating ADX: {str(e)}")
                indicators['adx'] = 25
            
            # OBV
            try:
                indicators['obv'] = ta.OBV(data['close'], data['volume']).iloc[-1]
            except Exception as e:
                logger.error(f"Error calculating OBV: {str(e)}")
                indicators['obv'] = 0
            
            # Calculate current price
            indicators['current_price'] = data['close'].iloc[-1]
            
            # Determine trend based on moving averages
            if indicators['current_price'] > indicators['sma_50'] > indicators['sma_200']:
                indicators['trend'] = "Bullish"
            elif indicators['current_price'] < indicators['sma_50'] < indicators['sma_200']:
                indicators['trend'] = "Bearish"
            else:
                indicators['trend'] = "Neutral"
            
            # Determine overbought/oversold based on RSI
            if indicators['rsi'] > 70:
                indicators['rsi_signal'] = "Overbought"
            elif indicators['rsi'] < 30:
                indicators['rsi_signal'] = "Oversold"
            else:
                indicators['rsi_signal'] = "Neutral"
            
            # Determine MACD signal
            if indicators['macd'] > indicators['macd_signal']:
                indicators['macd_signal_value'] = "Bullish"
            else:
                indicators['macd_signal_value'] = "Bearish"
            
            # Create summary
            summary = f"Technical Analysis: {indicators['trend']}. "
            summary += f"RSI: {indicators['rsi']:.2f} ({indicators['rsi_signal']}), "
            summary += f"MACD: {indicators['macd_signal_value']}, "
            summary += f"Price: {indicators['current_price']:.2f}"
            
            indicators['summary'] = summary
            
            return indicators
            
        except Exception as e:
            logger.error(f"Error in technical analysis: {str(e)}")
            return self._get_empty_indicators()
    
    def _get_empty_indicators(self):
        """Return empty indicators when analysis fails"""
        return {
            'sma_20': 0,
            'sma_50': 0,
            'sma_200': 0,
            'ema_20': 0,
            'rsi': 50,
            'macd': 0,
            'macd_signal': 0,
            'macd_hist': 0,
            'bb_upper': 0,
            'bb_middle': 0,
            'bb_lower': 0,
            'stoch_k': 50,
            'stoch_d': 50,
            'adx': 25,
            'obv': 0,
            'current_price': 0,
            'trend': "Unknown",
            'rsi_signal': "Unknown",
            'macd_signal_value': "Unknown",
            'summary': "Technical analysis not available"
        }