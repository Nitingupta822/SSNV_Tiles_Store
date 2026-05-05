import sys
import os

# Add the project root and backend to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'backend'))

# Import from the 'app' package inside 'backend'
# We use a slightly different name or ensure the path is correct
try:
    from app import create_app
except ImportError:
    # Fallback if the above fails due to conflict
    from backend.app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
