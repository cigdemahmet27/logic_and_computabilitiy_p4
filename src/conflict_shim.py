"""
Mock Shim for Conflict Test Scenario

This simulates a scenario where:
- DL 0: Initial state, 2 variables unassigned
- DL 1 with literal=1 (positive): CONFLICT occurs
- Backtrack, DL 1 with literal=-1 (negative): SAT

The CNF formula simulated is:
  C1: (1 OR 2)     - At least one must be true
  C2: (1 OR -2)    - If 1 is true, 2 can't also be true
  C3: (-1 OR -2)   - If 2 is true, 1 can't be true

This is UNSAT with both variables TRUE, but SAT with both FALSE or mixed.
"""
import os
import shutil
import sys

# Define paths relative to the project root (where main.py runs)
DATA_DIR = "data"
TEST_DIR = os.path.join(DATA_DIR, "conflict_test")
TRIGGER_FILE = os.path.join(DATA_DIR, "bcp_trigger_input.txt")
OUTPUT_FILE = os.path.join(DATA_DIR, "bcp_output.txt")

def main():
    target_dl = 0
    literal = 0

    # 1. Check if a trigger file exists to see what DL and literal are requested
    if os.path.exists(TRIGGER_FILE):
        try:
            with open(TRIGGER_FILE, "r") as f:
                content = f.read()
                # Parse lines to find "DL: X" and "TRIGGER_LITERAL: Y"
                for line in content.splitlines():
                    if line.startswith("DL:"):
                        target_dl = int(line.split(":")[1].strip())
                    elif line.startswith("TRIGGER_LITERAL:"):
                        literal = int(line.split(":")[1].strip())
        except Exception as e:
            print(f"[Conflict Shim] Error reading trigger: {e}")
            target_dl = 0
    else:
        target_dl = 0

    # 2. Determine which file to copy based on DL and literal
    if target_dl == 0:
        source_filename = "dl0.txt"
    elif target_dl == 1:
        # Check if literal is positive or negative
        if literal > 0:
            source_filename = "dl1_pos.txt"  # This will CONFLICT
            print(f"[Conflict Shim] DL {target_dl}, Literal {literal} -> CONFLICT")
        else:
            source_filename = "dl1_neg.txt"  # This will SAT after backtrack
            print(f"[Conflict Shim] DL {target_dl}, Literal {literal} -> SAT (after backtrack)")
    else:
        # Fallback for other DLs
        source_filename = "dl0.txt"

    source_path = os.path.join(TEST_DIR, source_filename)

    # 3. Copy the pre-made file to the official output file
    if os.path.exists(source_path):
        print(f"[Conflict Shim] Copying {source_filename} -> bcp_output.txt")
        shutil.copy(source_path, OUTPUT_FILE)
    else:
        print(f"[Conflict Shim] Error: {source_filename} not found in {TEST_DIR}")
        # Create a generic dummy file to prevent crashing
        with open(OUTPUT_FILE, "w") as f:
            f.write("STATUS: CONFLICT\nDL: 99\nCONFLICT_ID: NONE")

if __name__ == "__main__":
    main()
