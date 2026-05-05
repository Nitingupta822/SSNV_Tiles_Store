
import sys
import os
sys.path.insert(0, os.getcwd()) # Normal behavior
try:
    from test_pkg import hello
    print("Import success:", hello())
except ImportError as e:
    print("Import failed:", e)
