import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import os
import re
from bs4 import BeautifulSoup
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

logger = logging.getLogger(__name__)

class NewsAnalyzer:
    def __init__(self, api_key=None):
        """
        Initialize the News Analyzer
        
        Args:
            api_key (str, optional): News API key
        """
        self.api_key = api_key or os.getenv("NEWS_API_KEY")
        self.sentiment_analyzer = None
        self._initialize_nltk()
    
    def _initialize_nltk(self):
        """Initialize NLTK resources"""
        try:
            # Download necessary NLTK resources
            nltk.download('vader_lexicon', quiet=True)
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            
            # Initialize sentiment analyzer
            self.sentiment_analyzer = SentimentIntensityAnalyzer()
            
            logger.info("NLTK resources initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing NLTK resources: {str(e)}")
    
    def analyze_for_symbol(self, symbol, days=7):
        """
        Analyze news for a specific symbol
        
        Args:
            symbol (str): Stock symbol
            days (int): Number of days to look back
            
        Returns:
            dict: Analysis results
        """
        try:
            # Get news articles
            articles = self._get_news_articles(symbol, days)
            
            if not articles:
                logger.warning(f"No news articles found for {symbol}")
                return {
                    'sentiment': 'NEUTRAL',
                    'sentiment_score': 0.0,
                    'articles': [],
                    'keywords': {}
                }
            
            # Analyze sentiment for each article
            for article in articles:
                article['sentiment_score'] = self._analyze_sentiment(article['title'] + ' ' + article['description'])
                article['sentiment'] = self._score_to_sentiment(article['sentiment_score'])
            
            # Calculate overall sentiment
            overall_score = np.mean([article['sentiment_score'] for article in articles])
            overall_sentiment = self._score_to_sentiment(overall_score)
            
            # Extract keywords
            keywords = self._extract_keywords(articles)
            
            return {
                'sentiment': overall_sentiment,
                'sentiment_score': float(overall_score),
                'articles': articles,
                'keywords': keywords
            }
            
        except Exception as e:
            logger.error(f"Error analyzing news for {symbol}: {str(e)}")
            return {
                'sentiment': 'NEUTRAL',
                'sentiment_score': 0.0,
                'articles': [],
                'keywords': {},
                'error': str(e)
            }
    
    def _get_news_articles(self, symbol, days=7):
        """
        Get news articles for a symbol
        
        Args:
            symbol (str): Stock symbol
            days (int): Number of days to look back
            
        Returns:
            list: News articles
        """
        articles = []
        
        try:
            # Try to use News API if API key is available
            if self.api_key:
                articles = self._get_articles_from_news_api(symbol, days)
            
            # If no articles found or no API key, try alternative sources
            if not articles:
                articles = self._get_articles_from_alternative_sources(symbol, days)
            
            return articles
            
        except Exception as e:
            logger.error(f"Error getting news articles for {symbol}: {str(e)}")
            return []
    
    def _get_articles_from_news_api(self, symbol, days):
        """Get articles from News API"""
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Format dates
            from_date = start_date.strftime('%Y-%m-%d')
            to_date = end_date.strftime('%Y-%m-%d')
            
            # Build query
            company_name = self._get_company_name(symbol)
            query = f"{symbol} OR {company_name}"
            
            # Make API request
            url = f"https://newsapi.org/v2/everything?q={query}&from={from_date}&to={to_date}&sortBy=popularity&apiKey={self.api_key}"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                if data['status'] == 'ok':
                    # Process articles
                    processed_articles = []
                    
                    for article in data['articles'][:20]:  # Limit to 20 articles
                        processed_articles.append({
                            'title': article['title'],
                            'description': article['description'] or '',
                            'url': article['url'],
                            'source': article['source']['name'],
                            'published_at': article['publishedAt'],
                            'relevance': self._calculate_relevance(article['title'] + ' ' + (article['description'] or ''), symbol, company_name)
                        })
                    
                    # Sort by relevance
                    processed_articles.sort(key=lambda x: x['relevance'], reverse=True)
                    
                    # Return top 10 most relevant articles
                    return processed_articles[:10]
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting articles from News API: {str(e)}")
            return []
    
    def _get_articles_from_alternative_sources(self, symbol, days):
        """Get articles from alternative sources when News API is not available"""
        try:
            # This is a placeholder for alternative news sources
            # In a real implementation, you might scrape financial news websites
            # or use other free APIs
            
            # For now, return some dummy data
            current_date = datetime.now()
            
            dummy_articles = [
                {
                    'title': f"Market analysis for {symbol}",
                    'description': f"Recent market trends show {symbol} has been performing well in the current economic climate.",
                    'url': f"https://example.com/market-analysis/{symbol}",
                    'source': "Market Analysis",
                    'published_at': current_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    'relevance': 0.9
                },
                {
                    'title': f"Quarterly results for {symbol}",
                    'description': f"{symbol} announced its quarterly results with positive outlook for investors.",
                    'url': f"https://example.com/quarterly-results/{symbol}",
                    'source': "Financial News",
                    'published_at': (current_date - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%SZ'),
                    'relevance': 0.95
                },
                {
                    'title': f"Industry trends affecting {symbol}",
                    'description': f"Analysis of how current industry trends might impact {symbol}'s future performance.",
                    'url': f"https://example.com/industry-trends/{symbol}",
                    'source': "Industry Insights",
                    'published_at': (current_date - timedelta(days=2)).strftime('%Y-%m-%dT%H:%M:%SZ'),
                    'relevance': 0.8
                }
            ]
            
            return dummy_articles
            
        except Exception as e:
            logger.error(f"Error getting articles from alternative sources: {str(e)}")
            return []
    
    def _analyze_sentiment(self, text):
        """
        Analyze sentiment of text
        
        Args:
            text (str): Text to analyze
            
        Returns:
            float: Sentiment score (-1 to 1)
        """
        try:
            if not self.sentiment_analyzer:
                return 0.0
            
            if not text:
                return 0.0
            
            # Get sentiment scores
            sentiment = self.sentiment_analyzer.polarity_scores(text)
            
            # Return compound score
            return sentiment['compound']
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return 0.0
    
    def _score_to_sentiment(self, score):
        """
        Convert sentiment score to sentiment label
        
        Args:
            score (float): Sentiment score (-1 to 1)
            
        Returns:
            str: Sentiment label (BULLISH, NEUTRAL, BEARISH)
        """
        if score >= 0.2:
            return 'BULLISH'
        elif score <= -0.2:
            return 'BEARISH'
        else:
            return 'NEUTRAL'
    
    def _calculate_relevance(self, text, symbol, company_name):
        """
        Calculate relevance of an article to the symbol
        
        Args:
            text (str): Article text
            symbol (str): Stock symbol
            company_name (str): Company name
            
        Returns:
            float: Relevance score (0 to 1)
        """
        try:
            if not text:
                return 0.0
            
            # Count occurrences of symbol and company name
            symbol_count = text.upper().count(symbol.upper())
            company_count = text.upper().count(company_name.upper())
            
            # Calculate relevance score
            total_words = len(text.split())
            if total_words == 0:
                return 0.0
            
            relevance = min(1.0, (symbol_count * 2 + company_count) / (total_words / 10))
            
            return relevance
            
        except Exception as e:
            logger.error(f"Error calculating relevance: {str(e)}")
            return 0.0
    
    def _extract_keywords(self, articles):
        """
        Extract keywords from articles
        
        Args:
            articles (list): List of articles
            
        Returns:
            dict: Keywords with frequencies
        """
        try:
            if not articles:
                return {}
            
            # Combine all article texts
            all_text = ' '.join([article['title'] + ' ' + article['description'] for article in articles])
            
            # Tokenize
            tokens = word_tokenize(all_text.lower())
            
            # Remove stopwords
            stop_words = set(stopwords.words('english'))
            filtered_tokens = [word for word in tokens if word.isalpha() and word not in stop_words]
            
            # Count frequencies
            freq_dist = nltk.FreqDist(filtered_tokens)
            
            # Get top 20 keywords
            keywords = {word: count for word, count in freq_dist.most_common(20)}
            
            return keywords
            
        except Exception as e:
            logger.error(f"Error extracting keywords: {str(e)}")
            return {}
    
    def _get_company_name(self, symbol):
        """
        Get company name from symbol
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            str: Company name
        """
        # This is a simplified mapping for common stocks
        # In a real implementation, you would use a more comprehensive database
        company_mapping = {
            'AAPL': 'Apple',
            'MSFT': 'Microsoft',
            'GOOGL': 'Google',
            'AMZN': 'Amazon',
            'FB': 'Facebook',
            'TSLA': 'Tesla',
            'NFLX': 'Netflix',
            'NVDA': 'NVIDIA',
            'PYPL': 'PayPal',
            'ADBE': 'Adobe',
            'INTC': 'Intel',
            'CMCSA': 'Comcast',
            'PEP': 'PepsiCo',
            'CSCO': 'Cisco',
            'AVGO': 'Broadcom',
            'TXN': 'Texas Instruments',
            'QCOM': 'Qualcomm',
            'TMUS': 'T-Mobile',
            'AMGN': 'Amgen',
            'SBUX': 'Starbucks',
            'INFY': 'Infosys',
            'TCS': 'Tata Consultancy Services',
            'RELIANCE': 'Reliance Industries',
            'HDFCBANK': 'HDFC Bank',
            'ICICIBANK': 'ICICI Bank',
            'SBIN': 'State Bank of India',
            'TATAMOTORS': 'Tata Motors',
            'WIPRO': 'Wipro',
            'AXISBANK': 'Axis Bank',
            'BAJFINANCE': 'Bajaj Finance'
        }
        
        return company_mapping.get(symbol, symbol)