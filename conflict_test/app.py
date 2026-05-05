
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))
try:
    from app import create_app
    print("Success:", create_app())
except Exception as e:
    print("Failed:", type(e).__name__, ":", e)
