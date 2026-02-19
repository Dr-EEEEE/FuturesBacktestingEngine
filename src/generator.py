"""
Synthetic History Generator
---------------------------
Constructs multi-asset price series with endpoint convergence
for historical simulation and strategy stress-testing.
"""

import pandas as pd
import numpy as np
import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta

def generate_synthetic_history():
    script_dir = Path(__file__).resolve().parent
    data_folder = script_dir.parent / 'data'
    if data_folder.exists():
        shutil.rmtree(data_folder)
    os.makedirs(data_folder, exist_ok=True)

    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    offset = (today.weekday() - 4) % 7
    last_friday = today - timedelta(days=offset)

    dates = pd.date_range(start='2000-01-01', end=last_friday, freq='B')
    num_days = len(dates)

    anchors = {
        'ES': (1469, 6875), 'NQ': (3790, 24750), 'YM': (11350, 49600), 'RTY': (1100, 2644),
        'EMD': (1200, 3200), 'M2K': (1100, 2644), 'MES': (1469, 6875), 'MNQ': (3790, 24750),
        'MYM': (11350, 49600), 'SP': (1400, 6875), 'NK': (10000, 38500), 'NIY': (10000, 38500),
        'DAX': (6000, 18500), 'FTSE': (5000, 8400), 'NKY': (10000, 38500), 'STXE': (2500, 5200),
        'US': (100.0, 130.0), 'TY': (100.0, 115.0), 'FV': (100.0, 112.0), 'TU': (100.0, 105.0),
        'ZN': (80.0, 113.0), 'ZB': (70.0, 122.0), 'ZT': (100.0, 106.0), 'ZF': (95.0, 110.0),
        'ED': (94.0, 97.0), 'FF': (95.0, 96.5), 'FGBL': (110.0, 135.0), 'CONF': (110.0, 140.0),
        'JGB': (130.0, 145.0), 'FGBM': (110.0, 125.0), 'FGBX': (100.0, 150.0), 'FGBS': (100.0, 105.0),
        'GC': (288.0, 5030.0), 'SI': (5.30, 76.50), 'HG': (0.80, 5.75), 'PL': (600, 1100), 'PA': (400, 1200),
        'CL': (25.6, 63.8), 'QM': (25.0, 60.0), 'NG': (1.80, 3.10), 'RB': (0.80, 1.92),
        'HO': (0.80, 2.41), 'QH': (0.80, 2.41), 'QU': (0.80, 1.92),
        'C': (210.0, 480.0), 'S': (500.0, 1150.0), 'W': (300.0, 620.0), 'SB': (10.0, 25.0),
        'AD': (0.50, 0.68), 'CD': (0.60, 0.72), 'EC': (0.90, 1.08), 'BP': (1.20, 1.25),
        'JY': (0.006, 0.0065), 'MP1': (0.04, 0.05), 'NE1': (0.45, 0.60), 'SF': (0.60, 0.88), 'DX': (80.0, 104.5)
    }

    # Bond identification list
    bond_syms = ['US', 'TY', 'FV', 'TU', 'ZN', 'ZB', 'ZT', 'ZF', 'FGBL', 'CONF', 'JGB', 'FGBM', 'FGBX', 'FGBS']

    for symbol, (start_val, target_val) in anchors.items():
        t = np.linspace(0, 1, num_days)
        is_equity = symbol in ['ES', 'NQ', 'YM', 'RTY', 'EMD', 'M2K', 'MES', 'MNQ', 'MYM', 'SP', 'NK', 'NIY', 'DAX', 'FTSE', 'NKY', 'STXE']
        is_metal = symbol in ['GC', 'SI', 'HG', 'PL', 'PA']
        is_bond = any(s == symbol for s in bond_syms)

        drift = start_val + (target_val - start_val) * t

        if is_equity:
            harmonics = (np.sin(t * 6 * np.pi) * 0.04 +
                        np.sin(t * 25 * np.pi) * 0.03) * (0.7 + t * 0.5)
            base_vol = 0.06
        elif is_metal:
            harmonics = (np.sin(t * 20 * np.pi) * 0.08 +
                        np.sin(t * 60 * np.pi) * 0.05) * (0.6 + t * 0.4)
            base_vol = 0.085
        else:
            harmonics = np.sin(t * 40 * np.pi) * 0.07
            base_vol = 0.05 if is_bond else 0.08

        vol_ramp = 1.3 + (t * 2.2)
        stochastic_walk = np.cumsum(np.random.normal(0, base_vol, num_days)) * vol_ramp

        raw_series = drift * (1 + harmonics) + (stochastic_walk * start_val * 0.20)

        error = raw_series[-1] - target_val
        adjustment = t * error
        final_series = raw_series - adjustment
        final_series = np.maximum(final_series, start_val * 0.05)

        # Precision logic updated for all Bond symbols
        if symbol == 'JY':
            tick, decimals = 0.000001, 6
        elif symbol in ['AD', 'CD', 'EC', 'BP', 'NE1', 'SF']:
            tick, decimals = 0.0001, 4
        elif is_bond:
            tick, decimals = 0.03125, 5
        elif any(s in symbol for s in ['ES', 'NQ', 'C', 'S', 'W']):
            tick, decimals = 0.25, 2
        else:
            tick, decimals = 0.01, 2

        final_series = np.round(final_series / tick) * tick
        final_series[-1] = target_val

        df = pd.DataFrame({'Date': dates, 'Open': final_series, 'High': final_series + tick,
                           'Low': final_series - tick, 'Close': final_series})

        for col in ['Open', 'High', 'Low', 'Close']:
            df[col] = df[col].apply(lambda x: f"{x:.{decimals}f}")

        df.to_csv(data_folder / f"{symbol}.csv", index=False)

    print(f"Dataset Generation Complete | Terminal Date: {dates[-1].strftime('%Y-%m-%d')}")

if __name__ == "__main__":
    generate_synthetic_history()