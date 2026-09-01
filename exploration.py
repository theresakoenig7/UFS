from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

# Unterordner mit den CSV-Dateien
input_dir = Path("03_LueckenloseDaten")

# Ordner fuer die gespeicherten Plots (wird bei Bedarf angelegt)
output_dir = Path("plots")
output_dir.mkdir(exist_ok=True)

for csv_path in input_dir.glob("*.csv"):
    df = pd.read_csv(csv_path, parse_dates=["Zulu"])
    df = df.set_index("Zulu")

    plt.figure(figsize=(10, 5))
    plt.plot(df.index, df["Temp"])
    plt.xlabel("Datum")
    plt.ylabel("Wert")
    plt.title(csv_path.stem)
    plt.tight_layout()

    output_path = output_dir / f"{csv_path.stem}.png"
    plt.savefig(output_path)
    plt.show()