import tkinter as tk
from tkinter import scrolledtext, messagebox
import subprocess
import time
import threading
import math

# ---------------- CONFIG ---------------- #

BASE_URL = "http://localhost:8220"

MOUNT_CONNECT_URL = f"{BASE_URL}/mount/connect"
MOUNT_ENABLE_URL  = f"{BASE_URL}/mount/enable"
MOUNT_GOTO_URL    = f"{BASE_URL}/mount/goto_alt_az"
STATUS_URL        = f"{BASE_URL}/status"

ALT_AZ_TOLERANCE = 0.05
POLL_INTERVAL = 0.01
SLEW_TIMEOUT = 120

SPEED_LOG_FILE = "slew_speed_log.txt"


# ---------------- UTIL ---------------- #

def send_get(url, params=None):
    cmd = ["curl", "-s", url]
    if params:
        query = "&".join([f"{k}={v}" for k, v in params.items()])
        cmd[-1] = f"{url}?{query}"
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return None
    return result.stdout


def parse_status(text):
    data = {}
    for line in text.splitlines():
        if "=" in line:
            key, value = line.strip().split("=", 1)
            data[key] = value
    return data


def log_speed_to_file(test_name, speed, elapsed, distance):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(SPEED_LOG_FILE, "a") as f:
        f.write(
            f"{timestamp} | {test_name} | "
            f"Distance: {distance:.4f} deg | "
            f"Time: {elapsed:.4f} sec | "
            f"Speed: {speed:.4f} deg/sec\n"
        )


def initialize_mount():
    send_get(MOUNT_CONNECT_URL)
    time.sleep(0.3)
    send_get(MOUNT_ENABLE_URL)
    time.sleep(0.3)


def wait_until_reached(target_alt, target_az):
    deadline = time.time() + SLEW_TIMEOUT
    while True:
        if time.time() > deadline:
            return False

        raw = send_get(STATUS_URL)
        if not raw:
            continue

        status = parse_status(raw)

        curr_alt = float(status.get("mount.altitude_degs", 0))
        curr_az  = float(status.get("mount.azimuth_degs", 0))
        is_slewing = status.get("mount.is_slewing", "true") == "true"

        live_position_label.config(
            text=f"Live Alt: {curr_alt:.3f}°   Live Az: {curr_az:.3f}°"
        )

        az_diff = abs(curr_az - target_az)
        if az_diff > 180:
            az_diff = 360 - az_diff

        alt_diff = abs(curr_alt - target_alt)

        if (not is_slewing) and \
           (alt_diff <= ALT_AZ_TOLERANCE) and \
           (az_diff <= ALT_AZ_TOLERANCE):
            return True

        time.sleep(POLL_INTERVAL)


# ---------------- NORMAL SLEW ---------------- #

def start_slew():
    try:
        alt = float(entry_alt.get())
        az  = float(entry_az.get())
    except ValueError:
        messagebox.showerror("Error", "Invalid Alt / Az")
        return

    threading.Thread(target=run_normal_slew, args=(alt, az), daemon=True).start()


def run_normal_slew(target_alt, target_az):

    initialize_mount()

    raw_status = send_get(STATUS_URL)
    status = parse_status(raw_status)

    start_alt = float(status.get("mount.altitude_degs", 0))
    start_az  = float(status.get("mount.azimuth_degs", 0))

    start_time = time.perf_counter()

    log_box.insert(tk.END, "\n--- Normal Slew ---\n")
    log_box.see(tk.END)

    send_get(MOUNT_GOTO_URL, {"alt_degs": target_alt, "az_degs": target_az})

    if not wait_until_reached(target_alt, target_az):
        status_label.config(text="Timeout!", fg="red")
        return

    elapsed = time.perf_counter() - start_time

    delta_alt = target_alt - start_alt
    delta_az  = target_az - start_az

    if abs(delta_az) > 180:
        delta_az = 360 - abs(delta_az)

    total_distance = math.sqrt(delta_alt**2 + delta_az**2)
    slew_speed = total_distance / elapsed if elapsed > 0 else 0

    log_box.insert(
        tk.END,
        f"Distance: {total_distance:.4f} deg\n"
        f"Time: {elapsed:.4f} sec\n"
        f"Average Speed: {slew_speed:.4f} deg/sec\n"
        + "-"*60 + "\n"
    )
    log_box.see(tk.END)

    status_label.config(text=f"Slew Speed: {slew_speed:.2f} deg/sec", fg="green")


# ---------------- AZ FULL SPEED TEST ---------------- #

def az_full_speed_test():
    threading.Thread(target=run_az_test, daemon=True).start()


