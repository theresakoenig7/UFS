from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Unterordner mit den CSV-Dateien
input_dir = Path("03_LueckenloseDaten")

# Ordner fuer die gespeicherten Plots (wird bei Bedarf angelegt)
output_dir = Path("plots")
output_dir.mkdir(exist_ok=True)

for csv_path in input_dir.glob("*.csv"):
    df = pd.read_csv(csv_path, parse_dates=["Zulu"])
    df = df.set_index("Zulu")

    fig, ax = plt.subplots(figsize=(20, 5))
    ax.plot(df.index, df["Temp"])

    # Tick fuer jede Minute
    ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=5))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    plt.xticks(rotation=90, fontsize=7)

    ax.set_xlabel("Datum")
    ax.set_ylabel("Wert")
    ax.set_title(csv_path.stem)
    plt.tight_layout()

    output_path = output_dir / f"{csv_path.stem}.png"
    plt.savefig(output_path)
    plt.close()