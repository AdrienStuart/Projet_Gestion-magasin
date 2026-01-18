
import sys
import os

print("Checking environment...")

# 1. Check Python Version
print(f"Python: {sys.version}")

# 2. Check PySide6
try:
    import PySide6
    print(f"PySide6 verified: {PySide6.__version__}")
except ImportError:
    print("ERROR: PySide6 not installed.")

# 3. Check qtawesome
try:
    import qtawesome
    print("qtawesome verified.")
except ImportError:
    print("ERROR: qtawesome not installed.")

# 4. Check Database imports
try:
    # Hack path to find 'gestion_magasin_qt' and 'db'
    base_dir = os.path.dirname(os.path.abspath(__file__)) # inside gestion_magasin_qt usually if run there
    if "gestion_magasin_qt" in base_dir:
        # We are probably in the subdir
        sys.path.append(os.path.join(base_dir, ".."))
    
    from gestion_magasin_qt.database import Database
    print("Database module importable.")
except Exception as e:
    print(f"ERROR: Could not import Database module: {e}")

print("Verification complete.")
