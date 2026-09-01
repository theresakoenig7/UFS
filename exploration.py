from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from scipy.optimize import curve_fit

# Unterordner mit den CSV-Dateien
input_dir = Path("03_LueckenloseDaten")

# Ordner fuer die gespeicherten Plots (wird bei Bedarf angelegt)
output_dir = Path("plots")
output_dir.mkdir(exist_ok=True)

fit_start_times = {
    "GRIPS6_2016012122": "22:28:00",
    "GRIPS7_2016012122": "22:25:00",
    "GRIPS16_2016012122": "22:35:00",
    "GRIPS6_2016012930": "23:35:00",
    "GRIPS7_2016012930": "23:30:00",
    "GRIPS16_2016012930": "23:50:00",
}
frequency_guesses = {
    "GRIPS6_2016012122": 1 / 16200,
    "GRIPS7_2016012122": 1 / 16200,
    "GRIPS16_2016012122": 1 / 16200,
    "GRIPS6_2016012930": 1 / 16200,
    "GRIPS7_2016012930": 1 / 16200,
    "GRIPS16_2016012930": 1 / 16200,
}
def sine_func(t, amplitude, frequency, phase, offset):
    """Return a sine curve evaluated at t with the given parameters."""
    return amplitude * np.sin(2 * np.pi * frequency * t + phase) + offset

for csv_path in input_dir.glob("*.csv"):
    df = pd.read_csv(csv_path, parse_dates=["Zulu"])
    df = df.set_index("Zulu")

    fig, ax = plt.subplots(figsize=(20, 5))
    ax.plot(df.index, df["Temp"], alpha=0.5)

    fit_start_time = fit_start_times.get(csv_path.stem)

    if fit_start_time is not None:
        fit_df = df.between_time(fit_start_time, df.index[-1].strftime("%H:%M:%S"))

        if len(fit_df) > 3:
            t_seconds = (fit_df.index - fit_df.index[0]).total_seconds().to_numpy()
            y_values = fit_df["Temp"].to_numpy()

            amplitude_guess = (y_values.max() - y_values.min()) / 2
            offset_guess = y_values.mean()
            frequency_guess = frequency_guesses.get(csv_path.stem, 1 / 16200)
            initial_guess = [amplitude_guess, frequency_guess, 0, offset_guess]

            params, _ = curve_fit(sine_func, t_seconds, y_values, p0=initial_guess, maxfev=10000)

            fit_values = sine_func(t_seconds, *params)
            ax.plot(fit_df.index, fit_values, label="Sinus-Fit", linestyle="--")
    else:
        print(f"Keine Fit-Startzeit fuer {csv_path.stem} definiert, ueberspringe Fit.")

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


groups = ["2122", "2930"]

for group in groups:
    fig, ax = plt.subplots(figsize=(20, 5))

    for csv_path in sorted(input_dir.glob(f"*{group}*.csv")):
        df = pd.read_csv(csv_path, parse_dates=["Zulu"])
        df = df.set_index("Zulu")

        fit_start_time = fit_start_times.get(csv_path.stem)

        if fit_start_time is None:
            print(f"Keine Fit-Startzeit fuer {csv_path.stem} definiert, ueberspringe Fit.")
            continue

        fit_df = df.between_time(fit_start_time, df.index[-1].strftime("%H:%M:%S"))

        if len(fit_df) <= 3:
            continue

        t_seconds = (fit_df.index - fit_df.index[0]).total_seconds().to_numpy()
        y_values = fit_df["Temp"].to_numpy()

        amplitude_guess = (y_values.max() - y_values.min()) / 2
        offset_guess = y_values.mean()
        frequency_guess = frequency_guesses.get(csv_path.stem, 1 / 16200)
        initial_guess = [amplitude_guess, frequency_guess, 0, offset_guess]

        params, _ = curve_fit(sine_func, t_seconds, y_values, p0=initial_guess, maxfev=10000)

        fit_values = sine_func(t_seconds, *params)
        ax.plot(fit_df.index, fit_values, label=csv_path.stem, linestyle="--")

    ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=5))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    plt.xticks(rotation=90, fontsize=7)

    ax.set_xlabel("Datum")
    ax.set_ylabel("Wert")
    ax.set_title(f"Sinus-Fits {group}")
    ax.legend()
    plt.tight_layout()

    output_path = output_dir / f"sinus_fits_{group}.png"
    plt.savefig(output_path)
    plt.close()

stations = ["GRIPS6", "GRIPS7", "GRIPS16"]
groups = ["2122", "2930"]

for group in groups:
    fig, axes = plt.subplots(len(stations), 1, figsize=(20, 12), sharex=True)
    fig.suptitle(f"Sinus-Fits {group}", fontsize=20, fontweight='bold')

    for row, station in enumerate(stations):
        ax = axes[row]

        matches = list(input_dir.glob(f"*{station}*{group}*.csv"))
        if not matches:
            continue

        csv_path = matches[0]
        df = pd.read_csv(csv_path, parse_dates=["Zulu"])
        df = df.set_index("Zulu")

        ax.plot(df.index, df["Temp"], alpha=0.5)

        fit_start_time = fit_start_times.get(csv_path.stem)

        if fit_start_time is not None:
            fit_df = df.between_time(fit_start_time, df.index[-1].strftime("%H:%M:%S"))

            if len(fit_df) > 3:
                t_seconds = (fit_df.index - fit_df.index[0]).total_seconds().to_numpy()
                y_values = fit_df["Temp"].to_numpy()

                amplitude_guess = (y_values.max() - y_values.min()) / 2
                offset_guess = y_values.mean()
                frequency_guess = frequency_guesses.get(csv_path.stem, 1 / 16200)
                initial_guess = [amplitude_guess, frequency_guess, 0, offset_guess]

                params, _ = curve_fit(sine_func, t_seconds, y_values, p0=initial_guess, maxfev=10000)

                fit_values = sine_func(t_seconds, *params)
                ax.plot(fit_df.index, fit_values, label="Sinus-Fit", linestyle="--", color='salmon')

        ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=10))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        ax.tick_params(axis="x", rotation=45, labelsize=13)
        ax.tick_params(axis="y", labelsize=13)

        ax.set_title(f'{csv_path.stem[0:6]}', fontsize=20, fontweight='bold')
        ax.set_ylabel("Wert", fontsize=20, fontweight='bold')

    plt.tight_layout()

    output_path = output_dir / f"grid_sinus_fits_{group}.png"
    plt.savefig(output_path)
    plt.close()