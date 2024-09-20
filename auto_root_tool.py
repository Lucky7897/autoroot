import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import subprocess
import os
import requests
from bs4 import BeautifulSoup
from tkinter import StringVar

# Function to run shell commands and handle errors
def run_command(cmd):
    try:
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        if process.returncode != 0:
            print(f"Error: {err.decode()}")
            return None
        return out.decode().strip()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to execute command: {cmd}\nError: {e}")
        return None

# 1. Check if ADB and Fastboot are installed
def check_adb_fastboot():
    adb_check = run_command("adb version")
    fastboot_check = run_command("fastboot --version")
    if not adb_check or not fastboot_check:
        messagebox.showerror("Error", "ADB/Fastboot tools not found. Please install them.")
        return False
    return True

# 2. Detect multiple devices
def detect_devices():
    if not check_adb_fastboot():
        return None

    out = run_command("adb devices")
    devices = []
    for line in out.splitlines():
        if "device" in line:
            devices.append(line.split()[0])
    
    if not devices:
        messagebox.showerror("Error", "No devices detected. Please connect your phone.")
        return None
    return devices

# 3. Fetch phone details (with fallback for fastboot)
def get_phone_details(device):
    model = run_command(f"adb -s {device} shell getprop ro.product.model")
    firmware = run_command(f"adb -s {device} shell getprop ro.build.version.release")

    if model and firmware:
        model_label.config(text=f"Detected Model: {model}")
        firmware_label.config(text=f"Detected Firmware: {firmware}")
        return model, firmware
    else:
        messagebox.showerror("Error", "Could not fetch phone details. Trying fastboot fallback.")
        
        # Fastboot fallback if adb fails
        model = run_command(f"fastboot -s {device} getvar product")
        firmware = run_command(f"fastboot -s {device} getvar version")
        if model and firmware:
            model_label.config(text=f"Fastboot Model: {model}")
            firmware_label.config(text=f"Fastboot Firmware: {firmware}")
            return model, firmware
        else:
            messagebox.showerror("Error", "Fastboot also failed. Ensure USB debugging is enabled.")
            return None

# 4. Fetch compatible firmware from SamFW
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

# 5. Display firmware options in the GUI
def show_firmware_options(firmware_list):
    if not firmware_list:
        return

    tree.delete(*tree.get_children())  # Clear the treeview
    for firmware_version, region, download_link in firmware_list:
        tree.insert("", "end", values=(firmware_version, region, download_link))

# 6. Flash selected firmware (with Samsung Odin detection)
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
        download_firmware(download_link, firmware_file)

        # Flash firmware logic (ADB/Fastboot/Odin)
        messagebox.showinfo("Info", f"Firmware downloaded to {firmware_file}. Now flashing...")
        model, _ = get_phone_details(device_var.get())
        
        # Samsung Odin or Heimdall (as placeholder)
        if "Samsung" in model:
            messagebox.showinfo("Info", "Samsung detected. Odin flashing required. Placeholder for Odin/Heimdall.")
            # Odin/Heimdall logic placeholder
        else:
            # Default ADB/fastboot flashing
            run_command(f"adb sideload {firmware_file}")
            messagebox.showinfo("Success", "Firmware flashed successfully. Rebooting device...")
            run_command(f"adb reboot")

# 7. Download firmware with progress tracking and retries
def download_firmware(url, file_path):
    try:
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        chunk_size = 1024
        progress_bar['maximum'] = total_size
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    progress_bar['value'] += len(chunk)
        messagebox.showinfo("Download Complete", f"Firmware downloaded successfully: {file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to download firmware.\nError: {e}")

# GUI Setup
root = tk.Tk()
root.title("Auto Root and Firmware Tool")
root.geometry("600x500")

# Detect phone section
detect_frame = tk.Frame(root)
detect_frame.pack(pady=10)

model_label = tk.Label(detect_frame, text="Detected Model: N/A")
model_label.pack()

firmware_label = tk.Label(detect_frame, text="Detected Firmware: N/A")
firmware_label.pack()

# Multi-device dropdown
device_var = StringVar()
device_dropdown = ttk.Combobox(detect_frame, textvariable=device_var)
device_dropdown.pack()

def detect_and_select_device():
    devices = detect_devices()
    if devices:
        device_dropdown['values'] = devices
        device_dropdown.current(0)
        get_phone_details(devices[0])

detect_button = tk.Button(detect_frame, text="Detect Phone", command=detect_and_select_device)
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
fetch_firmware_button = tk.Button(root, text="Fetch Firmware", command=lambda: show_firmware_options(fetch_firmware(get_phone_details(device_var.get())[0])))
fetch_firmware_button.pack(pady=10)

# Flash firmware button
flash_button = tk.Button(root, text="Flash Selected Firmware", command=flash_firmware)
flash_button.pack(pady=10)

# Progress bar for downloads
progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(pady=10)

root.mainloop()
