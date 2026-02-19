import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
from pathlib import Path

# Ensure interactive backend for windowed display
try:
    matplotlib.use('TkAgg')
except:
    pass


def plot_hover_visualizer():
    """
    Interactive diagnostic tool to visualize normalized asset performance.
    Uses actual CSV date columns for 100% temporal accuracy.
    """
    plt.style.use('default')
    script_dir = Path(__file__).resolve().parent
    data_folder = script_dir.parent / 'data'

    # Filter excluded assets
    excluded = ['BTC.csv', 'ETH.csv']
    all_files = sorted([f for f in os.listdir(data_folder)
                        if f.endswith('.csv') and f not in excluded])

    if not all_files:
        print("No CSV files found in /data/")
        return

    fig, ax = plt.subplots(figsize=(16, 9))
    fig.patch.set_facecolor('white')

    # Maximize window if supported
    manager = plt.get_current_fig_manager()
    try:
        manager.window.state('zoomed')
    except:
        pass

    colormap = plt.colormaps['gist_rainbow'].resampled(len(all_files))
    lines = []

    for i, file in enumerate(all_files):
        symbol = file.replace('.csv', '')
        # Read actual dates from the file
        df = pd.read_csv(data_folder / file, parse_dates=['Date'])

        # Rebase price series to 100
        norm_series = (df['Close'] / df['Close'].iloc[0]) * 100

        # Plot using the actual Date column from the CSV
        line, = ax.plot(df['Date'], norm_series, label=symbol, color=colormap(i),
                        linewidth=1.0, alpha=0.3)
        lines.append(line)

    # Scale X-axis to match data limits
    ax.set_xlim(left=df['Date'].min(), right=df['Date'].max())

    # Temporal axis formatting
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    plt.xticks(rotation=0, ha='center', fontsize=9)

    # Interactive Symbol Tooltip
    annot = ax.annotate("", xy=(0, 0), xytext=(15, 15),
                        textcoords="offset points",
                        bbox=dict(boxstyle="round,pad=0.3", fc="#FFFFCC", ec="black", alpha=0.9),
                        arrowprops=dict(arrowstyle="->"))
    annot.set_visible(False)

    def hover(event):
        if event.inaxes == ax:
            found = False
            for line in lines:
                cont, ind = line.contains(event)
                if cont:
                    annot.xy = (event.xdata, event.ydata)
                    annot.set_text(f"Symbol: {line.get_label()}")
                    annot.get_bbox_patch().set_edgecolor(line.get_color())
                    annot.set_visible(True)
                    line.set_linewidth(3.0)
                    line.set_alpha(1.0)
                    found = True
                else:
                    line.set_linewidth(1.0)
                    line.set_alpha(0.3)

            if not found:
                annot.set_visible(False)
            fig.canvas.draw_idle()

    fig.canvas.mpl_connect("motion_notify_event", hover)

    ax.set_title("NORMALIZED ASSET COMPARISON", fontsize=18, fontweight='bold', pad=30)
    ax.axhline(100, color='black', linestyle='-', alpha=0.2, linewidth=1)
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel("Normalized Value (Base 100)", fontsize=12)
    ax.grid(True, axis='x', linestyle=':', alpha=0.5)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    plot_hover_visualizer()