def run_az_test():

    initialize_mount()

    log_box.insert(tk.END, "\n--- AZ Full Speed Test ---\n")
    log_box.see(tk.END)

    send_get(MOUNT_GOTO_URL, {"alt_degs": 45, "az_degs": 0})
    if not wait_until_reached(45, 0):
        return

    start_time = time.perf_counter()

    send_get(MOUNT_GOTO_URL, {"alt_degs": 45, "az_degs": 179})
    if not wait_until_reached(45, 179):
        return

    elapsed = time.perf_counter() - start_time
    az_speed = 179.0 / elapsed if elapsed > 0 else 0

    log_speed_to_file("AZ Full Speed Test", az_speed, elapsed, 179.0)

    log_box.insert(
        tk.END,
        f"AZ Speed: {az_speed:.4f} deg/sec\n"
        + "-"*60 + "\n"
    )
    log_box.see(tk.END)

    status_label.config(text=f"AZ Speed: {az_speed:.2f} deg/sec", fg="green")


# ---------------- ALT FULL SPEED TEST ---------------- #

def alt_full_speed_test():
    threading.Thread(target=run_alt_test, daemon=True).start()


def run_alt_test():

    initialize_mount()

    log_box.insert(tk.END, "\n--- ALT Full Speed Test ---\n")
    log_box.see(tk.END)

    send_get(MOUNT_GOTO_URL, {"alt_degs": 10, "az_degs": 90})
    if not wait_until_reached(10, 90):
        return

    start_time = time.perf_counter()

    send_get(MOUNT_GOTO_URL, {"alt_degs": 80, "az_degs": 90})
    if not wait_until_reached(80, 90):
        return

    elapsed = time.perf_counter() - start_time
    alt_speed = 70.0 / elapsed if elapsed > 0 else 0

    log_speed_to_file("ALT Full Speed Test", alt_speed, elapsed, 70.0)

    log_box.insert(
        tk.END,
        f"ALT Speed: {alt_speed:.4f} deg/sec\n"
        + "-"*60 + "\n"
    )
    log_box.see(tk.END)

    status_label.config(text=f"ALT Speed: {alt_speed:.2f} deg/sec", fg="green")


# ---------------- DIAGONAL FULL SPEED TEST ---------------- #

def diagonal_full_speed_test():
    threading.Thread(target=run_diagonal_test, daemon=True).start()


def run_diagonal_test():

    initialize_mount()

    log_box.insert(tk.END, "\n--- Diagonal Full Speed Test ---\n")
    log_box.see(tk.END)

    send_get(MOUNT_GOTO_URL, {"alt_degs": 20, "az_degs": 10})
    if not wait_until_reached(20, 10):
        return

    start_time = time.perf_counter()

    send_get(MOUNT_GOTO_URL, {"alt_degs": 80, "az_degs": 179})
    if not wait_until_reached(80, 179):
        return

    elapsed = time.perf_counter() - start_time

    delta_az = 169
    delta_alt = 60
    distance = math.sqrt(delta_az**2 + delta_alt**2)

    diagonal_speed = distance / elapsed if elapsed > 0 else 0

    log_speed_to_file("Diagonal Full Speed Test", diagonal_speed, elapsed, distance)

    log_box.insert(
        tk.END,
        f"Diagonal Speed: {diagonal_speed:.4f} deg/sec\n"
        + "-"*60 + "\n"
    )
    log_box.see(tk.END)

    status_label.config(text=f"Diagonal Speed: {diagonal_speed:.2f} deg/sec", fg="green")


# ---------------- GUI ---------------- #

root = tk.Tk()
root.title("Telescope Control - Full Axis Performance Suite")
root.geometry("850x700")

tk.Label(root, text="Target Altitude (deg)").pack()
entry_alt = tk.Entry(root)
entry_alt.pack()

tk.Label(root, text="Target Azimuth (deg)").pack()
entry_az = tk.Entry(root)
entry_az.pack()

tk.Button(root, text="Normal Slew", command=start_slew, width=30).pack(pady=6)
tk.Button(root, text="AZFullSpeed Test", command=az_full_speed_test, width=30, bg="orange").pack(pady=6)
tk.Button(root, text="AltFullSpeed Test", command=alt_full_speed_test, width=30, bg="lightblue").pack(pady=6)
tk.Button(root, text="DiagonalFullSpeed Test", command=diagonal_full_speed_test, width=30, bg="lightgreen").pack(pady=6)

status_label = tk.Label(root, text="Status: Idle", fg="blue", font=("Arial", 13, "bold"))
status_label.pack(pady=8)

live_position_label = tk.Label(root, text="Live Alt: ---   Live Az: ---", font=("Arial", 11))
live_position_label.pack(pady=5)

log_box = scrolledtext.ScrolledText(root, height=25)
log_box.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

root.mainloop()
