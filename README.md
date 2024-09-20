# ⚠️ WARNING: USE AT YOUR OWN RISK ⚠️

**THIS TOOL IS EXTREMELY DANGEROUS AND CAN PERMANENTLY DAMAGE YOUR PHONE IF USED IMPROPERLY.**  

- Flashing firmware incorrectly can **BRICK** your phone, making it unusable.
- Rooting your phone can **VOID YOUR WARRANTY** and expose your device to security vulnerabilities.
- Make sure you have **BACKED UP ALL IMPORTANT DATA** before proceeding, as this process may result in **DATA LOSS**.
- This tool is provided **AS IS**, without any warranties or guarantees. The authors are **NOT RESPONSIBLE** for any damage to your device or data loss.

**PROCEED WITH CAUTION!**  

If you're unsure about what you're doing, **DO NOT USE THIS TOOL**.



# Auto Root and Firmware Tool

This tool allows users to:
1. Automatically detect a connected phone's model and firmware using ADB.
2. Fetch compatible firmware from [SamFW](https://samfw.com/firmware).
3. Flash selected firmware directly onto the phone.

## Requirements
- **Python 3.x**
- **ADB** and **Fastboot** tools (for phone detection and flashing).
- Python libraries:
  - `requests`
  - `beautifulsoup4`
  - `tkinter` (built-in with Python)

## Installation

1. Clone the repository:
   git clone https://github.com/Lucky7897/autoroot.git

2. Install the required Python packages:
   pip install requests beautifulsoup4

3. Make sure you have **ADB** and **Fastboot** installed:
   sudo apt install android-tools-adb android-tools-fastboot

## How to Use

1. Connect your phone with **USB Debugging** enabled.
2. Run the script:
   python auto_root_tool.py

3. Detect the phone, fetch firmware, and flash the selected firmware.

## License

This project is licensed under the MIT License.
