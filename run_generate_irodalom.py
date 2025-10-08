#!/usr/bin/env python3
"""
Wrapper script to run generate_questions_and_answers.py with proper path priority
"""

# MUST DO THIS BEFORE ANY OTHER IMPORTS!
import sys

# Reorder sys.path to prioritize conda site-packages over user site-packages
user_site = r"C:\Users\szolzol\AppData\Roaming\Python\Python311\site-packages"
conda_site = r"I:\CODE\tts-2\.conda\Lib\site-packages"

if user_site in sys.path:
    sys.path.remove(user_site)
if conda_site in sys.path:
    sys.path.remove(conda_site)

# Add them back in the correct order: conda first, user last
sys.path.insert(0, conda_site)
sys.path.append(user_site)

print(f"✅ Path priority fixed - conda packages will be used first")
print()

# Now safe to import everything else
import os
os.chdir(r"i:\CODE\tts-2")

# Run the original script by executing its main function
sys.argv = ["generate_questions_and_answers.py", "4", "2"]
sys.path.insert(0, r"i:\CODE\tts-2\scripts")

# Import and run
try:
    print("Importing generate_questions_and_answers...")
    from generate_questions_and_answers import main
    print("✅ Import successful")
    print()
    print("Running main()...")
    main()
    print("✅ main() completed")
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
