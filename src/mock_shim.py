"""
Test Mock Shim for Conflict After DL1 Scenario

This mock simulates:
- DL 0: No propagation, CONTINUE status
- DL 1 (positive literal 1=TRUE): Propagation causes CONFLICT at C4
- DL 1 (negative literal 1=FALSE): Backtrack succeeds, CONTINUE
- DL 2 (positive literal 2=TRUE): Propagation leads to SAT

This demonstrates conflict detection after a decision and backtracking recovery.
"""
import os
import shutil

# Paths relative to project root
DATA_DIR = "data"
TEST_DATA_DIR = os.path.join("tests", "test_data", "conflict_after_dl1")
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
            print(f"[Conflict DL1 Shim] Error reading trigger: {e}")
            target_dl = 0

    # Determine which mock file to use based on DL and literal polarity
    if target_dl == 0:
        source_filename = "dl0.txt"
        print(f"[Conflict DL1 Shim] DL {target_dl} -> CONTINUE (no propagation)")
    elif target_dl == 1:
        if literal > 0:
            source_filename = "dl1_pos.txt"  # This will CONFLICT
            print(f"[Conflict DL1 Shim] DL {target_dl}, Literal {literal} -> CONFLICT after propagation")
        else:
            source_filename = "dl1_neg.txt"  # This will CONTINUE (backtrack succeeded)
            print(f"[Conflict DL1 Shim] DL {target_dl}, Literal {literal} -> CONTINUE (backtrack)")
    elif target_dl == 2:
        source_filename = "dl2_pos.txt"  # This will lead to SAT
        print(f"[Conflict DL1 Shim] DL {target_dl}, Literal {literal} -> SAT (all satisfied)")
    else:
        source_filename = "dl0.txt"  # Fallback

    source_path = os.path.join(TEST_DATA_DIR, source_filename)

    if os.path.exists(source_path):
        print(f"[Conflict DL1 Shim] Copying {source_filename} -> bcp_output.txt")
        shutil.copy(source_path, OUTPUT_FILE)
    else:
        print(f"[Conflict DL1 Shim] Error: {source_filename} not found in {TEST_DATA_DIR}")
        with open(OUTPUT_FILE, "w") as f:
            f.write("--- STATUS ---\nSTATUS: CONFLICT\nDL: 99\nCONFLICT_ID: NONE\n")


if __name__ == "__main__":
    main()
