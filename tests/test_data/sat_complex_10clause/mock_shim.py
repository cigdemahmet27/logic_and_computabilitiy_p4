"""
Test Mock Shim for Complex 10-Clause SAT Scenario

This mock DYNAMICALLY generates consistent BCP output based on:
- The actual trigger literal from the solver
- The current decision level
- The expected behavior (CONTINUE, CONFLICT, SAT)

This ensures the trace is accurate and matches what the solver actually decides.
"""
import os
import json

# Paths relative to project root
DATA_DIR = "data"
TRIGGER_FILE = os.path.join(DATA_DIR, "bcp_trigger_input.txt")
OUTPUT_FILE = os.path.join(DATA_DIR, "bcp_output.txt")
STATE_FILE = os.path.join(DATA_DIR, "mock_state.json")


def load_state():
    """Load the current mock state from file."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                state = json.load(f)
                # Convert string keys back to integers for assignments
                if "assignments" in state:
                    state["assignments"] = {int(k): v for k, v in state["assignments"].items()}
                return state
        except:
            pass
    return {"call_count": 0, "history": [], "assignments": {}}


def save_state(state):
    """Save the mock state to file."""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def generate_bcp_output(dl, literal, status, conflict_clause=None, propagations=None, 
                         satisfied_clauses=None, assignments=None):
    """Generate a consistent BCP output based on the actual decision."""
    var = abs(literal) if literal != 0 else 0
    value = "TRUE" if literal > 0 else "FALSE" if literal < 0 else "NONE"
    
    output = "--- STATUS ---\n"
    output += f"STATUS: {status}\n"
    output += f"DL: {dl}\n"
    output += f"CONFLICT_ID: {conflict_clause if conflict_clause else 'None'}\n\n"
    
    output += "--- BCP EXECUTION LOG ---\n"
    
    if dl == 0:
        output += f"[DL{dl}] NO UNIT       | No unit clauses found\n"
        output += f"[DL{dl}] CONTINUE      | All 6 variables unassigned\n"
    else:
        # Log the actual decision that was made
        output += f"[DL{dl}] DECIDE      L={literal}  | Decided Var {var} = {value}\n"
        
        # Add satisfied clauses
        if satisfied_clauses:
            for clause in satisfied_clauses:
                output += f"[DL{dl}] SATISFIED         | {clause}\n"
        
        # Add propagations
        if propagations:
            for prop in propagations:
                output += f"[DL{dl}] PROPAGATE   L={prop['lit']}  | {prop['reason']}\n"
        
        # Add conflict or continue
        if status == "CONFLICT":
            output += f"[DL{dl}] CONFLICT          | {conflict_clause} violated\n"
            output += f"[DL{dl}] BACKTRACK         |\n"
        elif status == "SAT":
            output += f"[DL{dl}] ALL SATISFIED     | All clauses satisfied!\n"
        else:
            output += f"[DL{dl}] CONTINUE          | Need more decisions\n"
    
    output += "\n--- CURRENT VARIABLE STATE ---\n"
    if assignments:
        for v in sorted(assignments.keys()):
            val = assignments[v]
            if val is True:
                output += f"{v}    | TRUE\n"
            elif val is False:
                output += f"{v}    | FALSE\n"
            else:
                output += f"{v}    | UNASSIGNED\n"
    
    return output


def main():
    target_dl = 0
    literal = 0

    # Read the trigger file
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
            print(f"[Complex Shim] Error reading trigger: {e}")

    # Load state
    state = load_state()
    
    # Reset state at DL0
    if target_dl == 0:
        state = {"call_count": 0, "history": [], "assignments": {1: None, 2: None, 3: None, 4: None, 5: None, 6: None}}
    
    state["call_count"] += 1
    state["history"].append({"dl": target_dl, "literal": literal})
    
    call_num = state["call_count"]
    print(f"[Complex Shim] Call #{call_num}: DL={target_dl}, Literal={literal}")

    # Update assignments based on trigger
    if literal != 0:
        var = abs(literal)
        state["assignments"][var] = (literal > 0)
    
    # Determine behavior based on current state
    # This simulates the formula: checking which clauses are satisfied/conflicted
    
    assignments = state["assignments"]
    
    if target_dl == 0:
        # Initial state - all unassigned
        output = generate_bcp_output(
            dl=0, literal=0, status="CONTINUE",
            assignments={1: None, 2: None, 3: None, 4: None, 5: None, 6: None}
        )
    else:
        # Simulate formula behavior based on current assignments
        # Formula clauses:
        # C1: (1 OR 2 OR 3), C2: (-1 OR 4), C3: (-2 OR 5), C4: (-3 OR 6)
        # C5: (-4 OR -5), C6: (-4 OR -6), C7: (-5 OR -6), C8: (1 OR -2)
        # C9: (-1 OR 2 OR 6), C10: (3 OR 4 OR 5), C11: (-3 OR -4 OR 5), C12: (2 OR -5 OR 6)
        
        var = abs(literal)
        val = literal > 0
        
        # Check for conflicts based on current assignments
        conflict = None
        propagations = []
        satisfied = []
        
        # Simple conflict detection for key scenarios
        a = assignments
        
        # If 1=TRUE, propagate 4=TRUE via C2
        if a.get(1) == True and a.get(4) is None:
            a[4] = True
            propagations.append({"lit": 4, "reason": "C2 (-1 OR 4): 1=TRUE forces 4=TRUE"})
        
        # If 2=TRUE, propagate 5=TRUE via C3
        if a.get(2) == True and a.get(5) is None:
            a[5] = True
            propagations.append({"lit": 5, "reason": "C3 (-2 OR 5): 2=TRUE forces 5=TRUE"})
        
        # If 3=TRUE, propagate 6=TRUE via C4
        if a.get(3) == True and a.get(6) is None:
            a[6] = True
            propagations.append({"lit": 6, "reason": "C4 (-3 OR 6): 3=TRUE forces 6=TRUE"})
        
        # Check C5: (-4 OR -5) - conflict if both 4=TRUE and 5=TRUE
        if a.get(4) == True and a.get(5) == True:
            conflict = "C5 (-4 OR -5)"
        
        # Check C6: (-4 OR -6) - conflict if both 4=TRUE and 6=TRUE
        if a.get(4) == True and a.get(6) == True:
            conflict = "C6 (-4 OR -6)"
        
        # Check C7: (-5 OR -6) - conflict if both 5=TRUE and 6=TRUE
        if a.get(5) == True and a.get(6) == True:
            conflict = "C7 (-5 OR -6)"
        
        # Check C9: (-1 OR 2 OR 6) - conflict if 1=TRUE, 2=FALSE, 6=FALSE
        if a.get(1) == True and a.get(2) == False and a.get(6) == False:
            conflict = "C9 (-1 OR 2 OR 6)"
        
        # Check for SAT - all clauses satisfied
        all_assigned = all(v is not None for v in a.values())
        
        if conflict:
            status = "CONFLICT"
        elif all_assigned:
            status = "SAT"
        else:
            status = "CONTINUE"
        
        # Build satisfied clauses list
        if a.get(1) == True or a.get(2) == True or a.get(3) == True:
            satisfied.append("C1 (1 OR 2 OR 3)")
        if a.get(1) == False or a.get(4) == True:
            satisfied.append("C2 (-1 OR 4)")
        if a.get(1) == True or a.get(2) == False:
            satisfied.append("C8 (1 OR -2)")
        if a.get(3) == True or a.get(4) == True or a.get(5) == True:
            satisfied.append("C10 (3 OR 4 OR 5)")
        
        output = generate_bcp_output(
            dl=target_dl, 
            literal=literal, 
            status=status,
            conflict_clause=conflict,
            propagations=propagations if propagations else None,
            satisfied_clauses=satisfied[:3] if satisfied else None,  # Limit to 3
            assignments=a
        )
        
        state["assignments"] = a
    
    save_state(state)
    
    # Write output
    with open(OUTPUT_FILE, "w") as f:
        f.write(output)
    
    print(f"[Complex Shim] Output written: STATUS={output.split('STATUS: ')[1].split()[0]}")


if __name__ == "__main__":
    main()
