import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
import numpy as np
from matplotlib.ticker import StrMethodFormatter, MultipleLocator
from pathlib import Path
from matplotlib.patches import Patch

# Core Strategy and Engine Imports
from models import generate_trend_signals
from engine import CONTRACT_SPECS, get_tick_value

try:
    matplotlib.use('TkAgg')
except:
    pass


def run_portfolio_backtest():
    """
    Core backtesting engine for multi-asset futures simulation
    using the SG Trend Indicator model and precise contract specs.
    """
    initial_capital = 10_000_000
    capital = 10_000_000

    # Portfolio Risk Budgeting
    target_daily_vol_dollars = capital * 0.0030
    num_assets = 57
    risk_per_asset = target_daily_vol_dollars / np.sqrt(num_assets)

    script_dir = Path(__file__).resolve().parent
    data_folder = script_dir.parent / 'data'

    sectors = {
        'Equity Indices': ['ES', 'NQ', 'YM', 'RTY', 'EMD', 'M2K', 'MES', 'MNQ', 'MYM', 'SP', 'NK', 'NIY', 'DAX', 'FTSE',
                           'NKY', 'STXE'],
        'Rates and Bonds': ['US', 'TY', 'FV', 'TU', 'ZN', 'ZB', 'ZT', 'ZF', 'ED', 'FF', 'FGBL', 'CONF', 'JGB', 'FGBM',
                            'FGBX', 'FGBS'],
        'Metals': ['GC', 'SI', 'HG', 'PL', 'PA'],
        'Energies': ['CL', 'QM', 'NG', 'RB', 'HO', 'QH', 'QU'],
        'Agriculture': ['C', 'S', 'W', 'SB'],
        'Currencies': ['AD', 'CD', 'EC', 'BP', 'JY', 'MP1', 'NE1', 'SF', 'DX']
    }

    if not data_folder.exists():
        return

    all_files = [f for f in os.listdir(data_folder) if f.endswith('.csv')]
    sector_pnls = {sector: [] for sector in sectors}

    for file in all_files:
        symbol = file.split('.')[0]
        current_sector = next((s for s, syms in sectors.items() if symbol in syms), None)
        if not current_sector:
            continue

        df = pd.read_csv(data_folder / file, parse_dates=['Date'])

        # PRECISE CONTRACT SPECIFICATION MAPPING FROM ENGINE.PY
        # This replaces the hard-coded if/elif blocks for 100% accuracy
        spec = CONTRACT_SPECS.get(symbol)
        if spec:
            tick_size = spec['tick']
            tick_val = get_tick_value(symbol)
        else:
            # Fallback only if symbol is missing from engine.py
            tick_size, tick_val = 0.01, 10.00

        # Apply the actual Trend Indicator model from models.py
        df = generate_trend_signals(df)

        # Volatility-Adjusted Position Sizing
        df['Daily_Range'] = df['Close'].diff().abs().rolling(40).mean()
        contract_vola_dollars = df['Daily_Range'] * (tick_val / tick_size)
        df['Pos_Size'] = (risk_per_asset / contract_vola_dollars.replace(0, np.nan)).fillna(0)

        # Exposure Management (Sector Caps)
        cap = 4 if current_sector == 'Currencies' else 1 if current_sector == 'Equity Indices' else 15
        df['Pos_Size'] = df['Pos_Size'].clip(0, cap).round()

        multiplier = (tick_val / tick_size)
        df['Net_PnL'] = (df['Close'].diff() * multiplier * df['Pos_Size'] * df['Signal'].shift(1)).fillna(0)
        sector_pnls[current_sector].append(df.set_index('Date')['Net_PnL'])

    # --- VISUALIZATION CODE REMAINS UNCHANGED ---
    fig, ax = plt.subplots(figsize=(22, 11))
    plt.suptitle("BACKTEST RESULTS FOR SOCIETE GENERALE TREND INDICATOR",
                 fontsize=20, fontweight='bold', color='#1a1a1a', y=0.95)

    manager = plt.get_current_fig_manager()
    try:
        manager.window.state('zoomed')
    except:
        pass

    ax.set_facecolor('white')
    total_portfolio_pnl = []
    colors = ['#0077FF', '#FF8800', '#00CC44', '#FF3333', '#AA33FF', '#00CCCC']
    plot_lines = []

    for i, (sector_name, pnl_list) in enumerate(sector_pnls.items()):
        if not pnl_list:
            continue
        combined = pd.concat(pnl_list, axis=1).fillna(0).sum(axis=1)
        total_portfolio_pnl.append(combined)
        line, = ax.plot(capital + combined.cumsum(), label=sector_name, linewidth=2.3, color=colors[i % len(colors)])
        plot_lines.append(line)

    if total_portfolio_pnl:
        overall = pd.concat(total_portfolio_pnl, axis=1).fillna(0).sum(axis=1)
        equity_curve = capital + overall.cumsum()
        total_line, = ax.plot(equity_curve, color='black', linewidth=4.2, label='TOTAL PORTFOLIO', zorder=10)
        plot_lines.append(total_line)

        # Performance Metrics Calculation
        total_days = len(equity_curve)
        final_ratio = equity_curve.iloc[-1] / capital
        ann_ret = (pow(max(0.01, final_ratio), (252 / total_days)) - 1) * 100
        daily_rets = overall / capital
        sharpe = (daily_rets.mean() / daily_rets.std() * np.sqrt(252)) if daily_rets.std() != 0 else 0
        downside_rets = daily_rets[daily_rets < 0]
        sortino = (daily_rets.mean() / downside_rets.std() * np.sqrt(252)) if not downside_rets.empty else 0

        # Attribution Overlays
        leg1 = ax.legend(loc='upper left', frameon=True, shadow=True, fontsize=15, title="SECTORS")
        ax.add_artist(leg1)

        stats_text = (f"  ANNUALIZED RETURN │ {ann_ret:>8.2f}%\n"
                      f"  SHARPE RATIO      │ {sharpe:>8.2f}\n"
                      f"  SORTINO RATIO     │ {sortino:>8.2f}")

        ax.legend([Patch(visible=False)], [stats_text], loc='upper left', bbox_to_anchor=(0.22, 1.0),
                  frameon=True, shadow=True, handlelength=0, title="PERFORMANCE METRICS",
                  prop={'family': 'monospace', 'size': 15, 'weight': 'bold'})

    # Interactive Cursor Logic
    annot = ax.annotate("", xy=(0, 0), xytext=(20, 20), textcoords="offset points",
                        bbox=dict(boxstyle="round", fc="white", alpha=0.9, ec="gray"),
                        arrowprops=dict(arrowstyle="->"))
    annot.set_visible(False)

    def update_annot(line, idx):
        x_data, y_data = line.get_data()
        annot.xy = (x_data[idx], y_data[idx])
        date_str = pd.to_datetime(x_data[idx]).strftime('%Y-%m-%d')
        text = f"{line.get_label()}\n{date_str}\n${y_data[idx]:,.0f}"
        annot.set_text(text)

    def hover(event):
        if event.inaxes == ax:
            for line in plot_lines:
                cont, ind = line.contains(event)
                if cont:
                    update_annot(line, ind["ind"][0])
                    annot.set_visible(True)
                    fig.canvas.draw_idle()
                    return
        if annot.get_visible():
            annot.set_visible(False)
            fig.canvas.draw_idle()

    fig.canvas.mpl_connect("motion_notify_event", hover)

    # Scaling and Label Configuration
    ax.set_xlim(left=pd.Timestamp('2000-01-01'), right=equity_curve.index.max())
    ax.set_ylim(bottom=0, top=max(20_000_000, equity_curve.max() * 1.1))

    ax.xaxis.set_major_locator(mdates.YearLocator(1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.yaxis.set_major_locator(MultipleLocator(5_000_000))
    ax.yaxis.set_major_formatter(StrMethodFormatter('${x:,.0f}'))

    # Original Labeling Styles
    ax.set_ylabel('Account Value', fontsize=22, fontweight='bold', labelpad=50)
    ax.set_xlabel('Date', fontsize=22, fontweight='bold', labelpad=25)

    ax.grid(True, linestyle=':', color='lightgray', alpha=0.8)
    plt.subplots_adjust(left=0.13, right=0.96, top=0.90, bottom=0.12)

    # Output Management
    plots_folder = script_dir.parent / 'plots'
    os.makedirs(plots_folder, exist_ok=True)
    plt.savefig(plots_folder / 'performance.png', dpi=300, bbox_inches='tight')

    plt.show()


if __name__ == "__main__":
    run_portfolio_backtest()