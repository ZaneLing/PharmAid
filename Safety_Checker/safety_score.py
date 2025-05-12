import json
import sys
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
        "Conflict_score": 0.3,
        "Dosage_score": 0.2,
        "Duplication_score": 0.2,
        "Context_score": 0.1,
        "Physical_score": 0.1,
        "Coverage_score": 0.1
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
    json_path = "./output/prescription_safety_evaluation.json"
    safety_score = calculate_safety_score(json_path)
    print(f"总安全评估分数: {safety_score}")