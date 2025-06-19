import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
import ta

logger = logging.getLogger(__name__)

class DataProcessor:
    def __init__(self):
        """Initialize the data processor"""
        pass
    
    def process(self, data):
        """
        Process raw historical data
        
        Args:
            data (pandas.DataFrame): Raw historical data
            
        Returns:
            pandas.DataFrame: Processed data with additional features
        """
        try:
            # Create a copy to avoid modifying the original data
            df = data.copy()
            
            # Check if data is empty
            if df.empty:
                logger.warning("Empty data provided to data processor")
                return df
            
            # Make sure the index is datetime
            if not isinstance(df.index, pd.DatetimeIndex):
                logger.warning("Data index is not DatetimeIndex. Attempting to convert.")
                if 'timestamp' in df.columns:
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    df.set_index('timestamp', inplace=True)
                else:
                    logger.error("Cannot convert index to DatetimeIndex. No timestamp column found.")
            
            # Fill missing values
            df.fillna(method='ffill', inplace=True)
            
            # Add basic features
            self._add_basic_features(df)
            
            # Add technical indicators
            self._add_technical_indicators(df)
            
            # Add volatility features
            self._add_volatility_features(df)
            
            # Add momentum features
            self._add_momentum_features(df)
            
            # Add volume features
            self._add_volume_features(df)
            
            # Add date features
            self._add_date_features(df)
            
            # Drop NaN values
            df.dropna(inplace=True)
            
            return df
            
        except Exception as e:
            logger.error(f"Error processing data: {str(e)}")
            return data
    
    def _add_basic_features(self, df):
        """Add basic price features"""
        # Returns
        df['returns'] = df['close'].pct_change()
        df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
        
        # Price range
        df['daily_range'] = df['high'] - df['low']
        df['daily_range_pct'] = df['daily_range'] / df['close']
        
        # Gap
        df['gap'] = df['open'] - df['close'].shift(1)
        df['gap_pct'] = df['gap'] / df['close'].shift(1)
        
        # Price position
        df['price_position'] = (df['close'] - df['low']) / (df['high'] - df['low'])
    
    def _add_technical_indicators(self, df):
        """Add technical indicators"""
        # Moving Averages
        for window in [5, 10, 20, 50, 100, 200]:
            df[f'ma_{window}'] = df['close'].rolling(window=window).mean()
            df[f'ma_ratio_{window}'] = df['close'] / df[f'ma_{window}']
        
        # Exponential Moving Averages
        for window in [5, 10, 20, 50, 100, 200]:
            df[f'ema_{window}'] = df['close'].ewm(span=window, adjust=False).mean()
            df[f'ema_ratio_{window}'] = df['close'] / df[f'ema_{window}']
        
        # MACD
        df['macd_line'] = df['close'].ewm(span=12, adjust=False).mean() - df['close'].ewm(span=26, adjust=False).mean()
        df['macd_signal'] = df['macd_line'].ewm(span=9, adjust=False).mean()
        df['macd_histogram'] = df['macd_line'] - df['macd_signal']
        
        # RSI
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        
        rs = avg_gain / avg_loss
        df['rsi_14'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        for window in [20]:
            df[f'bb_middle_{window}'] = df['close'].rolling(window=window).mean()
            df[f'bb_std_{window}'] = df['close'].rolling(window=window).std()
            df[f'bb_upper_{window}'] = df[f'bb_middle_{window}'] + 2 * df[f'bb_std_{window}']
            df[f'bb_lower_{window}'] = df[f'bb_middle_{window}'] - 2 * df[f'bb_std_{window}']
            df[f'bb_width_{window}'] = (df[f'bb_upper_{window}'] - df[f'bb_lower_{window}']) / df[f'bb_middle_{window}']
            df[f'bb_position_{window}'] = (df['close'] - df[f'bb_lower_{window}']) / (df[f'bb_upper_{window}'] - df[f'bb_lower_{window}'])
        
        # Add more indicators using TA library
        try:
            # Trend indicators
            df['adx'] = ta.trend.adx(df['high'], df['low'], df['close'], window=14)
            df['cci'] = ta.trend.cci(df['high'], df['low'], df['close'], window=20)
            df['dpo'] = ta.trend.dpo(df['close'], window=20)
            df['ichimoku_a'] = ta.trend.ichimoku_a(df['high'], df['low'], window1=9, window2=26)
            df['ichimoku_b'] = ta.trend.ichimoku_b(df['high'], df['low'], window2=26, window3=52)
            
            # Momentum indicators
            df['awesome_oscillator'] = ta.momentum.awesome_oscillator(df['high'], df['low'])
            df['kama'] = ta.momentum.kama(df['close'], window=10)
            df['ppo'] = ta.momentum.ppo(df['close'])
            df['pvo'] = ta.momentum.pvo(df['volume'])
            df['stoch'] = ta.momentum.stoch(df['high'], df['low'], df['close'])
            df['stoch_signal'] = ta.momentum.stoch_signal(df['high'], df['low'], df['close'])
            df['tsi'] = ta.momentum.tsi(df['close'])
            df['ultimate_oscillator'] = ta.momentum.ultimate_oscillator(df['high'], df['low'], df['close'])
            df['williams_r'] = ta.momentum.williams_r(df['high'], df['low'], df['close'])
            
            # Volume indicators
            df['acc_dist_index'] = ta.volume.acc_dist_index(df['high'], df['low'], df['close'], df['volume'])
            df['chaikin_money_flow'] = ta.volume.chaikin_money_flow(df['high'], df['low'], df['close'], df['volume'])
            df['ease_of_movement'] = ta.volume.ease_of_movement(df['high'], df['low'], df['volume'])
            df['force_index'] = ta.volume.force_index(df['close'], df['volume'])
            df['money_flow_index'] = ta.volume.money_flow_index(df['high'], df['low'], df['close'], df['volume'])
            df['volume_weighted_average_price'] = ta.volume.volume_weighted_average_price(df['high'], df['low'], df['close'], df['volume'])
            
            # Volatility indicators
            df['average_true_range'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'])
            df['keltner_channel_hband'] = ta.volatility.keltner_channel_hband(df['high'], df['low'], df['close'])
            df['keltner_channel_lband'] = ta.volatility.keltner_channel_lband(df['high'], df['low'], df['close'])
            df['keltner_channel_width'] = ta.volatility.keltner_channel_wband(df['high'], df['low'], df['close'])
            
        except Exception as e:
            logger.warning(f"Error adding TA indicators: {str(e)}")
    
    def _add_volatility_features(self, df):
        """Add volatility features"""
        # Historical volatility
        for window in [5, 10, 20, 30]:
            df[f'volatility_{window}'] = df['returns'].rolling(window=window).std() * np.sqrt(252)  # Annualized
        
        # True Range
        df['true_range'] = np.maximum(
            df['high'] - df['low'],
            np.maximum(
                np.abs(df['high'] - df['close'].shift(1)),
                np.abs(df['low'] - df['close'].shift(1))
            )
        )
        
        # Average True Range
        df['atr_14'] = df['true_range'].rolling(window=14).mean()
        df['atr_ratio_14'] = df['atr_14'] / df['close']
    
    def _add_momentum_features(self, df):
        """Add momentum features"""
        # Price momentum
        for window in [1, 3, 5, 10, 20]:
            df[f'momentum_{window}'] = df['close'].pct_change(periods=window)
        
        # Rate of Change
        for window in [5, 10, 20]:
            df[f'roc_{window}'] = (df['close'] - df['close'].shift(window)) / df['close'].shift(window) * 100
    
    def _add_volume_features(self, df):
        """Add volume features"""
        # Volume changes
        df['volume_change'] = df['volume'].pct_change()
        
        # Volume moving averages
        for window in [5, 10, 20, 50]:
            df[f'volume_ma_{window}'] = df['volume'].rolling(window=window).mean()
            df[f'volume_ratio_{window}'] = df['volume'] / df[f'volume_ma_{window}']
        
        # On-Balance Volume (OBV)
        df['obv'] = 0
        df.loc[df['close'] > df['close'].shift(1), 'obv'] = df['volume']
        df.loc[df['close'] < df['close'].shift(1), 'obv'] = -df['volume']
        df['obv'] = df['obv'].cumsum()
    
    def _add_date_features(self, df):
        """Add date-based features"""
        if isinstance(df.index, pd.DatetimeIndex):
            # Day of week
            df['day_of_week'] = df.index.dayofweek
            
            # Month
            df['month'] = df.index.month
            
            # Is month end
            df['is_month_end'] = df.index.is_month_end.astype(int)
            
            # Is quarter end
            df['is_quarter_end'] = df.index.is_quarter_end.astype(int)
            
            # Day of month
            df['day_of_month'] = df.index.day
            
            # Week of year
            df['week_of_year'] = df.index.isocalendar().week
    
    def normalize_features(self, df):
        """
        Normalize features to [0, 1] range
        
        Args:
            df (pandas.DataFrame): DataFrame with features
            
        Returns:
            pandas.DataFrame: Normalized DataFrame
        """
        try:
            # Create a copy
            normalized_df = df.copy()
            
            # Get numerical columns
            numerical_cols = df.select_dtypes(include=['float64', 'int64']).columns
            
            # Skip certain columns
            skip_cols = ['day_of_week', 'month', 'is_month_end', 'is_quarter_end', 'day_of_month', 'week_of_year']
            cols_to_normalize = [col for col in numerical_cols if col not in skip_cols]
            
            # Normalize each column
            for col in cols_to_normalize:
                min_val = normalized_df[col].min()
                max_val = normalized_df[col].max()
                
                if max_val > min_val:
                    normalized_df[col] = (normalized_df[col] - min_val) / (max_val - min_val)
            
            return normalized_df
            
        except Exception as e:
            logger.error(f"Error normalizing features: {str(e)}")
            return df