"""
DPLL SAT Solver - Search Engine (Project #4)

This module implements the core DPLL (Davis-Putnam-Logemann-Loveland) algorithm
that systematically explores the space of possible variable assignments.

The DPLL recursive process:
1. Run Inference: Call the Inference Engine to perform BCP on the current partial assignment
2. Check Status: Analyze the result (SAT, CONFLICT, or CONTINUE)
3. Make Decision (Branching): If CONTINUE, select an unassigned variable using heuristics
4. Recurse: Call DPLL recursively; if it fails, try the opposite value (backtracking)

This module also maintains and writes the complete Master Execution Trace.
"""

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
        
        # Statistics for trace
        self.decisions_made = 0
        self.backtracks = 0

    def run_inference_engine(self):
        """
        Executes the mock inference engine.
        Ensures the external tool runs and updates bcp_output.txt.
        """
        try:
            # --- IMPORTANT ---
            # Using the Mock Shim (Python script) instead of an .exe
            subprocess.run(["python", "src/mock_shim.py"], check=True, 
                          capture_output=True, text=True)
            
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
        
        # Log start
        self.logger.log_start(config.INPUT_CNF_FILE)
        
        # Log DL 0
        self.logger.log_decision_level_start(0)
        
        # Run logic at Decision Level 0
        # First, write trigger and run engine to initialize DL 0
        self.io.write_trigger(0, 0)  # No literal chosen yet at DL 0
        self.run_inference_engine()
        
        # Run the recursive DPLL
        success, model = self._dpll_recursive(dl=0)
        
        # Log final result
        self.logger.log_final_result(success, model, self.decisions_made, self.backtracks)
        
        return success, model

    def _dpll_recursive(self, dl):
        """
        The Main Recursive Logic [Source: 1.1.1]
        
        This is the core DPLL algorithm that:
        1. Reads BCP results from the Inference Engine
        2. Checks for SAT/CONFLICT base cases
        3. Makes a decision using the MOM heuristic
        4. Recursively explores both branches (true/false)
        5. Backtracks if a branch leads to conflict
        """
        # 1. READ STATUS
        # We read the result of the LAST action (Decision or Propagation)
        state = self.io.read_bcp_output()
        
        status = state["status"]
        assignments = state["assignments"]
        conflict_id = state.get("conflict_id")
        
        # Log BCP result
        self.logger.log_bcp_result(dl, status, conflict_id)
        
        # Log propagations from BCP
        self.logger.log_propagations(state["full_log"])
        
        # Log current variable state
        self.logger.log_variable_state(assignments, state["unassigned_vars"])

        # 2. CHECK STATUS (Base Cases)
        if status == config.STATUS_SAT:
            print(f"SATISFIABLE at DL {dl}")
            return True, assignments

        if status == config.STATUS_UNSAT or status == config.STATUS_CONFLICT:
            # Conflict found, we must backtrack [Source: 45]
            print(f"CONFLICT at DL {dl}, backtracking...")
            return False, None

        # 3. MAKE DECISION (Branching)
        # Status is CONTINUE, so we pick a variable [Source: 46]
        
        # Get unassigned variables for the heuristic
        # We construct a full assignment dict including unassigned as None
        full_assignment_map = assignments.copy()
        for var in state["unassigned_vars"]:
            full_assignment_map[var] = None
            
        # select_variable now returns a LITERAL (with polarity), not just a variable
        chosen_literal = self.heuristic.select_variable(full_assignment_map)

        if chosen_literal is None:
            # No variables left to pick, but status wasn't SAT? 
            # This handles edge cases where engine might not report SAT immediately.
            return True, assignments

        # 4. RECURSION - BRANCH 1 (Try the heuristic's chosen literal)
        next_dl = dl + 1
        self.decisions_made += 1
        
        # Log new decision level and decision
        self.logger.log_decision_level_start(next_dl)
        self.logger.log_decision(next_dl, chosen_literal)
        
        print(f"[DL {next_dl}] Deciding: {chosen_literal}")
        
        # Action: Write Trigger -> Run Engine -> Recurse
        self.io.write_trigger(chosen_literal, next_dl)
        self.run_inference_engine()
        
        result, model = self._dpll_recursive(next_dl)
        if result:
            return True, model

        # 5. RECURSION - BRANCH 2 (Backtrack & Try Opposite Literal)
        # If Branch 1 failed, we "undo" and try the opposite [Source: 48]
        
        negated_literal = -chosen_literal
        self.backtracks += 1
        
        # Log backtrack
        self.logger.log_backtrack(next_dl, chosen_literal, negated_literal)
        
        print(f"[DL {next_dl}] Backtracking, trying opposite: {negated_literal}")
        
        # Log decision with opposite literal (still at same DL)
        self.logger.log_decision(next_dl, negated_literal)
        
        # We stay at the SAME decision level since this is the alternative at this decision point
        self.io.write_trigger(negated_literal, next_dl)
        self.run_inference_engine()
        
        result, model = self._dpll_recursive(next_dl)
        if result:
            return True, model

        # 6. FAILURE
        # If both branches fail, return failure to the previous level
        self.logger.log_branch_exhausted(next_dl)
        print(f"[DL {dl}] Both branches failed, propagating failure upward")
        return False, None