import os
import subprocess

# 定义文件路径
CCM_DATASET_PATH = "../CCMDataset/L1"
PATIENT_INFO_CLEANER_SCRIPT = "Patient_Info_Cleaner/Patient_info_cleaner.py"
PRESCRIPTION_SCRIPT = "Prescription/prescription.py"
DRUG_INTERACTION_SCRIPT = "Drug_Interaction_Checker/drug_drug_interaction.py"

def run_patient_info_cleaner(patient_id):
    """
    运行 Patient_Info_Cleaner 脚本，处理患者信息。
    :param patient_id: 病人编号
    """
    input_file = os.path.join(CCM_DATASET_PATH, f"{patient_id}.txt")
    if not os.path.exists(input_file):
        print(f"[ERROR] 输入文件 {input_file} 不存在。")
        return False

    print(f"[INFO] 正在运行 Patient_Info_Cleaner，处理文件: {input_file}")
    try:
        subprocess.run(["python", PATIENT_INFO_CLEANER_SCRIPT, input_file], check=True)
        print(f"[INFO] Patient_Info_Cleaner 运行完成。")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] 运行 Patient_Info_Cleaner 时出错: {e}")
        return False

def run_prescription():
    """
    运行 Prescription 脚本，生成处方。
    """
    print(f"[INFO] 正在运行 Prescription 脚本...")
    try:
        subprocess.run(["python", PRESCRIPTION_SCRIPT], check=True)
        print(f"[INFO] Prescription 脚本运行完成。")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] 运行 Prescription 脚本时出错: {e}")
        return False

def run_drug_interaction_checker():
    """
    运行 Drug_Interaction_Checker 脚本，检查药物相互作用。
    """
    print(f"[INFO] 正在运行 Drug_Interaction_Checker 脚本...")
    try:
        subprocess.run(["python", DRUG_INTERACTION_SCRIPT], check=True)
        print(f"[INFO] Drug_Interaction_Checker 脚本运行完成。")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] 运行 Drug_Interaction_Checker 脚本时出错: {e}")
        return False

def main(patient_id):
    """
    主流程函数，按顺序运行所有步骤。
    :param patient_id: 病人编号
    """
    print(f"[INFO] 开始处理病人编号: {patient_id}")

    # Step 1: 运行 Patient_Info_Cleaner
    if not run_patient_info_cleaner(patient_id):
        print("[ERROR] Patient_Info_Cleaner 运行失败，流程终止。")
        return

    # Step 2: 运行 Prescription
    if not run_prescription():
        print("[ERROR] Prescription 脚本运行失败，流程终止。")
        return

    # Step 3: 运行 Drug_Interaction_Checker
    if not run_drug_interaction_checker():
        print("[ERROR] Drug_Interaction_Checker 脚本运行失败，流程终止。")
        return

    print(f"[INFO] 病人编号 {patient_id} 的流程全部完成。")

if __name__ == "__main__":
    # 示例病人编号
    patient_id = 1055
    main(patient_id)