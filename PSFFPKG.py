#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import argparse
import tempfile
import shutil
import ctypes
import time
from pathlib import Path

# Name of the tool executable (searched next to the script or in PATH)
TOOL_EXE = "UFS2Tool.exe"

def is_admin():
    """Check if the script is running with administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def elevate_if_needed():
    """If not admin, restart the script with admin rights and exit."""
    if is_admin():
        return True

    print("[INFO] Administrator privileges required. Requesting elevation...")

    # Build command line: python.exe script.py [arguments]
    script = sys.argv[0]
    params = ' '.join(sys.argv[1:]) if len(sys.argv) > 1 else ''

    # Use ShellExecuteW with 'runas' verb to request elevation
    ret = ctypes.windll.shell32.ShellExecuteW(
        None,               # hwnd
        "runas",            # operation
        sys.executable,     # file (python interpreter)
        f'"{script}" {params}',  # parameters
        None,               # directory
        1                   # SW_SHOWNORMAL
    )

    # ShellExecute returns a value > 32 if successful
    if ret <= 32:
        print("[ERROR] Failed to elevate. Please run the script as Administrator manually.")
        sys.exit(1)
    else:
        # Elevation requested, exit this instance
        sys.exit(0)

def locate_tool():
    """Find UFS2Tool.exe next to the script or in the PATH environment variable"""
    script_dir = Path(__file__).parent
    tool_path = script_dir / TOOL_EXE
    if tool_path.is_file():
        return str(tool_path)
    which_tool = shutil.which(TOOL_EXE)
    if which_tool:
        return which_tool
    raise FileNotFoundError(
        f"{TOOL_EXE} not found. Please place it next to the script or in your PATH."
    )

def calculate_directory_size_bytes(path):
    """Calculate the actual size of a directory in bytes (sum of all file sizes)"""
    total = 0
    for entry in Path(path).rglob("*"):
        if entry.is_file():
            total += entry.stat().st_size
    return total

def run_newfs_with_D(tool_path, input_dir, output_image):
    """
    Run command:
    UFS2Tool.exe newfs -O 2 -b 32768 -f 4096 -D <input_dir> <output_image>
    Shows live output from UFS2Tool.exe.
    """
    cmd = [
        tool_path,
        "newfs",
        "-O", "2",
        "-b", "32768",
        "-f", "4096",
        "-D", input_dir,
        output_image
    ]
    print(f"[INFO] Executing command: {' '.join(cmd)}")
    print("[INFO] Creating UFS2 image... (this may take a while)")
    print("-" * 50)

    try:
        # Run the command without capturing output – UFS2Tool writes directly to console
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError:
        print("[ERROR] UFS2Tool execution failed.")
        sys.exit(1)

    print("-" * 50)
    print("[INFO] Image creation completed successfully.")
    return output_image

def interactive_input():
    """Get input from user in interactive mode (no command-line arguments)"""
    print("=== Create UFS2 image and convert to ffpkg ===")
    while True:
        in_dir = input("Enter the game dump folder path: ").replace('"','').replace("'",'').strip()
        if not in_dir:
            print("❌ Path cannot be empty.")
            continue
        if not os.path.isdir(in_dir):
            print("❌ Directory is not valid.")
            continue
        break
    out_dir = input("Enter output folder path (default: current directory): ").replace('"','').replace("'",'').strip()
    if not out_dir:
        out_dir = os.getcwd()
    return in_dir, out_dir

def main():
    # --- Elevation check ---
    elevate_if_needed()

    # Detect execution mode: use argparse if arguments are provided
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(
            description="Create UFS2 image from directory using UFS2Tool and convert to ffpkg"
        )
        parser.add_argument("input_dir", help="Path to the game dump folder")
        parser.add_argument(
            "output_dir", nargs="?", default=os.getcwd(),
            help="Path to output folder (default: current directory)"
        )
        args = parser.parse_args()
        input_dir = args.input_dir
        output_dir = args.output_dir
    else:
        input_dir, output_dir = interactive_input()

    # Validate input directory
    if not os.path.isdir(input_dir):
        print(f"❌ Error: Input directory '{input_dir}' does not exist.")
        sys.exit(1)

    # Create output directory if needed
    os.makedirs(output_dir, exist_ok=True)

    # Output file name based on input folder name
    folder_name = os.path.basename(os.path.normpath(input_dir))
    if not folder_name:
        folder_name = "output"
    final_filename = f"{folder_name}.ffpkg"
    final_path = os.path.join(output_dir, final_filename)

    # Calculate and display directory size and estimated image size
    bytes_size = calculate_directory_size_bytes(input_dir)
    slack = 10 * 1024 * 1024  # 10 MB
    total_bytes = bytes_size + slack
    estimated_mb = (total_bytes + (1024*1024 - 1)) // (1024*1024)
    print(f"[INFO] Actual file size: {bytes_size:,} bytes")
    print(f"[INFO] Estimated image size (with 10 MB slack): about {estimated_mb} MB")
    print(f"[INFO] Final file: {final_path}")

    # Locate the tool
    try:
        tool_path = locate_tool()
    except FileNotFoundError as e:
        print(f"❌ {e}")
        sys.exit(1)

    # Create a temporary file in the output directory
    temp_file = tempfile.NamedTemporaryFile(
        dir=output_dir, prefix=f"{folder_name}_", suffix=".tmp", delete=False
    )
    temp_path = temp_file.name
    temp_file.close()

    try:
        run_newfs_with_D(tool_path, input_dir, temp_path)

        if os.path.exists(final_path):
            os.remove(final_path)
        os.rename(temp_path, final_path)
        print(f"✅ UFS2 image successfully created and renamed to ffpkg:\n   {final_path}")

    except Exception as e:
        print(f"❌ Error during image creation: {e}")
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        sys.exit(1)

    # Keep window open for 5 seconds before exiting
    print("\n[INFO] Window will close automatically in 5 seconds...")
    time.sleep(5)

if __name__ == "__main__":
    main()