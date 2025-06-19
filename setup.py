from setuptools import setup, find_packages

setup(
    name="trading_bot",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "flask>=2.0.1",
        "pandas>=1.3.3",
        "numpy>=1.21.2",
        "scikit-learn>=1.0",
        "requests>=2.26.0",
        "beautifulsoup4>=4.10.0",
        "nltk>=3.6.5",
        "python-dotenv>=0.19.1",
        "schedule>=1.1.0",
        "plotly>=5.5.0",
        "ta>=0.7.0",
        "yfinance>=0.1.70",
    ],
    extras_require={
        "full": [
            "tensorflow>=2.8.0",
            "keras>=2.8.0",
            "matplotlib>=3.4.3",
            "seaborn>=0.11.2",
            "transformers>=4.12.0",
            "torch>=1.10.0",
            "groq>=0.4.0",
            "newsapi-python>=0.2.6",
        ]
    },
)