"""Regenerate every book figure by running each script in figures/scripts/.

    python scripts/build-figures.py            # all figures
    python scripts/build-figures.py ch05 ch12  # selected scripts

Requires numpy, scipy and matplotlib.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "figures" / "scripts"


def main(names):
    scripts = sorted(p for p in SCRIPTS.glob("*.py") if p.stem != "figstyle")
    if names:
        scripts = [p for p in scripts if p.stem in names]
    failed = []
    for script in scripts:
        print(f"== {script.name}")
        if subprocess.run([sys.executable, str(script)], cwd=ROOT).returncode:
            failed.append(script.name)
    if failed:
        sys.exit(f"Failed: {', '.join(failed)}")


if __name__ == "__main__":
    main(sys.argv[1:])
