import os
import subprocess

# 定义文件路径
CCM_DATASET_PATH = "./CCMDataset/L1"

# 定义各脚本的路径
PATIENT_INFO_CLEANER_SCRIPT = "./Patient_Info_Cleaner/Patient_info_cleaner.py"  # 替换为实际路径
PRESCRIPTION_SCRIPT = "./Prescription/prescription.py"  # 替换为实际路径
DRUG_DRUG_INTERACTION_SCRIPT = "./Drug_Drug_Interaction/drug_drug_detector.py"  # 替换为实际路径
DRUG_PATIENT_INTERACTION_SCRIPT = "./Drug_Patient_Interaction/drug_patient_detector.py"  # 替换为实际路径

def run_patient_info_cleaner(ds_path):
    """
    运行 Patient_Info_Cleaner 脚本，处理患者信息。
    """
    print(f"[INFO] 正在运行 Patient_Info_Cleaner 脚本...")
    try:
        subprocess.run(["python", PATIENT_INFO_CLEANER_SCRIPT, ds_path], check=True)
        print(f"[INFO] Patient_Info_Cleaner 脚本运行完成。")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] 运行 Patient_Info_Cleaner 脚本时出错: {e}")
        raise

def run_prescription(patient_id):
    """
    运行 Prescription 脚本，生成处方。
    :param patient_id: 病人编号
    """
    print(f"[INFO] 正在运行 Prescription 脚本，处理病人编号: {patient_id}")
    try:
        subprocess.run(["python", PRESCRIPTION_SCRIPT, str(patient_id)], check=True)
        print(f"[INFO] Prescription 脚本运行完成。")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] 运行 Prescription 脚本时出错: {e}")
        raise

def run_drug_interaction_checker(patient_id):
    """
    运行 Drug_Interaction_Checker 脚本，检查药物相互作用。
    :param patient_id: 病人编号
    """
    print(f"[INFO] 正在运行 Drug_Interaction_Checker 脚本，处理病人编号: {patient_id}")
    try:
        subprocess.run(["python", DRUG_DRUG_INTERACTION_SCRIPT, str(patient_id)], check=True)
        print(f"[INFO] Drug_Interaction_Checker 脚本运行完成。")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] 运行 Drug_Interaction_Checker 脚本时出错: {e}")
        raise

def run_drug_patient_interaction_checker(patient_id):
    """
    运行 Drug_Patient_Interaction 脚本，检查药物与患者的交互。
    :param patient_id: 病人编号
    """
    print(f"[INFO] 正在运行 Drug_Patient_Interaction 脚本，处理病人编号: {patient_id}")
    try:
        subprocess.run(["python", DRUG_PATIENT_INTERACTION_SCRIPT, str(patient_id)], check=True)
        print(f"[INFO] Drug_Patient_Interaction 脚本运行完成。")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] 运行 Drug_Patient_Interaction 脚本时出错: {e}")
        raise

def main():
    """
    主流程函数，按顺序运行所有步骤。
    """
    print(f"[INFO] 开始执行工作流...")
    patient_id = 1057  # 示例病人编号
    output_patient_folder = f"./BlackBoard/Contents/{patient_id}"
    os.makedirs(output_patient_folder, exist_ok=True)
    # Step 1: 运行 Patient_Info_Cleaner
    run_patient_info_cleaner(CCM_DATASET_PATH)

    # Step 3: 运行 Prescription
    run_prescription(patient_id)

    # Step 4: 运行 Drug_Interaction_Checker
    run_drug_interaction_checker(patient_id)

    # Step 5: 运行 Drug_Patient_Interaction
    run_drug_patient_interaction_checker(patient_id)

    print(f"[INFO] 工作流执行完成。")

if __name__ == "__main__":
    main()