"""
Futures Backtesting Engine - Contract Specifications
Reference for Big Point Values (BPV) and Tick Sizes.

This module maps exchange-traded symbols to their specific mechanical
properties for accurate PnL and risk calculations.
"""

from typing import Optional

# Symbol-specific mechanical specifications
CONTRACT_SPECS = {
    # --- EQUITY INDICES ---
    'ES':  {'name': 'E-mini S&P 500', 'tick': 0.25, 'bpv': 50},
    'MES': {'name': 'Micro E-mini S&P 500', 'tick': 0.25, 'bpv': 5},
    'NQ':  {'name': 'E-mini NASDAQ-100', 'tick': 0.25, 'bpv': 20},
    'MNQ': {'name': 'Micro E-mini Nasdaq-100', 'tick': 0.25, 'bpv': 2},
    'YM':  {'name': 'E-mini Dow Futures', 'tick': 1.00, 'bpv': 5},
    'MYM': {'name': 'Micro E-mini Dow', 'tick': 1.00, 'bpv': 0.50},
    'RTY': {'name': 'E-mini Russell 2000 Idx', 'tick': 0.10, 'bpv': 50},
    'M2K': {'name': 'Micro E-mini Russell 2000', 'tick': 0.10, 'bpv': 5},
    'EMD': {'name': 'E-mini S&P MidCap 400', 'tick': 0.10, 'bpv': 100},
    'SP':  {'name': 'S&P 500 (Big)', 'tick': 0.10, 'bpv': 250},
    'NIY': {'name': 'Nikkei 225 Yen Denominated', 'tick': 5.0, 'bpv': 500},
    'NK':  {'name': 'Nikkei 225 USD', 'tick': 5.0, 'bpv': 5},

    # --- METALS ---
    'GC': {'name': 'Gold', 'tick': 0.10, 'bpv': 100},
    'SI': {'name': 'Silver', 'tick': 0.005, 'bpv': 5000},
    'HG': {'name': 'Copper', 'tick': 0.0005, 'bpv': 25000},
    'PL': {'name': 'Platinum', 'tick': 0.10, 'bpv': 50},

    # --- ENERGIES ---
    'CL': {'name': 'Crude Oil', 'tick': 0.01, 'bpv': 1000},
    'QM': {'name': 'E-mini Crude Oil', 'tick': 0.025, 'bpv': 500},
    'NG': {'name': 'Natural Gas', 'tick': 0.001, 'bpv': 10000},
    'QN': {'name': 'miNY Natural Gas', 'tick': 0.005, 'bpv': 2500},
    'RB': {'name': 'NY Harbor RBOB Gasoline', 'tick': 0.0001, 'bpv': 42000},
    'HO': {'name': 'Heating Oil', 'tick': 0.0001, 'bpv': 42000},
    'QH': {'name': 'E-mini Heating Oil', 'tick': 0.0001, 'bpv': 42000},
    'QU': {'name': 'E-mini Gasoline', 'tick': 0.0001, 'bpv': 42000},

    # --- INTEREST RATES ---
    'US': {'name': '30 Yr U.S. Treasury Bonds', 'tick': 0.03125, 'bpv': 1000},
    'TY': {'name': '10 Yr U.S. Treasury Notes', 'tick': 0.015625, 'bpv': 1000},
    'FV': {'name': '5 Yr U.S. Treasury Notes', 'tick': 0.0078125, 'bpv': 1000},
    'TU': {'name': '2 Year U.S. Treasury Notes', 'tick': 0.00390625, 'bpv': 2000},
    'ED': {'name': 'Eurodollar', 'tick': 0.005, 'bpv': 2500},
    'FF': {'name': '30 Day Federal Funds', 'tick': 0.005, 'bpv': 4167},

    # --- CURRENCIES ---
    'AD':  {'name': 'Australian Dollar', 'tick': 0.0001, 'bpv': 100000},
    'BP':  {'name': 'British Pound', 'tick': 0.0001, 'bpv': 62500},
    'CD':  {'name': 'Canadian Dollar', 'tick': 0.0001, 'bpv': 100000},
    'EC':  {'name': 'Euro FX', 'tick': 0.0001, 'bpv': 125000},
    'E7':  {'name': 'E-Mini Euro FX', 'tick': 0.0001, 'bpv': 62500},
    'JY':  {'name': 'Japanese Yen', 'tick': 0.000001, 'bpv': 12500000},
    'J7':  {'name': 'E-Mini Japanese Yen', 'tick': 0.000001, 'bpv': 6250000},
    'SF':  {'name': 'Swiss Franc', 'tick': 0.0001, 'bpv': 125000},
    'DX':  {'name': 'U.S. Dollar Index', 'tick': 0.005, 'bpv': 1000},
    'MP1': {'name': 'Mexican Peso', 'tick': 0.00001, 'bpv': 500000},
    'NE1': {'name': 'New Zealand Dollar', 'tick': 0.0001, 'bpv': 100000},

    # --- AGRICULTURE & LIVESTOCK ---
    'C':  {'name': 'Corn', 'tick': 0.25, 'bpv': 50},
    'S':  {'name': 'Soybeans', 'tick': 0.25, 'bpv': 50},
    'W':  {'name': 'Wheat', 'tick': 0.25, 'bpv': 50},
    'KW': {'name': 'Hard Red Winter Wheat', 'tick': 0.25, 'bpv': 50},
    'KC': {'name': 'Coffee C', 'tick': 0.05, 'bpv': 375},
    'SB': {'name': 'Sugar No. 11', 'tick': 0.01, 'bpv': 1120},
    'CC': {'name': 'Cocoa', 'tick': 1.0, 'bpv': 10},
    'CT': {'name': 'Cotton No. 2', 'tick': 0.01, 'bpv': 500},
    'LC': {'name': 'Live Cattle', 'tick': 0.025, 'bpv': 400},
    'LH': {'name': 'Lean Hogs', 'tick': 0.025, 'bpv': 400},
    'FC': {'name': 'Feeder Cattle', 'tick': 0.025, 'bpv': 200},
    'OJ': {'name': 'Frozen Concentrated Orange Juice', 'tick': 0.05, 'bpv': 150},
    'BO': {'name': 'Soybean Oil', 'tick': 0.01, 'bpv': 600},
    'SM': {'name': 'Soybean Meal', 'tick': 0.1, 'bpv': 100},
    'RR': {'name': 'Rough Rice', 'tick': 0.01, 'bpv': 2000},
    'O':  {'name': 'Oats', 'tick': 0.25, 'bpv': 50},
}

def get_tick_value(symbol: str) -> Optional[float]:
    """
    Returns the dollar value of a single tick (Tick Size * BPV).

    Args:
        symbol: The ticker symbol (e.g., 'ES', 'CL').

    Returns:
        The dollar value per tick, or None if the symbol is not found.
    """
    spec = CONTRACT_SPECS.get(symbol)
    if spec:
        return float(spec['tick'] * spec['bpv'])
    return None