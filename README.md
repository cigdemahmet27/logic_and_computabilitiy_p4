# DPLL SAT Solver - Search Engine (Project #4)

A Python implementation of the **DPLL (Davis-Putnam-Logemann-Loveland)** algorithm for solving Boolean Satisfiability (SAT) problems. This module serves as the Search Engine component that systematically explores the space of possible variable assignments.

## Overview

The DPLL algorithm is a complete, backtracking-based search algorithm for deciding the satisfiability of propositional logic formulae in conjunctive normal form (CNF). This implementation includes:

- **Recursive DPLL Search** with backtracking
- **MOM Heuristic** (Maximum Occurrences in Minimum-sized Clauses) for variable selection
- **Integration with Inference Engine** (Project #3) for Boolean Constraint Propagation (BCP)
- **Automatic Master Trace Generation** for execution logging

## Algorithm Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        DPLL Algorithm                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Run BCP (Call Inference Engine)                            │
│            │                                                    │
│            ▼                                                    │
│  2. Check Status                                                │
│     ┌──────┼──────┐                                            │
│     │      │      │                                            │
│    SAT  CONFLICT  CONTINUE                                      │
│     │      │      │                                            │
│     ▼      ▼      ▼                                            │
│  Return  Backtrack  3. Make Decision (MOM Heuristic)           │
│  Success  (Fail)       │                                       │
│                        ▼                                        │
│                   4. Recurse with chosen literal                │
│                        │                                        │
│                   ┌────┴────┐                                   │
│                   │         │                                   │
│                Success    Fail                                  │
│                   │         │                                   │
│                   ▼         ▼                                   │
│                Return   5. Try opposite literal                 │
│                Success      │                                   │
│                        ┌────┴────┐                              │
│                        │         │                              │
│                     Success    Fail                             │
│                        │         │                              │
│                        ▼         ▼                              │
│                     Return   Return Fail                        │
│                     Success  (Backtrack further)                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## MOM Heuristic (Variable Selection)

The **Maximum Occurrences in Minimum-sized Clauses** heuristic prioritizes variables that appear frequently in short, critical clauses:

1. **Find Minimum Size**: Identify the smallest unsatisfied clause(s)
2. **Count Literal Occurrences**: Among minimum-sized clauses, count how often each literal appears
3. **Select Best Literal**: Return the literal (with polarity) that appears most frequently

This approach aims to:
- Satisfy critical clauses early
- Trigger strong Boolean Constraint Propagation
- Detect conflicts quickly

## Project Structure

```
logic_and_computabilitiy_p4/
├── main.py                 # Entry point
├── run_test.py             # Test runner with trace display
├── config.py               # Configuration and file paths
│
├── src/
│   ├── dpll.py             # Core DPLL algorithm
│   ├── heuristics.py       # MOM heuristic implementation
│   ├── io_manager.py       # File I/O for BCP communication
│   ├── trace_logger.py     # Master trace generation
│   └── mock_shim.py        # Mock inference engine (for testing)
│
├── data/
│   ├── input.cnf           # Input CNF formula
│   ├── bcp_trigger_input.txt   # Trigger for inference engine
│   ├── bcp_output.txt      # Output from inference engine
│   └── master_trace.txt    # Complete execution trace
│
└── tests/
    ├── tests_dpll.py       # Unit tests
    └── test_data/
        ├── sat_simple/         # Simple SAT test
        ├── sat_with_backtrack/ # SAT requiring backtracking
        ├── sat_4var/           # 4-variable SAT
        ├── sat_6var_deep/      # 6-variable SAT (4+ decision levels)
        ├── conflict_after_dl1/ # Conflict at DL1 with backtracking
        └── unsat_after_dl2/    # UNSAT discovered after exploring DL1
```

## Usage

### Running with Default Input
```bash
python main.py
```

### Running Specific Tests
```bash
python run_test.py sat_simple          # Simple SAT formula
python run_test.py sat_with_backtrack  # SAT with backtracking
python run_test.py sat_4var            # 4-variable SAT (multiple DLs)
python run_test.py sat_6var_deep       # 6-variable SAT (4+ decision levels)
python run_test.py conflict_after_dl1  # Conflict at DL1 with backtracking
python run_test.py unsat_after_dl2     # UNSAT discovered after DL1 exploration
```

### Running Unit Tests
```bash
python tests/tests_dpll.py
```

## Input Format (DIMACS CNF)

The input uses standard DIMACS CNF format:

```
c This is a comment
p cnf <num_vars> <num_clauses>
<literal1> <literal2> ... 0
<literal3> <literal4> ... 0
```

**Example:**
```
c Formula: (1 OR -2) AND (-1 OR 2 OR 3)
p cnf 3 2
1 -2 0
-1 2 3 0
```

## Output: Master Execution Trace

The solver automatically generates a complete execution trace in `data/master_trace.txt`:

```
================================================================================
                         MASTER EXECUTION TRACE
                         DPLL SAT Solver - Project #4
================================================================================

CNF File: data/input.cnf
----------------------------------------

============================================================
--- DECISION LEVEL 0 ---
============================================================
[DL0] BCP_RESULT        | STATUS: CONTINUE

--- CURRENT VARIABLE STATE ---
     1  | UNASSIGNED
     2  | UNASSIGNED

============================================================
--- DECISION LEVEL 1 ---
============================================================
[DL1] DECIDE      L=  -1  | Var 1 = FALSE
[DL1] BCP_RESULT        | STATUS: SAT - All clauses satisfied!

--- CURRENT VARIABLE STATE ---
     1  | FALSE
     2  | TRUE

================================================================================
                              FINAL RESULT
================================================================================

RESULT: SATISFIABLE

SATISFYING ASSIGNMENT:
  Variable 1 = FALSE
  Variable 2 = TRUE

STATISTICS:
  Decisions made: 1
  Backtracks: 0

================================================================================
```

## Communication Protocol

### BCP Trigger Input (Search Engine → Inference Engine)
```
TRIGGER_LITERAL: <literal>
DL: <decision_level>
```

### BCP Output (Inference Engine → Search Engine)
```
--- STATUS ---
STATUS: <SAT|UNSAT|CONFLICT|CONTINUE>
DL: <decision_level>
CONFLICT_ID: <clause_id or None>

--- BCP EXECUTION LOG ---
[DL<n>] DECIDE      L=<lit>  |
[DL<n>] UNIT        L=<lit>  | <clause>
[DL<n>] ASSIGN      L=<lit>  |
[DL<n>] SATISFIED         | <clause>
[DL<n>] CONFLICT          | <clause>

--- CURRENT VARIABLE STATE ---
<var>    | <TRUE|FALSE|UNASSIGNED>
```

## Test Cases

| Test | Variables | Clauses | Result | Description |
|------|-----------|---------|--------|-------------|
| `sat_simple` | 3 | 3 | SAT | Simple satisfiable formula |
| `sat_with_backtrack` | 2 | 3 | SAT | Requires backtracking |
| `sat_4var` | 4 | 3 | SAT | Multiple decision levels |
| `sat_6var_deep` | 6 | 6 | SAT | 4+ decision levels required |
| `conflict_after_dl1` | 3 | 5 | SAT | **Conflict at DL1**, backtrack to SAT |
| `unsat_after_dl2` | 2 | 4 | UNSAT | **UNSAT after DL1 exploration** (both branches fail) |

## Integration with Other Projects

- **Project #2 (Parser)**: Provides the input CNF file
- **Project #3 (Inference Engine)**: Performs BCP, returns status
- **Project #5 (Proof Generator)**: Uses the Master Trace for proof generation

## Authors

BLG345E - Logic and Computability - Term Project #4

## License

This project is for educational purposes as part of the BLG345E course.