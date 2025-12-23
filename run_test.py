"""
Run a specific test and display the generated master trace.

Usage:
    python run_test.py                  # Run with default test (sat_4var)
    python run_test.py sat_simple       # Run specific test
    python run_test.py sat_with_backtrack
    python run_test.py sat_4var
    python run_test.py sat_6var_deep    # 4+ decision levels test
"""
import sys
import os
sys.path.insert(0, '.')
import config
import shutil

# Get test name from command line or use default
if len(sys.argv) > 1:
    test_name = sys.argv[1]
else:
    test_name = "sat_4var"

# Available tests
available_tests = ["sat_simple", "sat_with_backtrack", "sat_4var", "sat_6var_deep", "conflict_after_dl1", "unsat_after_dl2"]

if test_name not in available_tests:
    print(f"Unknown test: {test_name}")
    print(f"Available tests: {available_tests}")
    sys.exit(1)

# Setup the test
test_data_path = f'tests/test_data/{test_name}'
if not os.path.exists(test_data_path):
    print(f"Test data not found: {test_data_path}")
    sys.exit(1)

shutil.copy(f'{test_data_path}/input.cnf', config.INPUT_CNF_FILE)
shutil.copy(f'{test_data_path}/mock_shim.py', 'src/mock_shim.py')

print("=" * 70)
print(f"  RUNNING TEST: {test_name}")
print("=" * 70)
print()

# Run the solver
from src.dpll import DPLLSolver
solver = DPLLSolver()
success, model = solver.solve()

print()
print("=" * 70)
print("  RESULT")
print("=" * 70)
if success:
    print("  Status: SATISFIABLE")
    print(f"  Model: {model}")
else:
    print("  Status: UNSATISFIABLE")
    print("  Model: None")

print()
print("=" * 70)
print("  MASTER TRACE (automatically generated)")
print("=" * 70)
print()

# Display the master trace
with open(config.MASTER_TRACE_FILE, 'r') as f:
    print(f.read())
