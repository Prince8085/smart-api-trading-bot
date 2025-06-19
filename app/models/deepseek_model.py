import os
import json
import logging
import pandas as pd
import numpy as np
from groq import Groq
from datetime import datetime

logger = logging.getLogger(__name__)

class DeepSeekModel:
    def __init__(self, api_key=None):
        """
        Initialize the DeepSeek model integration
        
        Args:
            api_key (str, optional): Groq API key
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model_name = "deepseek-coder-33b-instruct"  # Using DeepSeek model through Groq
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Groq client"""
        try:
            if not self.api_key:
                logger.warning("Groq API key not provided. DeepSeek model will not be available.")
                return
            
            self.client = Groq(api_key=self.api_key)
            logger.info("Groq client initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Groq client: {str(e)}")
    
    def _prepare_market_context(self, symbol, data, market_context):
        """
        Prepare market context for the DeepSeek model
        
        Args:
            symbol (str): Stock symbol
            data (pandas.DataFrame): Historical price data
            market_context (dict): Additional market context
            
        Returns:
            str: Formatted market context
        """
        # Format historical data
        recent_data = data.tail(5).reset_index()
        historical_data_str = "Recent price data:\n"
        for _, row in recent_data.iterrows():
            date_str = row['timestamp'].strftime('%Y-%m-%d')
            historical_data_str += f"{date_str}: Open: {row['open']:.2f}, High: {row['high']:.2f}, Low: {row['low']:.2f}, Close: {row['close']:.2f}, Volume: {row['volume']}\n"
        
        # Format technical indicators
        technical_indicators_str = "Technical indicators:\n"
        if 'technical_indicators' in market_context:
            for indicator, value in market_context['technical_indicators'].items():
                if isinstance(value, (int, float)):
                    technical_indicators_str += f"{indicator}: {value:.4f}\n"
                else:
                    technical_indicators_str += f"{indicator}: {value}\n"
        
        # Format option chain summary
        option_chain_str = "Option chain summary:\n"
        if 'option_chain' in market_context and 'summary' in market_context['option_chain']:
            option_summary = market_context['option_chain']['summary']
            for key, value in option_summary.items():
                option_chain_str += f"{key}: {value}\n"
        
        # Format news sentiment
        news_str = "Recent news sentiment:\n"
        if 'news' in market_context and 'articles' in market_context['news']:
            for article in market_context['news']['articles'][:3]:  # Limit to 3 articles
                news_str += f"- {article['title']}: {article['sentiment']}\n"
        
        # Combine all context
        full_context = f"""
        I need to analyze the stock {symbol} based on the following market data:
        
        {historical_data_str}
        
        {technical_indicators_str}
        
        {option_chain_str}
        
        {news_str}
        
        Current date: {datetime.now().strftime('%Y-%m-%d')}
        
        Based on this information, analyze the stock and provide:
        1. A trading recommendation (BUY, SELL, or HOLD)
        2. A confidence score between 0 and 1
        3. Key factors influencing your decision
        4. Short-term price target
        5. Potential risks
        
        Format your response as a JSON object with the following structure:
        {
            "recommendation": "BUY/SELL/HOLD",
            "confidence": 0.XX,
            "factors": ["factor1", "factor2", ...],
            "price_target": "value",
            "risks": ["risk1", "risk2", ...],
            "analysis": "brief analysis"
        }
        """
        
        return full_context
    
    def analyze(self, symbol, data, market_context=None):
        """
        Analyze a stock using the DeepSeek model
        
        Args:
            symbol (str): Stock symbol
            data (pandas.DataFrame): Historical price data
            market_context (dict, optional): Additional market context
            
        Returns:
            dict: Analysis results
        """
        try:
            if not self.client:
                logger.warning("Groq client not initialized. Returning default analysis.")
                return {
                    'action': "HOLD",
                    'confidence': 0.5,
                    'factors': ["DeepSeek model not available"],
                    'price_target': None,
                    'risks': ["Analysis not performed"],
                    'analysis': "DeepSeek model not available due to missing API key"
                }
            
            # Prepare market context
            prompt = self._prepare_market_context(symbol, data, market_context or {})
            
            # Call the DeepSeek model through Groq
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a professional stock market analyst with expertise in technical analysis, fundamental analysis, and market sentiment. Provide accurate and insightful stock analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1000
            )
            
            # Extract the response
            analysis_text = response.choices[0].message.content
            
            # Parse JSON from the response
            try:
                # Find JSON in the response
                json_start = analysis_text.find('{')
                json_end = analysis_text.rfind('}') + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_str = analysis_text[json_start:json_end]
                    analysis_result = json.loads(json_str)
                else:
                    # If JSON not found, create a structured response
                    logger.warning("JSON not found in DeepSeek response. Creating structured response.")
                    analysis_result = self._extract_structured_response(analysis_text)
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON from DeepSeek response. Creating structured response.")
                analysis_result = self._extract_structured_response(analysis_text)
            
            # Map recommendation to action
            recommendation = analysis_result.get('recommendation', 'HOLD').upper()
            if recommendation == 'BUY':
                action = "BUY"
                prediction = 1
            elif recommendation == 'SELL':
                action = "SELL"
                prediction = -1
            else:
                action = "HOLD"
                prediction = 0
            
            # Get confidence score
            confidence = float(analysis_result.get('confidence', 0.5))
            
            return {
                'action': action,
                'confidence': confidence,
                'prediction': prediction,
                'factors': analysis_result.get('factors', []),
                'price_target': analysis_result.get('price_target'),
                'risks': analysis_result.get('risks', []),
                'analysis': analysis_result.get('analysis', '')
            }
            
        except Exception as e:
            logger.error(f"Error analyzing with DeepSeek model: {str(e)}")
            return {
                'action': "HOLD",
                'confidence': 0.5,
                'prediction': 0,
                'factors': ["Error in analysis"],
                'price_target': None,
                'risks': ["Analysis failed"],
                'analysis': f"Error: {str(e)}"
            }
    
    def _extract_structured_response(self, text):
        """
        Extract structured information from unstructured text response
        
        Args:
            text (str): Unstructured text response
            
        Returns:
            dict: Structured response
        """
        # Default structure
        result = {
            'recommendation': 'HOLD',
            'confidence': 0.5,
            'factors': [],
            'price_target': None,
            'risks': [],
            'analysis': text[:200] + "..." if len(text) > 200 else text
        }
        
        # Try to extract recommendation
        if "BUY" in text.upper():
            result['recommendation'] = 'BUY'
        elif "SELL" in text.upper():
            result['recommendation'] = 'SELL'
        
        # Try to extract confidence
        import re
        confidence_pattern = r'confidence[:\s]+([0-9.]+)'
        confidence_match = re.search(confidence_pattern, text, re.IGNORECASE)
        if confidence_match:
            try:
                confidence = float(confidence_match.group(1))
                if 0 <= confidence <= 1:
                    result['confidence'] = confidence
            except ValueError:
                pass
        
        # Try to extract factors
        factors = []
        if "factor" in text.lower() or "reason" in text.lower():
            # Split by lines and look for numbered or bulleted lists
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if re.match(r'^[0-9*\-•]+\.?\s+', line) and len(line) > 5:
                    # Remove the numbering/bullet
                    factor = re.sub(r'^[0-9*\-•]+\.?\s+', '', line)
                    factors.append(factor)
        
        if factors:
            result['factors'] = factors
        
        # Try to extract price target
        price_pattern = r'price target[:\s]+([\$0-9.]+)'
        price_match = re.search(price_pattern, text, re.IGNORECASE)
        if price_match:
            result['price_target'] = price_match.group(1)
        
        # Try to extract risks
        risks = []
        if "risk" in text.lower():
            lines = text.split('\n')
            in_risks_section = False
            for line in lines:
                line = line.strip()
                if "risk" in line.lower() and ":" in line:
                    in_risks_section = True
                    continue
                
                if in_risks_section and re.match(r'^[0-9*\-•]+\.?\s+', line) and len(line) > 5:
                    risk = re.sub(r'^[0-9*\-•]+\.?\s+', '', line)
                    risks.append(risk)
        
        if risks:
            result['risks'] = risks
        
        return result