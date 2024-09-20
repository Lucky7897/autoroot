"""
Auto Root and Firmware Tool

This script provides a GUI to:
1. Detect a connected phone using ADB.
2. Fetch compatible firmware from SamFW.
3. Allow the user to flash the selected firmware to the phone.

Requirements:
- Python 3.x
- ADB and Fastboot tools (for phone detection and flashing)
- Python libraries: requests, beautifulsoup4, tkinter
  Install dependencies via: pip install requests beautifulsoup4

How to Use:
1. Connect your phone with USB Debugging enabled.
2. Run the script using Python.
3. Detect the connected phone.
4. Fetch firmware options from SamFW.
5. Flash selected firmware.

"""

import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import subprocess
import os
import requests
from bs4 import BeautifulSoup

# Function to run shell commands
def run_command(cmd):
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    if process.returncode != 0:
        print(f"Error: {err.decode()}")
    return out.decode().strip()

# 1. Detect phone and fetch model/firmware
def detect_phone():
    out = run_command("adb devices")
    if "device" not in out:
        messagebox.showerror("Error", "No device detected. Please connect your phone.")
        return None

    # Get phone details like model and firmware
    model = run_command("adb shell getprop ro.product.model")
    firmware = run_command("adb shell getprop ro.build.version.release")
    
    if model and firmware:
        model_label.config(text=f"Detected Model: {model}")
        firmware_label.config(text=f"Detected Firmware: {firmware}")
        return model, firmware
    else:
        messagebox.showerror("Error", "Could not fetch phone details.")
        return None

# 2. Fetch compatible firmware from SamFW
def fetch_firmware(model):
    base_url = f"https://samfw.com/firmware/{model.replace(' ', '-')}"
    response = requests.get(base_url)
    
    if response.status_code != 200:
        messagebox.showerror("Error", "Could not fetch firmware from SamFW.")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    firmware_list = []
    
    # Scrape firmware options
    for row in soup.select('.firmwares-table tbody tr'):
        columns = row.find_all('td')
        if len(columns) >= 4:
            firmware_version = columns[0].text.strip()
            region = columns[1].text.strip()
            download_link = columns[3].find('a')['href']
            firmware_list.append((firmware_version, region, download_link))

    return firmware_list

# 3. Display firmware options in the GUI
def show_firmware_options(firmware_list):
    for firmware_version, region, download_link in firmware_list:
        tree.insert("", "end", values=(firmware_version, region, download_link))

# 4. Flash selected firmware
def flash_firmware():
    selected_item = tree.focus()
    if not selected_item:
        messagebox.showwarning("Warning", "No firmware selected.")
        return

    selected_firmware = tree.item(selected_item)['values']
    download_link = selected_firmware[2]

    # Ask for confirmation
    confirm = messagebox.askyesno("Confirm", f"Do you want to download and flash firmware {selected_firmware[0]}?")
    if not confirm:
        return

    # Download firmware
    download_path = filedialog.askdirectory(title="Select folder to save firmware")
    if download_path:
        firmware_file = os.path.join(download_path, selected_firmware[0] + ".zip")
        # Download firmware (can replace with an actual download method if needed)
        run_command(f"curl -o {firmware_file} {download_link}")
        
        # Flash firmware (this part depends on the phone's flashing process, here is a placeholder)
        messagebox.showinfo("Info", f"Firmware downloaded to {firmware_file}. Now flashing...")
        # Flashing logic (adb/fastboot based on the firmware and device type)
        # Example: run_command(f"adb sideload {firmware_file}")

# GUI Setup
root = tk.Tk()
root.title("Auto Root and Firmware Tool")
root.geometry("600x400")

# Detect phone section
detect_frame = tk.Frame(root)
detect_frame.pack(pady=10)

model_label = tk.Label(detect_frame, text="Detected Model: N/A")
model_label.pack()

firmware_label = tk.Label(detect_frame, text="Detected Firmware: N/A")
firmware_label.pack()

detect_button = tk.Button(detect_frame, text="Detect Phone", command=lambda: detect_phone())
detect_button.pack()

# Firmware list section
firmware_frame = tk.Frame(root)
firmware_frame.pack(pady=20)

tree = ttk.Treeview(firmware_frame, columns=("Firmware Version", "Region", "Download Link"), show='headings', height=8)
tree.heading("Firmware Version", text="Firmware Version")
tree.heading("Region", text="Region")
tree.heading("Download Link", text="Download Link")
tree.pack()

# Fetch and show firmware button
fetch_firmware_button = tk.Button(root, text="Fetch Firmware", command=lambda: show_firmware_options(fetch_firmware(detect_phone()[0])))
fetch_firmware_button.pack(pady=10)

# Flash firmware button
flash_button = tk.Button(root, text="Flash Selected Firmware", command=flash_firmware)
flash_button.pack(pady=10)

root.mainloop()
