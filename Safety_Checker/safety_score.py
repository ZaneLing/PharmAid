import json
import sys
import os
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# from weight_update import dynamic_weight_update
w = [0.35, 0.26, 0.15, 0.1, 0.12, 0.02]

def calculate_safety_score(json_file_path):
    # 读取JSON文件
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    
    # 提取六个分数
    conflict_score = data["Conflict_score"]
    dosage_score = data["Dosage_score"]
    duplication_score = data["Duplication_score"]
    context_score = data["Context_score"]
    physical_score = data["Physical_score"]
    coverage_score = data["Coverage_score"]
    
    # 按照权重计算总分
    weights = {
        "Conflict_score": w[0],
        "Dosage_score": w[1],
        "Duplication_score": w[2],
        "Context_score": w[3], 
        "Physical_score": w[4],
        "Coverage_score": w[5]
    }
    
    total_score = (
        conflict_score * weights["Conflict_score"] +
        dosage_score * weights["Dosage_score"] +
        duplication_score * weights["Duplication_score"] +
        context_score * weights["Context_score"] +
        physical_score * weights["Physical_score"] +
        coverage_score * weights["Coverage_score"]
    )
    
    return total_score

if __name__ == "__main__":
    json_path = os.path.join(PROJECT_ROOT, "output/prescription_safety_evaluation.json")
    safety_score = calculate_safety_score(json_path)
    print(f"Final Evaluation Score: {safety_score}")