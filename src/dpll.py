import subprocess
import sys
import config
from src.io_manager import IOManager
from src.heuristics import MOMHeuristic
from src.trace_logger import TraceLogger

class DPLLSolver:
    def __init__(self):
        self.io = IOManager()
        self.logger = TraceLogger()
        self.heuristic = MOMHeuristic(config.INPUT_CNF_FILE)

    def run_inference_engine(self):
        """
        Executes the mock inference engine.
        Ensures the external tool runs and updates bcp_output.txt.
        """
        try:
            # --- IMPORTANT ---
            # Using the Mock Shim (Python script) instead of an .exe
            subprocess.run(["python", "src/mock_shim.py"], check=True)
            
        except subprocess.CalledProcessError:
            print("Error: Inference Engine crashed or returned non-zero exit code.")
            sys.exit(1)
        except FileNotFoundError:
            print(f"Error: Could not find executable at {config.INFERENCE_ENGINE_EXE}")
            sys.exit(1)

    def solve(self):
        """
        Public entry point. Starts the recursion at Decision Level 0.
        """
        print("--- Starting DPLL Search ---")
        
        # Run logic at Decision Level 0
        # First, write trigger and run engine to initialize DL 0
        self.io.write_trigger(0, 0)  # No literal chosen yet at DL 0
        self.run_inference_engine()
        
        return self._dpll_recursive(dl=0)

    def _dpll_recursive(self, dl):
        """
        The Main Recursive Logic [Source: 1.1.1]
        """
        # 1. READ STATUS
        # We read the result of the LAST action (Decision or Propagation)
        state = self.io.read_bcp_output()
        
        # Log the raw output from the engine to the Master Trace [Source: 109]
        self.logger.append_raw_content(state["full_log"])
        
        status = state["status"]
        assignments = state["assignments"]

        # 2. CHECK STATUS (Base Cases)
        if status == config.STATUS_SAT:
            print(f"SATISFIABLE at DL {dl}")
            return True, assignments

        if status == config.STATUS_UNSAT or status == config.STATUS_CONFLICT:
            # Conflict found, we must backtrack [Source: 45]
            return False, None

        # 3. MAKE DECISION (Branching)
        # Status is CONTINUE, so we pick a variable [Source: 46]
        
        # Get unassigned variables for the heuristic
        # We construct a full assignment dict including unassigned as None
        full_assignment_map = assignments.copy()
        for var in state["unassigned_vars"]:
            full_assignment_map[var] = None
            
        chosen_literal = self.heuristic.select_variable(full_assignment_map)

        if chosen_literal is None:
            # No variables left to pick, but status wasn't SAT? 
            # This handles edge cases where engine might not report SAT immediately.
            return True, assignments

        # 4. RECURSION - BRANCH 1 (Try True/Heuristic Choice)
        next_dl = dl + 1
        
        # Action: Write Trigger -> Run Engine -> Recurse
        self.io.write_trigger(chosen_literal, next_dl)
        self.run_inference_engine()
        
        result, model = self._dpll_recursive(next_dl)
        if result:
            return True, model

        # 5. RECURSION - BRANCH 2 (Backtrack & Try False/Opposite)
        # If Branch 1 failed, we "undo" and try the opposite [Source: 48]
        
        negated_literal = -chosen_literal
        
        self.io.write_trigger(negated_literal, next_dl)
        self.run_inference_engine()
        
        result, model = self._dpll_recursive(next_dl)
        if result:
            return True, model

        # 6. FAILURE
        # If both branches fail, return failure to the previous level
        return False, None