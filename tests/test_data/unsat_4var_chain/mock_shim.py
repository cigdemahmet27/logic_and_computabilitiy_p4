"""
Test Mock Shim for 4-Variable UNSAT Chain Scenario

This mock simulates:
- DL 0: Unit propagation chain leads to CONFLICT
  - C1: -4 (unit) -> 4=FALSE
  - C2: (4 OR 1) -> 1=TRUE  
  - C3: (-1 OR 2) -> 2=TRUE
  - C4: (-2 OR 3) -> 3=TRUE
  - C5: (-3) -> CONFLICT! (3 is TRUE but C5 needs -3)

This demonstrates how BCP can detect UNSAT through propagation.
"""
import os
import shutil

# Paths relative to project root
DATA_DIR = "data"
TEST_DATA_DIR = os.path.join("tests", "test_data", "unsat_4var_chain")
TRIGGER_FILE = os.path.join(DATA_DIR, "bcp_trigger_input.txt")
OUTPUT_FILE = os.path.join(DATA_DIR, "bcp_output.txt")


def main():
    target_dl = 0

    # Read the trigger file
    if os.path.exists(TRIGGER_FILE):
        try:
            with open(TRIGGER_FILE, "r") as f:
                content = f.read()
                for line in content.splitlines():
                    if line.startswith("DL:"):
                        target_dl = int(line.split(":")[1].strip())
        except Exception as e:
            print(f"[UNSAT Chain Shim] Error reading trigger: {e}")
            target_dl = 0
    
    # Always return CONFLICT at DL 0 (UNSAT detected immediately)
    source_filename = "dl0.txt"
    source_path = os.path.join(TEST_DATA_DIR, source_filename)

    if os.path.exists(source_path):
        print(f"[UNSAT Chain Shim] DL {target_dl}: Copying {source_filename} -> bcp_output.txt (CONFLICT via chain)")
        shutil.copy(source_path, OUTPUT_FILE)
    else:
        print(f"[UNSAT Chain Shim] Error: {source_filename} not found in {TEST_DATA_DIR}")
        with open(OUTPUT_FILE, "w") as f:
            f.write("--- STATUS ---\nSTATUS: CONFLICT\nDL: 0\nCONFLICT_ID: NONE\n")


if __name__ == "__main__":
    main()
