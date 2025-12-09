"""
Goal: Store all file paths, constants, and settings in one place.


Why: The project document specifies very exact file names (e.g., "BCP TRIGGER INPUT"). If you hardcode these strings inside your loops and make a typo in one place, debugging will be a nightmare. Using a config file prevents this.


"""

import os

# --- DIRECTORIES ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# --- INPUTS (Files we READ) ---
# The mock engine writes to this file, we read it.
BCP_OUTPUT_FILE = os.path.join(DATA_DIR, "bcp_output.txt")
# The initial formula from Project #2
INPUT_CNF_FILE = os.path.join(DATA_DIR, "input.cnf")

# --- OUTPUTS (Files we WRITE) ---
# We write our decision here for the mock engine to read.
TRIGGER_INPUT_FILE = os.path.join(DATA_DIR, "bcp_trigger_input.txt")
# We append our logs here for Project #5.
MASTER_TRACE_FILE = os.path.join(DATA_DIR, "master_trace.txt")

# --- EXECUTABLE ---
# Path to the Mock Inference Engine (Project #3)
# Windows users might need ".exe", Mac/Linux might not.
# config.py
INFERENCE_ENGINE_EXE = "mock_runner.bat"

# --- CONSTANTS ---
STATUS_SAT = "SAT"
STATUS_UNSAT = "UNSAT"      # Some engines might return CONFLICT
STATUS_CONFLICT = "CONFLICT"
STATUS_CONTINUE = "CONTINUE"