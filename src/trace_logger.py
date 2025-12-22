"""
Trace Logger - Generates the Master Execution Trace

This module creates the "Official Execution Log" for Project #5.
It logs every event during DPLL execution:
- Decision Level changes
- Decisions made by the search engine
- BCP results from the inference engine
- Backtracking events
- Final result
"""

import config
import os


class TraceLogger:
    def __init__(self):
        """Initialize the trace logger and create a fresh trace file."""
        # Clear the trace file at the start of a new run
        if os.path.exists(config.MASTER_TRACE_FILE):
            os.remove(config.MASTER_TRACE_FILE)
        
        # Write header
        self._append("=" * 80 + "\n")
        self._append("                         MASTER EXECUTION TRACE\n")
        self._append("                         DPLL SAT Solver - Project #4\n")
        self._append("=" * 80 + "\n\n")

    def log_start(self, cnf_file):
        """Log the start of solving with CNF file info."""
        self._append(f"CNF File: {cnf_file}\n")
        self._append("-" * 40 + "\n\n")

    def log_decision_level_start(self, dl):
        """Log the start of a new decision level."""
        self._append("\n" + "=" * 60 + "\n")
        self._append(f"--- DECISION LEVEL {dl} ---\n")
        self._append("=" * 60 + "\n")

    def log_decision(self, dl, literal):
        """Log a decision made by the search engine."""
        var = abs(literal)
        value = "TRUE" if literal > 0 else "FALSE"
        self._append(f"[DL{dl}] DECIDE      L={literal:4}  | Var {var} = {value}\n")

    def log_bcp_trigger(self, dl, literal):
        """Log that we're triggering BCP with a decision."""
        self._append(f"[DL{dl}] TRIGGER_BCP L={literal:4}  | Calling Inference Engine\n")

    def log_bcp_result(self, dl, status, conflict_id=None):
        """Log the result from BCP."""
        if status == config.STATUS_SAT:
            self._append(f"[DL{dl}] BCP_RESULT        | STATUS: SAT - All clauses satisfied!\n")
        elif status == config.STATUS_CONFLICT or status == config.STATUS_UNSAT:
            conflict_str = f" (Clause: {conflict_id})" if conflict_id else ""
            self._append(f"[DL{dl}] BCP_RESULT        | STATUS: CONFLICT{conflict_str}\n")
        else:
            self._append(f"[DL{dl}] BCP_RESULT        | STATUS: CONTINUE\n")

    def log_propagations(self, bcp_log):
        """Log the propagation details from BCP output."""
        # Extract just the BCP execution log lines
        in_log_section = False
        for line in bcp_log.split('\n'):
            if "BCP EXECUTION LOG" in line:
                in_log_section = True
                continue
            if "CURRENT VARIABLE STATE" in line:
                in_log_section = False
                continue
            if in_log_section and line.strip() and line.strip().startswith('['):
                self._append(f"  {line.strip()}\n")

    def log_variable_state(self, assignments, unassigned_vars):
        """Log the current variable state."""
        self._append("\n--- CURRENT VARIABLE STATE ---\n")
        
        # Combine and sort all variables
        all_vars = set(assignments.keys()) | set(unassigned_vars)
        for var in sorted(all_vars):
            if var in assignments:
                val = "TRUE" if assignments[var] else "FALSE"
            else:
                val = "UNASSIGNED"
            self._append(f"  {var:4}  | {val}\n")

    def log_backtrack(self, from_dl, literal_tried, next_literal):
        """Log a backtracking event."""
        self._append("\n" + "*" * 60 + "\n")
        self._append(f"*** BACKTRACK at DL {from_dl} ***\n")
        self._append(f"    Failed literal: {literal_tried}\n")
        self._append(f"    Trying opposite: {next_literal}\n")
        self._append("*" * 60 + "\n\n")

    def log_branch_exhausted(self, dl):
        """Log when both branches at a decision level have been tried."""
        self._append(f"[DL{dl}] EXHAUSTED         | Both branches failed, propagating failure upward\n")

    def log_final_result(self, success, model, decisions_made, backtracks):
        """Log the final result of the solver."""
        self._append("\n" + "=" * 80 + "\n")
        self._append("                              FINAL RESULT\n")
        self._append("=" * 80 + "\n\n")
        
        if success:
            self._append("RESULT: SATISFIABLE\n\n")
            self._append("SATISFYING ASSIGNMENT:\n")
            if model:
                for var in sorted(model.keys()):
                    val = "TRUE" if model[var] else "FALSE"
                    self._append(f"  Variable {var} = {val}\n")
            else:
                self._append("  (Empty model - trivially SAT)\n")
        else:
            self._append("RESULT: UNSATISFIABLE\n\n")
            self._append("No satisfying assignment exists.\n")
        
        self._append(f"\nSTATISTICS:\n")
        self._append(f"  Decisions made: {decisions_made}\n")
        self._append(f"  Backtracks: {backtracks}\n")
        self._append("\n" + "=" * 80 + "\n")

    def log_step(self, dl, event_type, details):
        """
        Legacy method - Appends a structured log entry.
        Format based on Sample Run outputs.
        """
        log_entry = f"[DL{dl}] {event_type}: {details}\n"
        self._append(log_entry)

    def append_raw_content(self, content):
        """
        Appends the raw BCP Execution Log from the Inference Engine.
        This captures all the details from the inference engine output.
        """
        if content:
            # Add a separator before raw content
            self._append("\n--- RAW BCP OUTPUT ---\n")
            self._append(content)
            self._append("--- END RAW BCP OUTPUT ---\n")

    def _append(self, text):
        """Internal method to append text to the trace file."""
        with open(config.MASTER_TRACE_FILE, "a") as f:
            f.write(text)