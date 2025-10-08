#!/usr/bin/env python3
"""Test script to debug import issues"""

import sys
import traceback

try:
    print("Starting import...")
    sys.path.insert(0, r"i:\CODE\tts-2\scripts")
    import generate_questions_and_answers
    print("Import successful!")
except Exception as e:
    print(f"ERROR: {e}")
    print()
    traceback.print_exc()
