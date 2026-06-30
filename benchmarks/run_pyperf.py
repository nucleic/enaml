# --------------------------------------------------------------------------------------
# Copyright (c) 2013-2025, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# --------------------------------------------------------------------------------------
"""Benchmark runner dispatcher for enaml extensions using pyperf.

Runs performance benchmarks for enaml extensions migrated to PyO3.

Usage:
    python benchmarks/run_pyperf.py --list                    # List all families
    python benchmarks/run_pyperf.py --family object_creation  # Run a family
"""
import argparse
import subprocess
import sys
from pathlib import Path

# Available benchmark families
BENCHMARK_FAMILIES = {
    'object_creation': 'object_creation.py',
    'attribute_access': 'attribute_access.py',
}


def list_families():
    """List available benchmark families."""
    print("Available benchmark families:")
    print()
    for name in sorted(BENCHMARK_FAMILIES.keys()):
        print(f"  {name}")
    print()


def run_family(family_name, pyperf_args):
    """Run a benchmark family using pyperf."""
    script = BENCHMARK_FAMILIES.get(family_name)
    if not script:
        print(f"Error: Unknown family '{family_name}'")
        return 1
    
    script_path = Path(__file__).parent / script
    if not script_path.exists():
        print(f"Error: Benchmark script not found: {script_path}")
        return 1
    
    # Run the benchmark script with pyperf arguments
    cmd = [sys.executable, str(script_path)] + pyperf_args
    result = subprocess.run(cmd)
    return result.returncode


def main():
    # Check for --list before argument parsing to avoid pyperf handling it
    if '--list' in sys.argv:
        list_families()
        return 0
    
    # Extract --family before creating parser
    family = None
    family_idx = -1
    for i, arg in enumerate(sys.argv[1:]):
        if arg == '--family':
            family_idx = i + 1
            if i + 2 < len(sys.argv):
                family = sys.argv[i + 2]
            break
    
    if family_idx >= 0 and family:
        # Remove --family and its value from sys.argv
        del sys.argv[family_idx:family_idx + 2]
        # Run the family and pass remaining arguments to pyperf
        return run_family(family, sys.argv[1:])
    
    if family_idx >= 0:
        print("Error: --family requires an argument")
        print("Usage: python run_pyperf.py --family <name>")
        return 1
    
    print("Error: --family argument required. Use --list to see families.")
    print("Usage: python run_pyperf.py --family <name>")
    return 1


if __name__ == '__main__':
    sys.exit(main())
