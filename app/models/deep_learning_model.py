import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import MinMaxScaler
import os
import logging

logger = logging.getLogger(__name__)

class DeepLearningModel:
    def __init__(self, model_path=None):
        """
        Initialize the Deep Learning model
        
        Args:
            model_path (str, optional): Path to saved model
        """
        self.model = None
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.sequence_length = 60  # Number of time steps to look back
        self.model_path = model_path or 'app/models/saved/dl_model.h5'
        self.scaler_path = model_path or 'app/models/saved/dl_scaler.npy'
        
        # Try to load pre-trained model if it exists
        if os.path.exists(self.model_path):
            self._load_model()
        else:
            # Initialize a new model
            self._build_model()
    
    def _build_model(self):
        """Build the LSTM model architecture"""
        try:
            # Define model architecture
            self.model = Sequential([
                LSTM(units=50, return_sequences=True, input_shape=(self.sequence_length, 1)),
                Dropout(0.2),
                BatchNormalization(),
                
                LSTM(units=100, return_sequences=True),
                Dropout(0.2),
                BatchNormalization(),
                
                LSTM(units=50, return_sequences=False),
                Dropout(0.2),
                BatchNormalization(),
                
                Dense(units=25, activation='relu'),
                Dense(units=3, activation='softmax')  # 3 classes: buy, hold, sell
            ])
            
            # Compile model
            self.model.compile(
                optimizer=Adam(learning_rate=0.001),
                loss='sparse_categorical_crossentropy',
                metrics=['accuracy']
            )
            
            logger.info("Deep Learning model built successfully")
            
        except Exception as e:
            logger.error(f"Error building Deep Learning model: {str(e)}")
    
    def _load_model(self):
        """Load model from disk"""
        try:
            self.model = load_model(self.model_path)
            
            # Load scaler if available
            if os.path.exists(self.scaler_path):
                scaler_params = np.load(self.scaler_path, allow_pickle=True).item()
                self.scaler.min_ = scaler_params['min_']
                self.scaler.scale_ = scaler_params['scale_']
                self.scaler.data_min_ = scaler_params['data_min_']
                self.scaler.data_max_ = scaler_params['data_max_']
                self.scaler.data_range_ = scaler_params['data_range_']
            
            logger.info(f"Loaded Deep Learning model from {self.model_path}")
        except Exception as e:
            logger.error(f"Error loading Deep Learning model: {str(e)}")
            # Build a new model if loading fails
            self._build_model()
    
    def _save_model(self):
        """Save model to disk"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            
            # Save model
            self.model.save(self.model_path)
            
            # Save scaler
            scaler_params = {
                'min_': self.scaler.min_,
                'scale_': self.scaler.scale_,
                'data_min_': self.scaler.data_min_,
                'data_max_': self.scaler.data_max_,
                'data_range_': self.scaler.data_range_
            }
            np.save(self.scaler_path, scaler_params)
            
            logger.info(f"Saved Deep Learning model to {self.model_path}")
        except Exception as e:
            logger.error(f"Error saving Deep Learning model: {str(e)}")
    
    def _prepare_sequences(self, data):
        """
        Prepare sequences for LSTM model
        
        Args:
            data (pandas.DataFrame): Historical price data
            
        Returns:
            tuple: (X, y) where X is the sequence data and y is the target
        """
        # Extract close prices
        close_prices = data['close'].values.reshape(-1, 1)
        
        # Scale the data
        scaled_data = self.scaler.fit_transform(close_prices)
        
        X = []
        y = []
        
        for i in range(self.sequence_length, len(scaled_data)-1):
            # Create sequence
            X.append(scaled_data[i-self.sequence_length:i, 0])
            
            # Create target
            # Compare current price with next day's price
            current_price = scaled_data[i, 0]
            next_price = scaled_data[i+1, 0]
            
            # Calculate percentage change
            pct_change = (next_price - current_price) / current_price
            
            # Classify as buy (1), hold (0), or sell (-1)
            if pct_change > 0.01:  # More than 1% increase
                target = 1  # Buy
            elif pct_change < -0.01:  # More than 1% decrease
                target = 2  # Sell (using 2 instead of -1 for sparse_categorical_crossentropy)
            else:
                target = 0  # Hold
            
            y.append(target)
        
        # Convert to numpy arrays
        X = np.array(X)
        y = np.array(y)
        
        # Reshape X for LSTM [samples, time steps, features]
        X = np.reshape(X, (X.shape[0], X.shape[1], 1))
        
        return X, y
    
    def _prepare_prediction_data(self, data):
        """
        Prepare data for prediction
        
        Args:
            data (pandas.DataFrame): Historical price data
            
        Returns:
            numpy.ndarray: Prepared sequence for prediction
        """
        # Extract close prices
        close_prices = data['close'].values.reshape(-1, 1)
        
        # Scale the data
        scaled_data = self.scaler.transform(close_prices)
        
        # Create sequence for prediction (most recent sequence_length points)
        X = []
        X.append(scaled_data[-self.sequence_length:, 0])
        
        # Convert to numpy array and reshape for LSTM
        X = np.array(X)
        X = np.reshape(X, (X.shape[0], X.shape[1], 1))
        
        return X
    
    def train(self, historical_data, epochs=50, batch_size=32):
        """
        Train the Deep Learning model
        
        Args:
            historical_data (pandas.DataFrame): Historical price data
            epochs (int): Number of training epochs
            batch_size (int): Batch size for training
            
        Returns:
            dict: Training history
        """
        try:
            # Prepare sequences
            X, y = self._prepare_sequences(historical_data)
            
            # Split data into train and validation sets
            split = int(0.8 * len(X))
            X_train, X_val = X[:split], X[split:]
            y_train, y_val = y[:split], y[split:]
            
            # Define callbacks
            callbacks = [
                EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True),
                ModelCheckpoint(
                    filepath=self.model_path,
                    monitor='val_loss',
                    save_best_only=True,
                    verbose=1
                )
            ]
            
            # Train model
            history = self.model.fit(
                X_train, y_train,
                epochs=epochs,
                batch_size=batch_size,
                validation_data=(X_val, y_val),
                callbacks=callbacks,
                verbose=1
            )
            
            # Save model
            self._save_model()
            
            # Return training history
            return {
                'accuracy': history.history['accuracy'][-1],
                'val_accuracy': history.history['val_accuracy'][-1],
                'loss': history.history['loss'][-1],
                'val_loss': history.history['val_loss'][-1]
            }
            
        except Exception as e:
            logger.error(f"Error training Deep Learning model: {str(e)}")
            return {'error': str(e)}
    
    def predict(self, data, technical_indicators=None):
        """
        Make predictions using the Deep Learning model
        
        Args:
            data (pandas.DataFrame): Historical price data
            technical_indicators (dict, optional): Technical indicators (not used in this model)
            
        Returns:
            dict: Prediction results
        """
        try:
            # Check if we have enough data
            if len(data) < self.sequence_length:
                return {
                    'action': "HOLD",
                    'confidence': 0.0,
                    'prediction': 0,
                    'error': "Not enough data for prediction"
                }
            
            # Prepare data for prediction
            X = self._prepare_prediction_data(data)
            
            # Make prediction
            prediction_probs = self.model.predict(X)[0]
            
            # Get class with highest probability
            prediction_class = np.argmax(prediction_probs)
            confidence = prediction_probs[prediction_class]
            
            # Map class to action
            if prediction_class == 1:  # Buy
                action = "BUY"
                prediction_value = 1
            elif prediction_class == 2:  # Sell
                action = "SELL"
                prediction_value = -1
            else:  # Hold
                action = "HOLD"
                prediction_value = 0
            
            return {
                'action': action,
                'confidence': float(confidence),
                'prediction': prediction_value,
                'class_probabilities': {
                    'hold': float(prediction_probs[0]),
                    'buy': float(prediction_probs[1]),
                    'sell': float(prediction_probs[2])
                }
            }
            
        except Exception as e:
            logger.error(f"Error making Deep Learning prediction: {str(e)}")
            return {
                'action': "HOLD",
                'confidence': 0.0,
                'prediction': 0,
                'error': str(e)
            }
    
    def evaluate(self, test_data):
        """
        Evaluate the model on test data
        
        Args:
            test_data (pandas.DataFrame): Test data
            
        Returns:
            dict: Evaluation metrics
        """
        try:
            # Prepare sequences
            X, y = self._prepare_sequences(test_data)
            
            # Evaluate model
            loss, accuracy = self.model.evaluate(X, y, verbose=0)
            
            # Make predictions for detailed metrics
            y_pred_probs = self.model.predict(X)
            y_pred = np.argmax(y_pred_probs, axis=1)
            
            # Calculate confusion matrix
            from sklearn.metrics import confusion_matrix
            cm = confusion_matrix(y, y_pred)
            
            # Calculate precision, recall, and f1 for each class
            from sklearn.metrics import precision_recall_fscore_support
            precision, recall, f1, _ = precision_recall_fscore_support(y, y_pred, average=None)
            
            return {
                'accuracy': accuracy,
                'loss': loss,
                'confusion_matrix': cm.tolist(),
                'precision': precision.tolist(),
                'recall': recall.tolist(),
                'f1': f1.tolist()
            }
            
        except Exception as e:
            logger.error(f"Error evaluating Deep Learning model: {str(e)}")
            return {'error': str(e)}