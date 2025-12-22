"""
Test Mock Shim for UNSAT Conflict Scenario

This mock simulates:
- DL 0: Unit propagation leads to immediate CONFLICT (UNSAT)
"""
import os
import shutil

# Paths relative to project root
DATA_DIR = "data"
TEST_DATA_DIR = os.path.join("tests", "test_data", "unsat_conflict")
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
            print(f"[UNSAT Shim] Error reading trigger: {e}")
            target_dl = 0
    
    # Always return DL 0 conflict for this test (UNSAT is detected at DL 0)
    source_filename = "dl0.txt"
    source_path = os.path.join(TEST_DATA_DIR, source_filename)

    if os.path.exists(source_path):
        print(f"[UNSAT Shim] DL {target_dl}: Copying {source_filename} -> bcp_output.txt (CONFLICT)")
        shutil.copy(source_path, OUTPUT_FILE)
    else:
        print(f"[UNSAT Shim] Error: {source_filename} not found in {TEST_DATA_DIR}")
        with open(OUTPUT_FILE, "w") as f:
            f.write("--- STATUS ---\nSTATUS: CONFLICT\nDL: 0\nCONFLICT_ID: NONE\n")


if __name__ == "__main__":
    main()
