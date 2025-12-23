"""
DPLL SAT Solver Test Suite

This module contains comprehensive tests for the DPLL Search Engine (Project #4).
Each test uses its own mock data files to simulate the Inference Engine's responses.

Test Cases:
1. test_sat_simple: A simple SAT formula that resolves without backtracking
2. test_unsat_conflict: An UNSAT formula that conflicts immediately at DL 0
3. test_sat_with_backtrack: A SAT formula that requires backtracking (first branch fails)
4. test_sat_4var: A 4-variable SAT with 2 decision levels
5. test_sat_6var_deep: A 6-variable SAT requiring 4+ decision levels (DL0-DL4)

Usage:
    python -m pytest tests/tests_dpll.py -v
    OR
    python tests/tests_dpll.py
"""

import os
import sys
import shutil
import unittest

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

import config
from src.dpll import DPLLSolver
from src.heuristics import MOMHeuristic


class TestDPLLSolver(unittest.TestCase):
    """Test cases for the DPLL SAT Solver"""
    
    def setUp(self):
        """Clean up data directory before each test"""
        # Remove old output files
        for f in ["bcp_output.txt", "bcp_trigger_input.txt", "master_trace.txt"]:
            path = os.path.join(config.DATA_DIR, f)
            if os.path.exists(path):
                os.remove(path)
    
    def tearDown(self):
        """Restore original mock shim after each test"""
        pass  # Tests restore the shim themselves
    
    def _setup_test(self, test_name):
        """
        Setup a test by:
        1. Copying the test's CNF file to input.cnf
        2. Replacing the mock shim with the test-specific one
        """
        test_data_dir = os.path.join(PROJECT_ROOT, "tests", "test_data", test_name)
        
        # Copy CNF file
        src_cnf = os.path.join(test_data_dir, "input.cnf")
        dst_cnf = config.INPUT_CNF_FILE
        shutil.copy(src_cnf, dst_cnf)
        
        # Copy mock shim
        src_shim = os.path.join(test_data_dir, "mock_shim.py")
        dst_shim = os.path.join(PROJECT_ROOT, "src", "mock_shim.py")
        shutil.copy(src_shim, dst_shim)
        
        print(f"\n[TEST] Setup complete for '{test_name}'")
        print(f"  CNF: {src_cnf}")
        print(f"  Mock: {src_shim}")

    # =========================================================================
    # TEST 1: Simple SAT (No Backtracking Required)
    # =========================================================================
    def test_sat_simple(self):
        """
        Test a simple SAT formula: (1 OR 2) AND (-1 OR 2) AND (-2 OR 3)
        
        Expected behavior:
        - DL 0: All variables unassigned
        - DL 1: Heuristic picks literal, BCP finds SAT
        
        Expected result: SATISFIABLE
        """
        print("\n" + "="*60)
        print("TEST: SAT Simple (No Backtracking)")
        print("="*60)
        
        self._setup_test("sat_simple")
        
        solver = DPLLSolver()
        success, model = solver.solve()
        
        # Assertions
        self.assertTrue(success, "Formula should be SATISFIABLE")
        self.assertIsNotNone(model, "Model should not be None for SAT")
        
        # Check that the model is valid (at least one assignment exists)
        print(f"  Result: SAT")
        print(f"  Model: {model}")
        
        # Verify trace was created
        self.assertTrue(
            os.path.exists(config.MASTER_TRACE_FILE),
            "Master trace file should be created"
        )
        print(f"  Trace: {config.MASTER_TRACE_FILE}")

    # =========================================================================
    # TEST 2: UNSAT with Conflict at DL 0
    # =========================================================================
    def test_unsat_conflict(self):
        """
        Test an UNSAT formula: (1) AND (-1 OR 2) AND (-2)
        
        Expected behavior:
        - DL 0: Unit propagation finds conflict immediately
        
        Expected result: UNSATISFIABLE
        """
        print("\n" + "="*60)
        print("TEST: UNSAT Conflict (Immediate at DL 0)")
        print("="*60)
        
        self._setup_test("unsat_conflict")
        
        solver = DPLLSolver()
        success, model = solver.solve()
        
        # Assertions
        self.assertFalse(success, "Formula should be UNSATISFIABLE")
        self.assertIsNone(model, "Model should be None for UNSAT")
        
        print(f"  Result: UNSAT")
        print(f"  Model: {model}")
        
        # Verify trace was created
        self.assertTrue(
            os.path.exists(config.MASTER_TRACE_FILE),
            "Master trace file should be created for UNSAT"
        )
        print(f"  Trace: {config.MASTER_TRACE_FILE}")

    # =========================================================================
    # TEST 3: UNSAT 4-Variable with Propagation Chain
    # =========================================================================
    def test_unsat_4var_chain(self):
        """
        Test a 4-variable UNSAT formula with propagation chain:
        C1: (-4)           - unit clause, forces 4=FALSE
        C2: (4 OR 1)       - with 4=FALSE, forces 1=TRUE
        C3: (-1 OR 2)      - with 1=TRUE, forces 2=TRUE
        C4: (-2 OR 3)      - with 2=TRUE, forces 3=TRUE
        C5: (-3)           - unit clause, requires 3=FALSE -> CONFLICT!
        
        Expected behavior:
        - DL 0: Chain propagation: -4 -> 1 -> 2 -> 3 -> CONFLICT
        
        Expected result: UNSATISFIABLE (conflict detected at DL 0)
        """
        print("\n" + "="*60)
        print("TEST: UNSAT 4-Variable Chain Propagation")
        print("="*60)
        
        self._setup_test("unsat_4var_chain")
        
        solver = DPLLSolver()
        success, model = solver.solve()
        
        # Assertions
        self.assertFalse(success, "Formula should be UNSATISFIABLE")
        self.assertIsNone(model, "Model should be None for UNSAT")
        
        print(f"  Result: UNSAT (via propagation chain)")
        print(f"  Model: {model}")
        
        # Verify trace was created
        self.assertTrue(
            os.path.exists(config.MASTER_TRACE_FILE),
            "Master trace file should be created for UNSAT"
        )
        print(f"  Trace: {config.MASTER_TRACE_FILE}")

    # =========================================================================
    # TEST 4: SAT with Backtracking Required
    # =========================================================================
    def test_sat_with_backtrack(self):
        """
        Test a SAT formula that requires backtracking:
        (-1 OR -2) AND (1 OR 2) AND (2)
        
        Expected behavior:
        - DL 0: Unit propagation assigns 2=TRUE
        - DL 1: First choice (1=TRUE) leads to CONFLICT
        - DL 1: Backtrack, try 1=FALSE -> SAT
        
        Expected result: SATISFIABLE after backtracking
        """
        print("\n" + "="*60)
        print("TEST: SAT with Backtracking")
        print("="*60)
        
        self._setup_test("sat_with_backtrack")
        
        solver = DPLLSolver()
        success, model = solver.solve()
        
        # Assertions
        self.assertTrue(success, "Formula should be SATISFIABLE after backtracking")
        self.assertIsNotNone(model, "Model should not be None for SAT")
        
        print(f"  Result: SAT (after backtracking)")
        print(f"  Model: {model}")
        
        # Verify the model has the expected values
        # According to our mock: 1=FALSE, 2=TRUE
        self.assertEqual(model.get(1), False, "Variable 1 should be FALSE")
        self.assertEqual(model.get(2), True, "Variable 2 should be TRUE")
        
        # Verify trace was created
        self.assertTrue(
            os.path.exists(config.MASTER_TRACE_FILE),
            "Master trace file should be created"
        )
        print(f"  Trace: {config.MASTER_TRACE_FILE}")

    # =========================================================================
    # TEST 4: 4-Variable SAT (Multiple Decision Levels)
    # =========================================================================
    def test_sat_4var(self):
        """
        Test a 4-variable SAT formula:
        C1: (-1 OR -2 OR 3)
        C2: (-1 OR 2 OR 4)
        C3: (-3 OR -4)
        
        Expected behavior:
        - DL 0: All 4 variables unassigned
        - DL 1: Heuristic picks from smallest clause C3, decides -3 (3=FALSE)
        - DL 2: Heuristic picks -1 (1=FALSE) -> satisfies C1 and C2 -> SAT
        
        Expected result: SATISFIABLE with 1=FALSE, 3=FALSE
        """
        print("\n" + "="*60)
        print("TEST: 4-Variable SAT (Multiple Decision Levels)")
        print("="*60)
        
        self._setup_test("sat_4var")
        
        solver = DPLLSolver()
        success, model = solver.solve()
        
        # Assertions
        self.assertTrue(success, "Formula should be SATISFIABLE")
        self.assertIsNotNone(model, "Model should not be None for SAT")
        
        print(f"  Result: SAT")
        print(f"  Model: {model}")
        
        # Verify the model has the expected values
        # According to our mock: 1=FALSE, 3=FALSE
        self.assertEqual(model.get(1), False, "Variable 1 should be FALSE")
        self.assertEqual(model.get(3), False, "Variable 3 should be FALSE")
        
        # Verify trace was created
        self.assertTrue(
            os.path.exists(config.MASTER_TRACE_FILE),
            "Master trace file should be created"
        )
        print(f"  Trace: {config.MASTER_TRACE_FILE}")

    # =========================================================================
    # TEST 5: 6-Variable SAT with Deep Decision Levels (4+ DLs)
    # =========================================================================
    def test_sat_6var_deep(self):
        """
        Test a 6-variable SAT formula requiring 4+ decision levels:
        C1: (1 OR 2)
        C2: (-1 OR 3)
        C3: (-2 OR 4)
        C4: (-3 OR 5)
        C5: (-4 OR 6)
        C6: (-5 OR -6)
        
        Expected behavior:
        - DL 0: All 6 variables unassigned
        - DL 1: Decide 1=TRUE, propagates 3=TRUE
        - DL 2: Decide 5=TRUE, propagates 6=FALSE
        - DL 3: Decide 4=FALSE, satisfies C5
        - DL 4: Decide 2=FALSE, all clauses SAT!
        
        Expected result: SATISFIABLE with 1=TRUE, 2=FALSE, 3=TRUE, 4=FALSE, 5=TRUE, 6=FALSE
        """
        print("\n" + "="*60)
        print("TEST: 6-Variable SAT (4+ Decision Levels)")
        print("="*60)
        
        self._setup_test("sat_6var_deep")
        
        solver = DPLLSolver()
        success, model = solver.solve()
        
        # Assertions
        self.assertTrue(success, "Formula should be SATISFIABLE")
        self.assertIsNotNone(model, "Model should not be None for SAT")
        
        print(f"  Result: SAT")
        print(f"  Model: {model}")
        
        # Verify the model has the expected values
        # Expected: 1=TRUE, 2=FALSE, 3=TRUE, 4=FALSE, 5=TRUE, 6=FALSE
        self.assertEqual(model.get(1), True, "Variable 1 should be TRUE")
        self.assertEqual(model.get(2), False, "Variable 2 should be FALSE")
        self.assertEqual(model.get(3), True, "Variable 3 should be TRUE")
        self.assertEqual(model.get(4), False, "Variable 4 should be FALSE")
        self.assertEqual(model.get(5), True, "Variable 5 should be TRUE")
        self.assertEqual(model.get(6), False, "Variable 6 should be FALSE")
        
        # Verify trace was created
        self.assertTrue(
            os.path.exists(config.MASTER_TRACE_FILE),
            "Master trace file should be created"
        )
        print(f"  Trace: {config.MASTER_TRACE_FILE}")

    # =========================================================================
    # TEST 6: Conflict After DL1 (Conflict not at DL0, requires backtracking)
    # =========================================================================
    def test_conflict_after_dl1(self):
        """
        Test a formula where CONFLICT occurs after decision at DL1 (not at DL0):
        C1: (1 OR 2)
        C2: (-1 OR 3)
        C3: (-2 OR 3)
        C4: (-3 OR -1)
        
        Expected behavior:
        - DL 0: No unit clauses, all unassigned, CONTINUE
        - DL 1: Decide 1=TRUE -> propagates 3=TRUE via C2
                C4 (-3 OR -1) CONFLICTS since 3=TRUE and 1=TRUE
                Backtrack, try 1=FALSE -> C2, C4 satisfied
        - DL 2: Decide 2=TRUE -> C3 propagates 3=TRUE -> SAT
        
        Expected result: SATISFIABLE after conflict and backtracking at DL1
        """
        print("\n" + "="*60)
        print("TEST: Conflict After DL1 (Not at DL0)")
        print("="*60)
        
        self._setup_test("conflict_after_dl1")
        
        solver = DPLLSolver()
        success, model = solver.solve()
        
        # Assertions
        self.assertTrue(success, "Formula should be SATISFIABLE after backtracking")
        self.assertIsNotNone(model, "Model should not be None for SAT")
        
        print(f"  Result: SAT (after conflict at DL1 and backtrack)")
        print(f"  Model: {model}")
        
        # Verify the model has the expected values: 1=FALSE, 2=TRUE, 3=TRUE
        self.assertEqual(model.get(1), False, "Variable 1 should be FALSE")
        self.assertEqual(model.get(2), True, "Variable 2 should be TRUE")
        self.assertEqual(model.get(3), True, "Variable 3 should be TRUE")
        
        # Verify trace was created
        self.assertTrue(
            os.path.exists(config.MASTER_TRACE_FILE),
            "Master trace file should be created"
        )
        print(f"  Trace: {config.MASTER_TRACE_FILE}")

    # =========================================================================
    # TEST 7: UNSAT After DL2 (UNSAT not at DL0, discovered after exhausting branches)
    # =========================================================================
    def test_unsat_after_dl2(self):
        """
        Test a formula that is UNSAT but discovery requires exploring branches:
        C1: (1 OR 2)
        C2: (-1 OR -2)
        C3: (1 OR -2)
        C4: (-1 OR 2)
        
        Expected behavior:
        - DL 0: No unit clauses, all unassigned, CONTINUE
        - DL 1: Decide 1=TRUE -> C2 forces 2=FALSE
                C4 (-1 OR 2) CONFLICTS since 1=TRUE and 2=FALSE
                Backtrack, try 1=FALSE
        - DL 1: Decide 1=FALSE -> C3 forces 2=FALSE
                C1 (1 OR 2) CONFLICTS since 1=FALSE and 2=FALSE
                Both branches exhausted -> UNSAT
        
        Expected result: UNSATISFIABLE (discovered after DL1 exploration)
        """
        print("\n" + "="*60)
        print("TEST: UNSAT After DL2 (Not at DL0)")
        print("="*60)
        
        self._setup_test("unsat_after_dl2")
        
        solver = DPLLSolver()
        success, model = solver.solve()
        
        # Assertions
        self.assertFalse(success, "Formula should be UNSATISFIABLE")
        self.assertIsNone(model, "Model should be None for UNSAT")
        
        print(f"  Result: UNSAT (after exploring both branches)")
        print(f"  Model: {model}")
        
        # Verify trace was created
        self.assertTrue(
            os.path.exists(config.MASTER_TRACE_FILE),
            "Master trace file should be created for UNSAT"
        )
        print(f"  Trace: {config.MASTER_TRACE_FILE}")


