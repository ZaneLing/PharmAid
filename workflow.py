import os
import json
from Safety_Checker.safety_score import calculate_safety_score
from Safety_Checker.safety_checker import run_safety_checker
from Patient_Info_Cleaner.patient_info_cleaner import patient_info_clean_process
from Prescription.prescription import run_prescription
from Drug_Drug_Interaction.drug_drug_detector import run_ddi
from Drug_Patient_Interaction.drug_patient_detector import run_dpi
from Retrospector.retrospector import run_retrospector

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))

def run_patient_info_cleaner(ds_path):
    print(f"[INFO] Processing: Patient_Info_Cleaner...")
    print(f"[INFO] Dataset Path: {ds_path}")
    try:
        patient_info_clean_process(ds_path)
        print(f"[INFO] Patient_Info_Cleaner Finish")
    except Exception as e:
        print(f"[ERROR] Patient_Info_Cleaner error: {e}")
        raise

def run_generate_prescription(patient_id):
    print(f"[INFO] Processing: Prescription , patient_id: {patient_id}")
    try:
        run_prescription(patient_id)
        print(f"[INFO] Prescription Finish.")
    except Exception as e:
        print(f"[ERROR] Generating Prescription Error: {e}")
        raise

def run_drug_interaction_checker(patient_id):
    print(f"[INFO] Processing Drug_Interaction_Checker : {patient_id}")
    try:
        run_ddi(patient_id)
        print(f"[INFO] Drug_Interaction_Checker Finish")
    except Exception as e:
        print(f"[ERROR] Running DDI Error: {e}")
        raise

def run_drug_patient_interaction_checker(patient_id):
    print(f"[INFO] Processing Drug_Patient_Interaction: {patient_id}")
    try:
        run_dpi(patient_id)
        print(f"[INFO] Drug_Patient_Interaction Finish.")
    except Exception as e:
        print(f"[ERROR] Running Drug_Patient_Interaction Error: {e}")
        raise

def run_safety_checker_process(patient_id):
    print(f"[INFO] Processing Safety_Checker: {patient_id}")
    try:
        run_safety_checker(patient_id)
        print(f"[INFO] Safety_Checker Finish.")
    except Exception as e:
        print(f"[ERROR] Running Safety_Checker Error: {e}")
        raise

def run_retrospection(patient_id):
    print(f"[INFO] Processing Retrospection: {patient_id}")
    try:
        run_retrospector(patient_id)
        print(f"[INFO] Retrospection Finish.")
    except Exception as e:
        print(f"[ERROR] Runing Retrospection Error: {e}")
        raise

def extract_drug_names(input_json):
    prescriptions = input_json.get("Prescription", [])
    drug_list = [item.get("DrugName") for item in prescriptions if "DrugName" in item]
    return {"DrugName": drug_list}

def main():
    print(f"[INFO] Start Workflow...")
   
    dataset_path = os.path.join(PROJECT_ROOT, "CCMDataset/CCMD")
    patient_folders = [f for f in os.listdir(dataset_path) if os.path.isdir(os.path.join(dataset_path, f))]

    for patient_id in patient_folders:
        try:
            patient_id = int(patient_id)  # 确保 patient_id 是整数

            output_patient_folder = os.path.join(PROJECT_ROOT, f"Blackboard/Contents/{patient_id}")
            os.makedirs(output_patient_folder, exist_ok=True)

            print(f"[INFO] Processing Patient_Info_Cleaner 函数...")
            #run_patient_info_cleaner(dataset_path)

            patient_prescription_score = 0
            while patient_prescription_score < 85:
                print(f"[INFO] Score: {patient_prescription_score}, start iteration...")
                try:
                    run_prescription(patient_id)

                    run_drug_interaction_checker(patient_id)

                    run_drug_patient_interaction_checker(patient_id)

                    run_safety_checker(patient_id)

                    safety_score_file = os.path.join(PROJECT_ROOT, f"Blackboard/Contents/{patient_id}/Safety_Check/safety_check.json")
                    patient_prescription_score = calculate_safety_score(safety_score_file)
                    print(f"[INFO] Score: {patient_prescription_score}")
                except RuntimeError as e:
                    print(f"[ERROR] error: {e}")
                    print(f"[INFO] Pass {patient_id} iteration.")
                    break 

            else:
                print(f"[INFO] Score: {patient_prescription_score}, Safe.")    

                prescription_file = os.path.join(PROJECT_ROOT, f"Blackboard/Contents/{patient_id}/Prescription/Prescription.json")
                with open(prescription_file, "r") as f:
                    prescription_data = json.load(f)
                drug_names = extract_drug_names(prescription_data)
                # 将药物名称保存到 JSON 文件
                output_file = os.path.join(PROJECT_ROOT, f"Blackboard/Contents/{patient_id}/Prescription/output_drugname.json")
                with open(output_file, "w") as f:
                    json.dump(drug_names, f)

                print(f"[INFO] DrugNames: {drug_names}")

                print(f"[INFO] Iteration over.")

                print(f"[INFO] Start retrospection...")
                run_retrospection(patient_id)
                print(f"[INFO] Retrospection Finish.")
        except ValueError:
            print(f"[ERROR] Invalid patient ID: {patient_id}, pass.")    
            continue
        except Exception as e:
            print(f"[ERROR] Pass {patient_id} error: {e}")
            print(f"[INFO] Pass {patient_id}。")
            continue

    print("----------Over----------")

if __name__ == "__main__":
    main()