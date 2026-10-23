# All Layers to Image Size (GIMP Plugin)
A powerful, lightweight Python-Fu plugin for GIMP that resizes all layers in your active project to match the image canvas boundaries simultaneously. Instead of clicking layers one by one, this tool processes your entire stack instantly and provides smart options for how the newly expanded margins should be filled.

## Features
When you run the plugin, an interactive menu will pop up offering three ways to fill the newly created space:
* **Auto-Detect Edge Color:** Intelligently scans the entire outer border of each layer, calculates the most dominant color, and uses it to seamlessly flood the new margins.
* **Force Transparency:** Automatically adds an Alpha Channel to layers that lack one, ensuring all expanded space transitions into pure transparency.
* **Custom Color or Pattern:** Allows you to pick a uniform solid color (using GIMP's color wheel) or an active pattern texture to fill the expanded spaces.

### Behind-the-Scenes Optimization
* **One-Step Undo:** The entire multi-layer operation is grouped together. Pressing `Ctrl + Z` undoes the changes for all layers instantly.
* **Group Safety:** Automatically skips Layer Groups to prevent structural rendering issues while processing individual content layers normally.

## Installation
1. Copy the `all_layers_to_image_size.py` file.
2. Place the file into your version's local GIMP **plug-ins** directory:

### For GIMP 3.x Users (Crucial Folder Step)
GIMP 3 requires every plugin file to live inside its own subfolder named **exactly** the same as the file. 
* Create a new folder named `all_layers_to_image_size` inside your plug-ins directory.
* Place your script inside it.

* **Windows:** `%APPDATA%\GIMP\3.0\plug-ins\all_layers_to_image_size\`
* **macOS:** `~/Library/Application Support/GIMP/3.0/plug-ins/all_layers_to_image_size/`
* **Linux:** `~/.config/GIMP/3.0/plug-ins/all_layers_to_image_size/`

### For GIMP 2.10 Users (latest v2.x version)
* **Windows:** `%APPDATA%\GIMP\2.10\plug-ins\`
* **macOS:** `~/Library/Application Support/GIMP/2.10/plug-ins/`
* **Linux:** `~/.config/GIMP/2.10/plug-ins/`

### For Older GIMP 2.8 Users
* **Windows:** `%USERPROFILE%\.gimp-2.8\plug-ins\`

3. *Linux/macOS only:* Open your terminal and mark the script as executable:
   ```bash
   chmod +x all_layers_to_image_size.py
   ```
4. Restart GIMP.

## How to Use
1. Open your project in GIMP.
2. Go to the top menu bar and select **Layer** ➔ **All Layers to Image Size...**
3. Choose your desired filling mode, pick your colors/patterns if applicable, and click **OK**.

### Recommended: Set a Keyboard Shortcut
To tie this action to a hotkey, go to **Edit** ➔ **Keyboard Shortcuts**, search for `"All Layers to Image Size"`, and assign your preferred key combination.

## License
This project is completely released into the **Public Domain** under **The Unlicense** / **CC0**. This tool was conceptualized by a human and authored with the assistance of AI. You are completely free to copy, modify, publish, use, compile, sell, or distribute this software in any form, for any purpose, commercial or non-commercial.
