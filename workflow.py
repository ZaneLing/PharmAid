import os
import json
from Safety_Checker.safety_score import calculate_safety_score
from Safety_Checker.safety_checker import run_safery_checker
from Patient_Info_Cleaner.Patient_info_cleaner import clean_patient_info
from Prescription.prescription import generate_prescription
from Drug_Drug_Interaction.drug_drug_detector import check_drug_interaction
from Drug_Patient_Interaction.drug_patient_detector import check_drug_patient_interaction
from Retrospector.retrospector import retrospection

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))

def run_patient_info_cleaner(ds_path):
    print(f"[INFO] 正在运行 Patient_Info_Cleaner 函数...")
    print(f"[INFO] 数据集路径: {ds_path}")
    try:
        clean_patient_info(ds_path)
        print(f"[INFO] Patient_Info_Cleaner 函数运行完成。")
    except Exception as e:
        print(f"[ERROR] 运行 Patient_Info_Cleaner 函数时出错: {e}")
        raise

def run_prescription(patient_id):
    print(f"[INFO] 正在运行 Prescription 函数，处理病人编号: {patient_id}")
    try:
        generate_prescription(patient_id)
        print(f"[INFO] Prescription 函数运行完成。")
    except Exception as e:
        print(f"[ERROR] 运行 Prescription 函数时出错: {e}")
        raise

def run_drug_interaction_checker(patient_id):
    print(f"[INFO] 正在运行 Drug_Interaction_Checker 函数，处理病人编号: {patient_id}")
    try:
        check_drug_interaction(patient_id)
        print(f"[INFO] Drug_Interaction_Checker 函数运行完成。")
    except Exception as e:
        print(f"[ERROR] 运行 Drug_Interaction_Checker 函数时出错: {e}")
        raise

def run_drug_patient_interaction_checker(patient_id):
    print(f"[INFO] 正在运行 Drug_Patient_Interaction 函数，处理病人编号: {patient_id}")
    try:
        check_drug_patient_interaction(patient_id)
        print(f"[INFO] Drug_Patient_Interaction 函数运行完成。")
    except Exception as e:
        print(f"[ERROR] 运行 Drug_Patient_Interaction 函数时出错: {e}")
        raise

def run_safety_checker(patient_id):
    print(f"[INFO] 正在运行 Safety_Checker 函数，处理病人编号: {patient_id}")
    try:
        safety_checker(patient_id)
        print(f"[INFO] Safety_Checker 函数运行完成。")
    except Exception as e:
        print(f"[ERROR] 运行 Safety_Checker 函数时出错: {e}")
        raise

def run_retrospection(patient_id):
    print(f"[INFO] 正在运行 Retrospection 函数，处理病人编号: {patient_id}")
    try:
        retrospection(patient_id)
        print(f"[INFO] Retrospection 函数运行完成。")
    except Exception as e:
        print(f"[ERROR] 运行 Retrospection 函数时出错: {e}")
        raise

def extract_drug_names(input_json):
    """
    从 input_json 中提取所有 Prescription 条目的 DrugName，
    返回一个 {"DrugName": [...]} 结构。
    """
    prescriptions = input_json.get("Prescription", [])
    drug_list = [item.get("DrugName") for item in prescriptions if "DrugName" in item]
    return {"DrugName": drug_list}

def main():
    print(f"[INFO] 开始工作流...")
   
    dataset_path = os.path.join(PROJECT_ROOT, "CCMDataset/CCMD")
    patient_folders = [f for f in os.listdir(dataset_path) if os.path.isdir(os.path.join(dataset_path, f))]

    for patient_id in patient_folders:
        try:
            patient_id = int(patient_id)  # 确保 patient_id 是整数

            output_patient_folder = os.path.join(PROJECT_ROOT, f"Blackboard/Contents/{patient_id}")
            os.makedirs(output_patient_folder, exist_ok=True)

            print(f"[INFO] 运行 Patient_Info_Cleaner 函数...")
            run_patient_info_cleaner(dataset_path)

            patient_prescription_score = 0
            while patient_prescription_score < 85:
                print(f"[INFO] 当前评分: {patient_prescription_score}，继续迭代...")
                try:
                    run_prescription(patient_id)

                    run_drug_interaction_checker(patient_id)

                    run_drug_patient_interaction_checker(patient_id)

                    run_safety_checker(patient_id)

                    safety_score_file = os.path.join(PROJECT_ROOT, f"Blackboard/Contents/{patient_id}/Safety_Check/safety_check.json")
                    patient_prescription_score = calculate_safety_score(safety_score_file)
                    print(f"[INFO] 当前评分: {patient_prescription_score}")
                except RuntimeError as e:
                    print(f"[ERROR] 子流程失败: {e}")
                    print(f"[INFO] 跳过病人 {patient_id} 的当前迭代。")
                    break 

            else:
                print(f"[INFO] 处方评分: {patient_prescription_score}，迭代结束。")    

                prescription_file = os.path.join(PROJECT_ROOT, f"Blackboard/Contents/{patient_id}/Prescription/Prescription.json")
                with open(prescription_file, "r") as f:
                    prescription_data = json.load(f)
                drug_names = extract_drug_names(prescription_data)
                # 将药物名称保存到 JSON 文件
                output_file = os.path.join(PROJECT_ROOT, f"Blackboard/Contents/{patient_id}/Prescription/output_drugname.json")
                with open(output_file, "w") as f:
                    json.dump(drug_names, f)

                print(f"[INFO] 药物名称: {drug_names}")

                print(f"[INFO] 迭代结束。")

                print(f"[INFO] 开始回顾分析...")
                run_retrospection(patient_id)
                print(f"[INFO] 回顾分析完成。")
        except ValueError:
            print(f"[ERROR] 无效的病人编号: {patient_id}，跳过该病人。")    
            continue
        except Exception as e:
            print(f"[ERROR] 处理病人 {patient_id} 时发生错误: {e}")
            print(f"[INFO] 跳过病人 {patient_id}。")
            continue

    print("----------工作流结束----------")

if __name__ == "__main__":
    main()