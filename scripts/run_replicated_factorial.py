#!/usr/bin/env python3
"""scripts/run_replicated_factorial.py: Unified runner for replicated factorial study.

Delegates execution directly to factorial/run_replicates.py (empirical trial execution)
and factorial/analyze_factorial.py (Yates algorithm and ANOVA analysis).
"""

import os
import sys

# Ensure repository root is on path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from factorial.run_replicates import main as run_replicates_main
from factorial.analyze_factorial import main as analyze_factorial_main


def main():
    print("=" * 80)
    print("EXECUTING EMPIRICAL FACTORIAL REPLICATES RUNTIME (CognitiveKernel)")
    print("=" * 80)
    run_replicates_main()

    print("\n" + "=" * 80)
    print("EXECUTING FACTORIAL STATISTICAL ANALYSIS & YATES ANOVA")
    print("=" * 80)
    analyze_factorial_main()


if __name__ == "__main__":
    main()
