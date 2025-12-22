"""
Test Mock Shim for SAT with Backtracking Scenario

This mock simulates:
- DL 0: Unit propagation assigns 2=TRUE
- DL 1 (positive literal): Decision 1=TRUE leads to CONFLICT
- DL 1 (negative literal): Backtrack, decision 1=FALSE leads to SAT

This demonstrates the DPLL backtracking mechanism.
"""
import os
import shutil

# Paths relative to project root
DATA_DIR = "data"
TEST_DATA_DIR = os.path.join("tests", "test_data", "sat_with_backtrack")
TRIGGER_FILE = os.path.join(DATA_DIR, "bcp_trigger_input.txt")
OUTPUT_FILE = os.path.join(DATA_DIR, "bcp_output.txt")


def main():
    target_dl = 0
    literal = 0

    # Read the trigger file to determine DL and literal
    if os.path.exists(TRIGGER_FILE):
        try:
            with open(TRIGGER_FILE, "r") as f:
                content = f.read()
                for line in content.splitlines():
                    if line.startswith("DL:"):
                        target_dl = int(line.split(":")[1].strip())
                    elif line.startswith("TRIGGER_LITERAL:"):
                        literal = int(line.split(":")[1].strip())
        except Exception as e:
            print(f"[Backtrack Shim] Error reading trigger: {e}")
            target_dl = 0

    # Determine which mock file to use based on DL and literal polarity
    if target_dl == 0:
        source_filename = "dl0.txt"
    elif target_dl == 1:
        if literal > 0:
            source_filename = "dl1_pos.txt"  # This will CONFLICT
            print(f"[Backtrack Shim] DL {target_dl}, Literal {literal} -> CONFLICT")
        else:
            source_filename = "dl1_neg.txt"  # This will SAT (after backtrack)
            print(f"[Backtrack Shim] DL {target_dl}, Literal {literal} -> SAT (backtrack succeeded)")
    else:
        source_filename = "dl0.txt"  # Fallback

    source_path = os.path.join(TEST_DATA_DIR, source_filename)

    if os.path.exists(source_path):
        print(f"[Backtrack Shim] Copying {source_filename} -> bcp_output.txt")
        shutil.copy(source_path, OUTPUT_FILE)
    else:
        print(f"[Backtrack Shim] Error: {source_filename} not found in {TEST_DATA_DIR}")
        with open(OUTPUT_FILE, "w") as f:
            f.write("--- STATUS ---\nSTATUS: CONFLICT\nDL: 99\nCONFLICT_ID: NONE\n")


if __name__ == "__main__":
    main()