class TestMOMHeuristic(unittest.TestCase):
    """Test cases for the MOM Heuristic"""
    
    def test_heuristic_returns_literal_with_polarity(self):
        """Test that the heuristic returns a literal (with sign), not just a variable"""
        print("\n" + "="*60)
        print("TEST: MOM Heuristic Polarity")
        print("="*60)
        
        # Create a temporary CNF file for testing
        test_cnf = os.path.join(config.DATA_DIR, "test_heuristic.cnf")
        with open(test_cnf, "w") as f:
            # Formula: (-1 OR -2) AND (-1 OR 2) -> -1 appears twice, 1 appears zero times
            f.write("p cnf 2 2\n")
            f.write("-1 -2 0\n")
            f.write("-1 2 0\n")
        
        heuristic = MOMHeuristic(test_cnf)
        
        # All variables unassigned
        assignments = {1: None, 2: None}
        
        chosen = heuristic.select_variable(assignments)
        
        print(f"  Chosen literal: {chosen}")
        
        # The heuristic should prefer -1 because it appears in both clauses
        self.assertEqual(chosen, -1, "Heuristic should return -1 (appears most frequently)")
        
        # Cleanup
        os.remove(test_cnf)
    
    def test_heuristic_selects_from_minimum_clauses(self):
        """Test that the heuristic focuses on minimum-sized clauses"""
        print("\n" + "="*60)
        print("TEST: MOM Heuristic Minimum Clause Focus")
        print("="*60)
        
        test_cnf = os.path.join(config.DATA_DIR, "test_heuristic2.cnf")
        with open(test_cnf, "w") as f:
            # Formula with different sized clauses
            # C1: (1 OR 2 OR 3) - size 3
            # C2: (-1 OR -2)    - size 2 (smaller!)
            # C3: (2 OR -3)     - size 2 (smaller!)
            f.write("p cnf 3 3\n")
            f.write("1 2 3 0\n")
            f.write("-1 -2 0\n")
            f.write("2 -3 0\n")
        
        heuristic = MOMHeuristic(test_cnf)
        
        # All variables unassigned
        assignments = {1: None, 2: None, 3: None}
        
        chosen = heuristic.select_variable(assignments)
        
        print(f"  Chosen literal: {chosen}")
        
        # The heuristic should choose from the size-2 clauses
        # -1 appears once, -2 appears once, 2 appears once, -3 appears once
        # Any of these from the minimum clauses is valid
        valid_choices = [-1, -2, 2, -3]
        self.assertIn(chosen, valid_choices, 
                      f"Heuristic should choose from minimum-sized clauses: {valid_choices}")
        
        # Cleanup
        os.remove(test_cnf)
    
    def test_heuristic_ignores_satisfied_clauses(self):
        """Test that the heuristic ignores satisfied clauses"""
        print("\n" + "="*60)
        print("TEST: MOM Heuristic Ignores Satisfied")
        print("="*60)
        
        test_cnf = os.path.join(config.DATA_DIR, "test_heuristic3.cnf")
        with open(test_cnf, "w") as f:
            # C1: (1 OR 2)  - will be satisfied by 1=TRUE
            # C2: (-1 OR 3) - becomes (-1 OR 3), effectively just 3
            f.write("p cnf 3 2\n")
            f.write("1 2 0\n")
            f.write("-1 3 0\n")
        
        heuristic = MOMHeuristic(test_cnf)
        
        # Variable 1 is assigned TRUE
        assignments = {1: True, 2: None, 3: None}
        
        chosen = heuristic.select_variable(assignments)
        
        print(f"  Chosen literal: {chosen}")
        
        # C1 is now satisfied (1=TRUE)
        # C2 has only 3 as unassigned literal (since -1 is falsified by 1=TRUE)
        # So the heuristic should choose 3
        self.assertEqual(chosen, 3, "Heuristic should choose 3 (only unassigned in unsatisfied clause)")
        
        # Cleanup
        os.remove(test_cnf)


def run_all_tests():
    """Run all test cases and display results"""
    print("\n" + "#"*70)
    print("# DPLL SAT SOLVER TEST SUITE")
    print("#"*70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDPLLSolver))
    suite.addTests(loader.loadTestsFromTestCase(TestMOMHeuristic))
    
    # Run with verbosity
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "#"*70)
    print("# TEST SUMMARY")
    print("#"*70)
    print(f"  Tests run: {result.testsRun}")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Success: {result.wasSuccessful()}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
