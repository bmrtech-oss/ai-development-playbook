import subprocess
import sys

"""Run a promptfoo evaluation from this minimal template."""

if __name__ == "__main__":
    print("Starting promptfoo evaluation...")

    command = [
        sys.executable,
        "-m",
        "promptfoo",
        "run",
        "promptfooconfig.yaml",
    ]

    result = subprocess.run(command, capture_output=True, text=True)
    print(result.stdout)

    if result.returncode != 0:
        print("Evaluation failed.")
        print(result.stderr)
        sys.exit(result.returncode)

    print("Evaluation completed successfully.")
