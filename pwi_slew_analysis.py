import pandas as pd
import time
import os

# ================= CONFIG =================

INPUT_FILE = r"C:\Users\Rohit\OneDrive - Digantara Research and Technologies Pvt. Ltd\Documents\PlaneWave Instruments\PWI4\Logs\Telemetry\Telemetry.csv"

# ===========================================


def clean_columns(df):
    df.columns = df.columns.str.strip()
    df.columns = df.columns.str.replace("#", "", regex=False)
    df.columns = df.columns.str.strip()
    return df


def get_latest_sample():
    df = pd.read_csv(INPUT_FILE)
    df = clean_columns(df)

    df["utc_time"] = pd.to_datetime(df["utc_time"])
    df["tele_alt_degs"] = pd.to_numeric(df["tele_alt_degs"], errors="coerce")
    df["tele_azm_degs"] = pd.to_numeric(df["tele_azm_degs"], errors="coerce")

    df = df.dropna(subset=["utc_time", "tele_alt_degs", "tele_azm_degs"])

    return df.iloc[-1]


def calculate_slew_details(start_time, end_time):
    df = pd.read_csv(INPUT_FILE)
    df = clean_columns(df)

    df["utc_time"] = pd.to_datetime(df["utc_time"])
    df["tele_alt_degs"] = pd.to_numeric(df["tele_alt_degs"], errors="coerce")
    df["tele_azm_degs"] = pd.to_numeric(df["tele_azm_degs"], errors="coerce")

    df = df.dropna(subset=["utc_time", "tele_alt_degs", "tele_azm_degs"])

    # Filter between start and end
    df = df[(df["utc_time"] >= start_time) & (df["utc_time"] <= end_time)]

    df["time_diff"] = df["utc_time"].diff().dt.total_seconds()
    df["alt_slew_rate"] = df["tele_alt_degs"].diff() / df["time_diff"]
    df["az_slew_rate"] = df["tele_azm_degs"].diff() / df["time_diff"]

    max_alt_speed = df["alt_slew_rate"].abs().max()
    max_az_speed = df["az_slew_rate"].abs().max()

    return max_alt_speed, max_az_speed


def main():

    print("========== PWI ALT/AZ SLEW TEST ==========\n")
    print("Make sure mount is at PARK position (Az=90, Alt=15)")
    input("Press ENTER to capture START position...")

    start_sample = get_latest_sample()

    start_time = start_sample["utc_time"]
    start_alt = start_sample["tele_alt_degs"]
    start_az = start_sample["tele_azm_degs"]

    print("\nStart Position Captured:")
    print(f"Time     : {start_time}")
    print(f"Altitude : {start_alt:.4f} deg")
    print(f"Azimuth  : {start_az:.4f} deg")

    print("\nNow slew mount to target position (example Az=180, Alt=90)")
    input("After movement completes, press ENTER to capture END position...")

    end_sample = get_latest_sample()

    end_time = end_sample["utc_time"]
    end_alt = end_sample["tele_alt_degs"]
    end_az = end_sample["tele_azm_degs"]

    print("\nEnd Position Captured:")
    print(f"Time     : {end_time}")
    print(f"Altitude : {end_alt:.4f} deg")
    print(f"Azimuth  : {end_az:.4f} deg")

    # Calculate differences
    alt_moved = end_alt - start_alt
    az_moved = end_az - start_az
    total_time = (end_time - start_time).total_seconds()

    avg_alt_speed = alt_moved / total_time if total_time != 0 else 0
    avg_az_speed = az_moved / total_time if total_time != 0 else 0

    max_alt_speed, max_az_speed = calculate_slew_details(start_time, end_time)

    print("\n========== SLEW ANALYSIS ==========\n")
    print(f"Total Time Taken     : {total_time:.2f} sec")
    print(f"Altitude Moved       : {alt_moved:.4f} deg")
    print(f"Azimuth Moved        : {az_moved:.4f} deg")
    print(f"Average Alt Speed    : {avg_alt_speed:.4f} deg/sec")
    print(f"Average Az Speed     : {avg_az_speed:.4f} deg/sec")
    print(f"Maximum Alt Speed    : {max_alt_speed:.4f} deg/sec")
    print(f"Maximum Az Speed     : {max_az_speed:.4f} deg/sec")

    print("\n========== TEST COMPLETE ==========")


if __name__ == "__main__":
    main()
