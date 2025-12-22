"""
Test Mock Shim for 6-Variable Deep SAT Scenario (4+ Decision Levels)

This mock simulates:
- DL 0: All 6 variables unassigned
- DL 1: Decide 1=TRUE, propagates 3=TRUE
- DL 2: Decide 5=TRUE, propagates 6=FALSE
- DL 3: Decide 4=FALSE, satisfies C5
- DL 4: Decide 2=FALSE, all clauses SAT!

Formula:
C1: (1 OR 2)
C2: (-1 OR 3)
C3: (-2 OR 4)
C4: (-3 OR 5)
C5: (-4 OR 6)
C6: (-5 OR -6)
"""
import os
import shutil

# Paths relative to project root
DATA_DIR = "data"
TEST_DATA_DIR = os.path.join("tests", "test_data", "sat_6var_deep")
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
            print(f"[6VAR Deep Shim] Error reading trigger: {e}")
            target_dl = 0
    
    # Map DL to the corresponding mock output file
    source_filename = f"dl{target_dl}.txt"
    source_path = os.path.join(TEST_DATA_DIR, source_filename)

    if os.path.exists(source_path):
        print(f"[6VAR Deep Shim] DL {target_dl}: Copying {source_filename} -> bcp_output.txt")
        shutil.copy(source_path, OUTPUT_FILE)
    else:
        print(f"[6VAR Deep Shim] Error: {source_filename} not found in {TEST_DATA_DIR}")
        # Create a generic CONFLICT to prevent infinite loops
        with open(OUTPUT_FILE, "w") as f:
            f.write("--- STATUS ---\nSTATUS: CONFLICT\nDL: 99\nCONFLICT_ID: NONE\n")


if __name__ == "__main__":
    main()
