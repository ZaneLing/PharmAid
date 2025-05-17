#!/usr/bin/env python3
import os
import subprocess
import sys

def run_workflow(patient_id):
    """
    Run the workflow for a single patient_id.
    """
    try:
        print(f"--- Processing patient: {patient_id} ---")
        subprocess.run([sys.executable, "eva_flow.py", patient_id], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error processing {patient_id}: exit code {e.returncode}")
        # optionally: log error, continue or abort
        # raise

def main(dataset_dir):
    """
    Iterate over each folder in dataset_dir (each folder name is a patient_id),
    and invoke workflow.py patient_id for each.
    """
    # List all entries in the dataset directory
    entries = sorted(os.listdir(dataset_dir))
    for name in entries:
        full_path = os.path.join(dataset_dir, name)
        # Only directories whose name looks like a patient_id
        if os.path.isdir(full_path):
            patient_id = name
            run_workflow(patient_id)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python run_all_workflows.py <dataset_directory>")
        sys.exit(1)
    dataset_directory = sys.argv[1]
    main(dataset_directory)
