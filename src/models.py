"""
Trend Following Strategy Modules
--------------------------------
Implementation of the Société Générale Trend Indicator benchmark
designed to replicate diversified CTA trend-following returns.
"""

import pandas as pd
import numpy as np


def generate_trend_signals(df: pd.DataFrame, short_window: int = 20, long_window: int = 120) -> pd.DataFrame:
    """
    Calculates a 20/120 Simple Moving Average (SMA) Crossover.
    This is a reversal model that maintains a constant market position.
    """
    data = df.copy()

    # Calculate Simple Moving Averages
    data['SMA20'] = data['Close'].rolling(window=short_window).mean()
    data['SMA120'] = data['Close'].rolling(window=long_window).mean()

    # Signal Generation (Binary Reversal)
    # Long (+1) if SMA20 is above SMA120, otherwise Short (-1).
    data['Signal'] = (data['SMA20'] > data['SMA120']).map({True: 1, False: -1})

    # MaxBarsBack Enforcement (Burn-in Period)
    # Signals are neutralized until the 120-day lookback is fully populated.
    data.iloc[:long_window, data.columns.get_loc('Signal')] = 0
    data['Signal'] = data['Signal'].fillna(0).astype(int)

    return data