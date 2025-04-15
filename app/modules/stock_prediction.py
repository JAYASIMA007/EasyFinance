import pandas as pd
import numpy as np
import random

def predict_stock_prices(ticker):
    """
    Simulates stock price prediction for a given ticker.
    Generates random data for demonstration purposes.
    """
    np.random.seed(42)  # For consistent results
    days = 30  # Simulate for 30 days
    prices = [random.uniform(100, 500) for _ in range(days)]
    dates = pd.date_range(start=pd.Timestamp.now(), periods=days).strftime("%Y-%m-%d")
    return pd.DataFrame({"Date": dates, "Predicted Price": prices}).set_index("Date")
