import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
import os
import logging

logger = logging.getLogger(__name__)

class MLModel:
    def __init__(self, model_path=None):
        """
        Initialize the ML model
        
        Args:
            model_path (str, optional): Path to saved model
        """
        self.model = None
        self.scaler = StandardScaler()
        self.features = []
        self.model_path = model_path or 'app/models/saved/ml_model.joblib'
        
        # Try to load pre-trained model if it exists
        if os.path.exists(self.model_path):
            self._load_model()
        else:
            # Initialize a new model
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
    
    def _load_model(self):
        """Load model from disk"""
        try:
            model_data = joblib.load(self.model_path)
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.features = model_data['features']
            logger.info(f"Loaded ML model from {self.model_path}")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            # Initialize a new model if loading fails
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
    
    def _save_model(self):
        """Save model to disk"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'features': self.features
            }
            joblib.dump(model_data, self.model_path)
            logger.info(f"Saved ML model to {self.model_path}")
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
    
    def _prepare_features(self, data, technical_indicators=None):
        """
        Prepare features for prediction
        
        Args:
            data (pandas.DataFrame): Historical price data
            technical_indicators (dict, optional): Technical indicators
            
        Returns:
            numpy.ndarray: Feature matrix
        """
        # Create a copy to avoid modifying the original data
        df = data.copy()
        
        # Add price-based features
        df['returns'] = df['close'].pct_change()
        df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
        
        # Add moving averages
        for window in [5, 10, 20, 50]:
            df[f'ma_{window}'] = df['close'].rolling(window=window).mean()
            df[f'ma_ratio_{window}'] = df['close'] / df[f'ma_{window}']
        
        # Add volatility
        for window in [5, 10, 20]:
            df[f'volatility_{window}'] = df['returns'].rolling(window=window).std()
        
        # Add price momentum
        for window in [1, 3, 5, 10]:
            df[f'momentum_{window}'] = df['close'].pct_change(periods=window)
        
        # Add volume features
        df['volume_change'] = df['volume'].pct_change()
        df['volume_ma_5'] = df['volume'].rolling(window=5).mean()
        df['volume_ma_10'] = df['volume'].rolling(window=10).mean()
        df['volume_ratio'] = df['volume'] / df['volume_ma_5']
        
        # Add price range features
        df['daily_range'] = df['high'] - df['low']
        df['daily_range_pct'] = df['daily_range'] / df['close']
        
        # Add gap features
        df['gap'] = df['open'] - df['close'].shift(1)
        df['gap_pct'] = df['gap'] / df['close'].shift(1)
        
        # Add technical indicators if provided
        if technical_indicators:
            for indicator, value in technical_indicators.items():
                if isinstance(value, (int, float)):
                    df[indicator] = value
        
        # Drop NaN values
        df.dropna(inplace=True)
        
        # Store feature names
        self.features = [col for col in df.columns if col not in ['open', 'high', 'low', 'close', 'volume']]
        
        # Return feature matrix
        X = df[self.features].values
        
        # Scale features
        X = self.scaler.fit_transform(X)
        
        return X
    
    def train(self, historical_data, labels, technical_indicators=None):
        """
        Train the ML model
        
        Args:
            historical_data (pandas.DataFrame): Historical price data
            labels (numpy.ndarray): Target labels (1 for buy, 0 for hold, -1 for sell)
            technical_indicators (dict, optional): Technical indicators
            
        Returns:
            dict: Training metrics
        """
        try:
            # Prepare features
            X = self._prepare_features(historical_data, technical_indicators)
            y = labels
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Define parameter grid for hyperparameter tuning
            param_grid = {
                'n_estimators': [50, 100, 200],
                'max_depth': [5, 10, 15, None],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4]
            }
            
            # Perform grid search
            grid_search = GridSearchCV(
                estimator=RandomForestClassifier(random_state=42),
                param_grid=param_grid,
                cv=5,
                scoring='f1_weighted',
                n_jobs=-1
            )
            
            grid_search.fit(X_train, y_train)
            
            # Get best model
            self.model = grid_search.best_estimator_
            
            # Evaluate on test set
            y_pred = self.model.predict(X_test)
            
            metrics = {
                'accuracy': accuracy_score(y_test, y_pred),
                'precision': precision_score(y_test, y_pred, average='weighted'),
                'recall': recall_score(y_test, y_pred, average='weighted'),
                'f1': f1_score(y_test, y_pred, average='weighted'),
                'best_params': grid_search.best_params_
            }
            
            logger.info(f"ML model trained with metrics: {metrics}")
            
            # Save the model
            self._save_model()
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error training ML model: {str(e)}")
            return {'error': str(e)}
    
    def predict(self, data, technical_indicators=None):
        """
        Make predictions using the ML model
        
        Args:
            data (pandas.DataFrame): Historical price data
            technical_indicators (dict, optional): Technical indicators
            
        Returns:
            dict: Prediction results
        """
        try:
            # Prepare features
            X = self._prepare_features(data, technical_indicators)
            
            # Get the most recent data point for prediction
            X_pred = X[-1].reshape(1, -1)
            
            # Make prediction
            prediction = self.model.predict(X_pred)[0]
            
            # Get prediction probabilities
            probabilities = self.model.predict_proba(X_pred)[0]
            
            # Map prediction to action
            if prediction == 1:
                action = "BUY"
                confidence = probabilities[list(self.model.classes_).index(1)]
            elif prediction == -1:
                action = "SELL"
                confidence = probabilities[list(self.model.classes_).index(-1)]
            else:
                action = "HOLD"
                confidence = probabilities[list(self.model.classes_).index(0)]
            
            # Get feature importances
            feature_importance = dict(zip(self.features, self.model.feature_importances_))
            top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:5]
            
            return {
                'action': action,
                'confidence': float(confidence),
                'prediction': int(prediction),
                'top_features': top_features
            }
            
        except Exception as e:
            logger.error(f"Error making ML prediction: {str(e)}")
            return {
                'action': "HOLD",
                'confidence': 0.0,
                'prediction': 0,
                'error': str(e)
            }
    
    def evaluate(self, test_data, test_labels, technical_indicators=None):
        """
        Evaluate the model on test data
        
        Args:
            test_data (pandas.DataFrame): Test data
            test_labels (numpy.ndarray): True labels
            technical_indicators (dict, optional): Technical indicators
            
        Returns:
            dict: Evaluation metrics
        """
        try:
            # Prepare features
            X_test = self._prepare_features(test_data, technical_indicators)
            y_test = test_labels
            
            # Make predictions
            y_pred = self.model.predict(X_test)
            
            # Calculate metrics
            metrics = {
                'accuracy': accuracy_score(y_test, y_pred),
                'precision': precision_score(y_test, y_pred, average='weighted'),
                'recall': recall_score(y_test, y_pred, average='weighted'),
                'f1': f1_score(y_test, y_pred, average='weighted')
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error evaluating ML model: {str(e)}")
            return {'error': str(e)}