"""
Goal: Mathematically decide which unassigned variable to pick next. 
You are forbidden from simply picking them in order (1, 2, 3...).

What you must do:
Implement a class/function for MOM (Maximum Occurrences in Minimum-Sized Clauses) or JW (Jeroslow-Wang).

The MOM Logic (Recommended):
Step A: Look at the current clause database (you get this from the initial CNF parsing or by tracking clause states).
Step B: Find the "Minimum Size": Ignore satisfied clauses. Look at the remaining unsatisfied clauses. 
        What is the smallest current length? (e.g., do we have any clauses with only 2 literals left?).
Step C: Count: Among those smallest clauses, which LITERAL (with polarity) appears most often?
Step D: Return that LITERAL.

Why? This targets the "critical" clauses to force a unit propagation or a conflict early, speeding up the search.
"""

import config


class MOMHeuristic:
    def __init__(self, cnf_path):
        """
        Loads the CNF formula once at the start.
        We need the original clauses to calculate sizes dynamically.
        """
        self.clauses = []
        self._parse_cnf(cnf_path)

    def _parse_cnf(self, cnf_path):
        """
        Reads the .cnf file and stores clauses as lists of integers.
        Example: "1 -2 3 0" -> [1, -2, 3]
        """
        try:
            with open(cnf_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and header
                    if line.startswith('c') or line.startswith('p') or not line:
                        continue
                    
                    # Parse integers, remove the trailing '0'
                    literals = [int(x) for x in line.split() if x != '0']
                    if literals:
                        self.clauses.append(literals)
        except FileNotFoundError:
            print(f"Error: CNF file not found at {cnf_path}")
            self.clauses = []

    def select_variable(self, assignments_dict):
        """
        Implements the MOM Heuristic logic with proper literal polarity selection.
        
        The MOM (Maximum Occurrences in Minimum-sized Clauses) heuristic:
        1. Finds the minimum size among all unsatisfied clauses
        2. Among those minimum-sized clauses, counts literal occurrences
        3. Returns the LITERAL (with polarity) that appears most often
        
        Args:
            assignments_dict: Dict {variable_id: True/False/None} for vars.
                              None means UNASSIGNED.
                              
        Returns:
            int: The selected LITERAL (e.g., 3 or -3) with proper polarity.
                 Returns None if no variables are left (Formula Solved).
        """
        
        # 1. Identify Unsatisfied Clauses & Calculate their Current Sizes
        unsatisfied_clauses = []
        min_size = float('inf')

        for clause in self.clauses:
            is_satisfied = False
            current_size = 0
            
            for literal in clause:
                var = abs(literal)
                val = assignments_dict.get(var)  # Returns True, False, or None
                
                # Check logic: 
                # If literal is positive (x) and val is True -> Satisfied
                # If literal is negative (-x) and val is False -> Satisfied
                if (literal > 0 and val is True) or (literal < 0 and val is False):
                    is_satisfied = True
                    break  # Stop checking this clause, it's done.
                
                # If val is None, this literal is unassigned -> It contributes to size
                if val is None:
                    current_size += 1
            
            if not is_satisfied:
                unsatisfied_clauses.append((clause, current_size))
                if current_size < min_size:
                    min_size = current_size

        # If no unsatisfied clauses remain, we might be done, or have full freedom.
        if not unsatisfied_clauses:
            return None

        # 2. Filter: Keep only clauses with the Minimum Size
        target_clauses = [c[0] for c in unsatisfied_clauses if c[1] == min_size]

        # 3. Count LITERAL occurrences (tracking polarity separately)
        # This is the key fix: we count +x and -x separately
        literal_counts = {}
        
        for clause in target_clauses:
            for literal in clause:
                var = abs(literal)
                # Only count if the variable is unassigned
                if assignments_dict.get(var) is None:
                    # Count the actual literal (with sign), not just the variable
                    literal_counts[literal] = literal_counts.get(literal, 0) + 1

        # 4. Pick the LITERAL with the Max Count
        if not literal_counts:
            return None  # Should not happen if clauses exist
            
        # Return the literal (with polarity) that appears most often
        # This ensures we pick the polarity that satisfies more clauses
        best_literal = max(literal_counts, key=literal_counts.get)
        return best_literal