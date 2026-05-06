"""
Root conftest for the tests/ directory.

Re-exports the shared Issue factory so all test modules can import from a
single well-known location.
"""
import sys
import os

# Allow `from tests.backend.unit.conftest import make_issue` style imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
