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