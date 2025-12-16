"""
Goal: The entry point that sets everything up.

What you must do:

Parse Initial CNF: Read the .cnf file (Project #2 output) so your Heuristic knows the initial clauses.


Initial Check (DL 0): Before making any guesses, run the Inference Engine once (as if DL=0) to check for initial unit propagations.

Start Recursion: Call dpll.solve(decision_level=0).

Final Output:

If solve returns True: Print "SAT" and the final assignment.

If solve returns False: Print "UNSAT" and the trace.
"""

import config
from src.dpll import DPLLSolver

def main():
    print(f"Target CNF: {config.INPUT_CNF_FILE}")
    
    # Initialize Solver
    solver = DPLLSolver()
    
    # Run
    success, model = solver.solve()
    
    # Final Output
    print("\n--- FINAL RESULT ---")
    if success:
        print("RESULT: SATISFIABLE")
        print("Model:", model)
        # Sort keys for pretty printing
        sorted_vars = sorted(model.keys())
        print("Assignment:")
        for var in sorted_vars:
            val = model[var]
            print(f"  Var {var}: {val}")
    else:
        print("RESULT: UNSATISFIABLE")
    
    # Always print the trace file path and content to terminal
    print("\nTrace written to:", config.MASTER_TRACE_FILE)
    print("\n--- MASTER TRACE CONTENT ---")
    try:
        with open(config.MASTER_TRACE_FILE, "r") as f:
            trace_content = f.read()
            print(trace_content)
    except FileNotFoundError:
        print("(No trace file found)")

if __name__ == "__main__":
    main()

    
    
    