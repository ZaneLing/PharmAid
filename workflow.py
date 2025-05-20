import os, json
import subprocess

from Safety_Checker.safety_score import calculate_safety_score

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))

# # 定义文件路径
# CCM_DATASET = "CCMDataset/L1"
# CCM_DATASET_PATH = os.path.join(PROJECT_ROOT, CCM_DATASET)

# 定义各脚本的路径

SAFETY_CHECKER_SCRIPT = os.path.join(PROJECT_ROOT, "Safety_Checker/safety_checker.py")
SAFETY_SCORE_SCRIPT = os.path.join(PROJECT_ROOT, "Safety_Checker/safety_score.py")
PATIENT_INFO_CLEANER_SCRIPT = os.path.join(PROJECT_ROOT, "Patient_Info_Cleaner/Patient_info_cleaner.py")
PRESCRIPTION_SCRIPT = os.path.join(PROJECT_ROOT, "Prescription/prescription.py")
DRUG_DRUG_INTERACTION_SCRIPT = os.path.join(PROJECT_ROOT, "Drug_Drug_Interaction/drug_drug_detector.py")
DRUG_PATIENT_INTERACTION_SCRIPT = os.path.join(PROJECT_ROOT, "Drug_Patient_Interaction/drug_patient_detector.py")
RETROSPECTION_SCRIPT = os.path.join(PROJECT_ROOT, "Retrospector/retrospector.py")

# SAFETY_SCORE_SCRIPT = "./Safety_Checker/safety_score.py" 
# PATIENT_INFO_CLEANER_SCRIPT = "./Patient_Info_Cleaner/Patient_info_cleaner.py"  # 替换为实际路径
# PRESCRIPTION_SCRIPT = "./Prescription/prescription.py"  # 替换为实际路径
# DRUG_DRUG_INTERACTION_SCRIPT = "./Drug_Drug_Interaction/drug_drug_detector.py"  # 替换为实际路径
# DRUG_PATIENT_INTERACTION_SCRIPT = "./Drug_Patient_Interaction/drug_patient_detector.py"  # 替换为实际路径
# RETROSPECTION_SCRIPT = "./Retrospector/retrospector.py"  


def run_patient_info_cleaner(ds_path):
    print(f"[INFO] 正在运行 Patient_Info_Cleaner 脚本...")
    print(f"[INFO] Project Path: {PROJECT_ROOT}")
    print(f"[INFO] 数据集路径: {ds_path}")
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
    print(f"[INFO] 正在运行 Drug_Patient_Interaction 脚本，处理病人编号: {patient_id}")
    try:
        subprocess.run(["python", DRUG_PATIENT_INTERACTION_SCRIPT, str(patient_id)], check=True)
        print(f"[INFO] Drug_Patient_Interaction 脚本运行完成。")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] 运行 Drug_Patient_Interaction 脚本时出错: {e}")
        raise
    
def run_safety_checker(patient_id):
    print(f"[INFO] 正在运行 Safety_Checker 脚本，处理病人编号: {patient_id}")
    try:
        subprocess.run(["python", SAFETY_CHECKER_SCRIPT, str(patient_id)], check=True)
        print(f"[INFO] Safety_Checker 脚本运行完成。")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] 运行 Safety_Checker 脚本时出错: {e}")
        raise

def run_safety_score(patient_id):
    print(f"[INFO] 正在运行 Safety_Score 脚本，处理病人编号: {patient_id}")
    try:
        result = subprocess.run(
            ["python", SAFETY_SCORE_SCRIPT, str(patient_id)],
            check=True,
            capture_output=True,
            text=True
        )
        score = float(result.stdout.strip())  # 假设脚本输出分数在标准输出中
        print(f"[INFO] Safety_Score 脚本运行完成，分数: {score}")
        return score
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] 运行 Safety_Score 脚本时出错: {e}")
        raise
    except ValueError as e:
        print(f"[ERROR] 无法解析 Safety_Score 脚本输出的分数: {e}")
        raise


def extract_drug_names(input_json):
    """
    从 input_json 中提取所有 Prescription 条目的 DrugName，
    返回一个 {"DrugName": [...]} 结构。
    """
    prescriptions = input_json.get("Prescription", [])
    drug_list = [item.get("DrugName") for item in prescriptions if "DrugName" in item]
    return {"DrugName": drug_list}

def run_retrospection(patient_id):
    print(f"[INFO]  {patient_id}")
    try:
        subprocess.run(["python", RETROSPECTION_SCRIPT, str(patient_id)], check=True)
        print(f"[INFO] Retrospection over。")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Retrospection error: {e}")
        raise

def main():
    print(f"[INFO] Set OpenAi Key...")
    print(f"[INFO] Start...")
    print(f"[INFO] Set retro guidance database...")
   
    dataset_path = os.path.join(PROJECT_ROOT, "CCMDataset/CCMD")
    patient_folders = [f for f in os.listdir(dataset_path) if os.path.isdir(os.path.join(dataset_path, f))]

    for patient_id in patient_folders:
        try:
            patient_id = int(patient_id)  # 确保 patient_id 是整数

            output_patient_folder = os.path.join(PROJECT_ROOT, f"Blackboard/Contents/{patient_id}")
            os.makedirs(output_patient_folder, exist_ok=True)

            print(f"[INFO] Patient_Info_Cleaner ...")
            print(f"[INFO] ds Path: {dataset_path}")
            

            patient_prescription_score = 0
            while patient_prescription_score < 85:
                print(f"[INFO] score: {patient_prescription_score}，iteration continue。")
                try:
                    run_prescription(patient_id)

                    run_drug_interaction_checker(patient_id)

                    run_drug_patient_interaction_checker(patient_id)

                    run_safety_checker(patient_id)

                    safety_score_file = os.path.join(PROJECT_ROOT, f"Blackboard/Contents/{patient_id}/Safety_Check/safety_check.json")
                    patient_prescription_score = calculate_safety_score(safety_score_file)
                    print(f"[INFO] Score: {patient_prescription_score}")
                except RuntimeError as e:
                    print(f"[ERROR] sub-process fail: {e}")
                    print(f"[INFO] Pass {patient_id} iteration")
                    break 

            else:
                print(f"[INFO] Prescription score: {patient_prescription_score}，iteration over。")    

                prescription_file = os.path.join(PROJECT_ROOT, f"Blackboard/Contents/{patient_id}/Prescription/Prescription.json")
                with open(prescription_file, "r") as f:
                    prescription_data = json.load(f)
                drug_names = extract_drug_names(prescription_data)
                # 将药物名称保存到 JSON 文件
                output_file = os.path.join(PROJECT_ROOT, f"Blackboard/Contents/{patient_id}/Prescription/output_drugname.json")
                with open(output_file, "w") as f:
                    json.dump(drug_names, f)

                print(f"[INFO] Drug names: {drug_names}")

                print(f"[INFO] Over Iteration.")

                print(f"[INFO] Retrospection start...")
                #run_retrospection(patient_id)
                print(f"[INFO] Retrospection over.")
        except ValueError:
            print(f"[ERROR] invalid {patient_id} patient")    
            continue
        except Exception as e:
            print(f"[ERROR]  {patient_id} error: {e}")
            print(f"[INFO] Pass {patient_id}。")
            continue

    print("----------Over---------")

if __name__ == "__main__":
    main()