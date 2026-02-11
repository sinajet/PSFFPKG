# PSFFPKG - PS5 UFS2 Image Creator

**PSFFPKG** is a lightweight utility designed to automate the creation of `.ffpkg` (UFS2) images for the PlayStation 5. It serves as a wrapper for **SvenGDK's UFS2Tool**, streamlining the process of converting game dump directories into installable package files supported by the **ShadowMount** payload.

## 🚀 Features

- **Automated Conversion:** Calculates directory size and executes the necessary arguments to create a UFS2 image.
- **Auto-Naming:** Automatically renames the output image to `.ffpkg` format.
- **Dual Mode:** Supports both **Interactive Mode** (double-click to run) and **Command Line Interface (CLI)** for batch scripting.
- **Admin Privileges:** Automatically requests elevation (Run as Administrator) to ensure file system operations succeed.

---

## ⚠️ Requirements

To use the generated `.ffpkg` files on your console, you need:

1.  **PlayStation 5** running a firmware compatible with the payload.
2.  **ShadowMount Payload (v1.4 or higher):**
    - You must inject the ShadowMount payload that supports UFS mounting.
    - [Download ShadowMount (adel-ailane)](https://github.com/adel-ailane/ShadowMount)
3.  **UFS2Tool:**
    - This tool relies on the `UFS2Tool.exe` to perform the filesystem creation.
    - [Download UFS2Tool (SvenGDK)](https://github.com/SvenGDK/UFS2Tool/releases/)

---

## 📥 Installation & Setup

1.  Download the latest **UFS2Tool** release from the link above and extract the zip file.
2.  Download the **PSFFPKG** executable from our releases:
    - [**Download PSFFPKG.exe**](https://github.com/sinajet/PSFFPKG/releases)
3.  **Crucial Step:** Place `PSFFPKG.exe` and `UFS2Tool.exe` in the **same folder**.

The folder structure should look like this:
```text
📂 UFS2Tool
 ├── 📄 PSFFPKG.exe
 ├── 📄 UFS2Tool.exe
 └── ...
```
---

## 🛠 Usage

### Method 1: Interactive Mode (Easy)
1.  Right-click `PSFFPKG.exe` and select **Run as Administrator** (The tool will try to auto-elevate if you forget).
2.  When prompted, paste the path to your **Game Dump Folder**.
3.  (Optional) Enter an output path or press Enter to save in the current folder.
4.  The tool will build the image and save it as `FolderName.ffpkg`.

### Method 2: Command Line (CLI)
You can use this tool in your own scripts or via CMD/PowerShell.

**Syntax:**
powershell
PSFFPKG.exe "Path\To\GameDump" "Path\To\OutputFolder"

**Example:**
powershell
PSFFPKG.exe "C:\Games\CUSA12345" "D:\PS5_Packages"
*Note: If the output path is omitted, the file will be saved in the current directory.*

---

## ⚙️ How It Works

This tool calculates the total size of your input directory, adds a safety buffer (slack space), and constructs the UFS2 image.

The logic used to create the filesystem (block sizes and format) is based on the methodology documented by **earthonion** in the [mkufs2 repository](https://github.com/earthonion/mkufs2) for creating valid UFS images on FreeBSD.

The tool executes the following command via `UFS2Tool`:
bash
UFS2Tool.exe newfs -O 2 -b 32768 -f 4096 -D "Input_Dir" "Temp_Image.img"

Once the process is complete, it renames the output to `.ffpkg` so it is ready for use with ShadowMount.

---

## 🏆 Credits & Acknowledgments

This tool is a wrapper and would not be possible without the hard work of the scene developers:

*   **[voidwhisper-ps](https://github.com/voidwhisper-ps):** Huge thanks for creating the **ShadowMount** payload and enabling UFS support on the PS5.
*   **[SvenGDK](https://github.com/SvenGDK):** Special thanks for developing **UFS2Tool** for Windows, which handles the core filesystem creation.
*   **[earthonion](https://github.com/earthonion/mkufs2):** For the research and documentation on creating UFS2 images for FreeBSD/PS5.

---

## 📝 Disclaimer

This software is provided "as is", without warranty of any kind. Use it at your own risk. The author is not responsible for any damage to your console or data.
