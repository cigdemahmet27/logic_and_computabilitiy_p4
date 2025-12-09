import os
import shutil
import sys

# Define paths relative to the project root (where main.py runs)
DATA_DIR = "data"
TRIGGER_FILE = os.path.join(DATA_DIR, "bcp_trigger_input.txt")
OUTPUT_FILE = os.path.join(DATA_DIR, "bcp_output.txt")

def main():
    target_dl = 0

    # 1. Check if a trigger file exists to see what DL is requested
    if os.path.exists(TRIGGER_FILE):
        try:
            with open(TRIGGER_FILE, "r") as f:
                content = f.read()
                # Parse lines to find "DL: X"
                for line in content.splitlines():
                    if line.startswith("DL:"):
                        target_dl = int(line.split(":")[1].strip())
        except Exception as e:
            print(f"Shim Error reading trigger: {e}")
            target_dl = 0
    else:
        # If no trigger exists, we assume it's the start (DL 0)
        target_dl = 0

    # 2. Construct the filename of the pre-made data (e.g., dl1_4.txt)
    source_filename = f"dl{target_dl}_4.txt"
    source_path = os.path.join(DATA_DIR, source_filename)

    # 3. Copy the pre-made file to the official output file
    if os.path.exists(source_path):
        print(f"[Mock Shim] Copying {source_filename} -> bcp_output.txt")
        shutil.copy(source_path, OUTPUT_FILE)
    else:
        # If the solver asks for a DL we don't have a file for (e.g. DL 3)
        print(f"[Mock Shim] Error: {source_filename} not found in data folder.")
        # Create a generic dummy file to prevent crashing
        with open(OUTPUT_FILE, "w") as f:
            f.write("STATUS: CONFLICT\nDL: 99\nCONFLICT_ID: NONE")

if __name__ == "__main__":
    main()