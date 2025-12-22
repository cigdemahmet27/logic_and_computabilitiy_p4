"""
Test Mock Shim for SAT Simple Scenario

This mock simulates:
- DL 0: All variables unassigned
- DL 1: Deciding literal 2 leads to SAT (unit propagation assigns 3)
"""
import os
import shutil

# Paths relative to project root
DATA_DIR = "data"
TEST_DATA_DIR = os.path.join("tests", "test_data", "sat_simple")
TRIGGER_FILE = os.path.join(DATA_DIR, "bcp_trigger_input.txt")
OUTPUT_FILE = os.path.join(DATA_DIR, "bcp_output.txt")


def main():
    target_dl = 0

    # Read the trigger file to determine which DL is being requested
    if os.path.exists(TRIGGER_FILE):
        try:
            with open(TRIGGER_FILE, "r") as f:
                content = f.read()
                for line in content.splitlines():
                    if line.startswith("DL:"):
                        target_dl = int(line.split(":")[1].strip())
        except Exception as e:
            print(f"[SAT Shim] Error reading trigger: {e}")
            target_dl = 0
    
    # Map DL to the corresponding mock output file
    source_filename = f"dl{target_dl}.txt"
    source_path = os.path.join(TEST_DATA_DIR, source_filename)

    if os.path.exists(source_path):
        print(f"[SAT Shim] DL {target_dl}: Copying {source_filename} -> bcp_output.txt")
        shutil.copy(source_path, OUTPUT_FILE)
    else:
        print(f"[SAT Shim] Error: {source_filename} not found in {TEST_DATA_DIR}")
        # Create a generic CONFLICT to prevent infinite loops
        with open(OUTPUT_FILE, "w") as f:
            f.write("--- STATUS ---\nSTATUS: CONFLICT\nDL: 99\nCONFLICT_ID: NONE\n")


if __name__ == "__main__":
    main()
