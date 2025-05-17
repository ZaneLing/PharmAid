#!/usr/bin/env python3
import subprocess
import sys

def run_step(script_name, patient_id):
    """
    Run a Python script with the given patient_id argument.
    Raises CalledProcessError on non-zero exit.
    """
    print(f"==> Running {script_name} for patient {patient_id} ...")
    subprocess.run(
        [sys.executable, script_name, patient_id],
        check=True
    )

def main():
    if len(sys.argv) != 2:
        print("Usage: python workflow.py <patient_id>")
        sys.exit(1)

    patient_id = sys.argv[1]

    try:
        # 1. Single-agent step
        run_step("single_agent.py", patient_id)

        # 2. Hospital prescription generation
        run_step("hospital_pres.py", patient_id)

        # 3. Final output prescription formatting
        run_step("output_pres.py", patient_id)

        run_step("evaluation.py", patient_id)

        print("All steps completed successfully.")

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}. Workflow aborted.")
        sys.exit(e.returncode)

if __name__ == "__main__":
    main()


