import json
import sys
import os
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# from weight_update import dynamic_weight_update
import numpy as np

# w=[0.35, 0.26, 0.15, 0.1, 0.12, 0.02]

def extract_weighs(weights_path):
    # 从文件中读取权重
    with open(weights_path, 'r') as file:
        json_data = json.load(file)
    weights = [
        json_data.get("w_conflict", 0),
        json_data.get("w_dosage", 0),
        json_data.get("w_duplication", 0),
        json_data.get("w_context", 0),
        json_data.get("w_physical", 0),
        json_data.get("w_coverage", 0)
    ]
    return weights

def extract_scores(json_data):
    scores = [
        json_data.get("Conflict_score", 0),
        json_data.get("Dosage_score", 0),
        json_data.get("Duplication_score", 0),
        json_data.get("Context_score", 0),
        json_data.get("Physical_score", 0),
        json_data.get("Coverage_score", 0)
    ]
    return scores

def dynamic_weight_update(w_t, scores, alpha=0.8, beta=0.05):
    # alpha (float): 平滑系数，越大越保留历史权重
    # beta (float): softmax温度因子，越大越敏感于得分差异
    w_t = np.array(w_t)
    s = np.array(scores)

    #  Softmax-based raw weights from scores
    raw_w = np.exp(beta * s)
    raw_w /= raw_w.sum()  # Normalize (Z)

    #  Exponential smoothing fusion
    w_t1 = alpha * w_t + (1 - alpha) * raw_w

    return w_t1.tolist()

def update_weights_file(weights_path, new_weights):
    weights_data = {
        "w_conflict": new_weights[0],
        "w_dosage": new_weights[1],
        "w_duplication": new_weights[2],
        "w_context": new_weights[3],
        "w_physical": new_weights[4],
        "w_coverage": new_weights[5]
    }
    with open(weights_path, 'w') as file:
        json.dump(weights_data, file, indent=4)
    print(f"[INFO] Updating weights to {weights_path}")

def calculate_safety_score(json_file_path, weights_array):
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
        "Conflict_score": weights_array[0],
        "Dosage_score": weights_array[1],
        "Duplication_score": weights_array[2],
        "Context_score": weights_array[3], 
        "Physical_score": weights_array[4],
        "Coverage_score": weights_array[5]
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
    json_score = json.load(open(json_path, 'r'))
    current_score = extract_scores(json_score)

    print("current score:", current_score)   

    weights_path = os.path.join(PROJECT_ROOT, "Safety_Checker/weights.json")
    current_weights = extract_weighs(weights_path)

    print("current weights:", current_weights)

    safety_score = calculate_safety_score(json_path, current_weights)

    w = dynamic_weight_update(current_weights, current_score)
    print(f"Updated Weights: {w}")
    update_weights_file(weights_path, w)
    print(f"Final Evaluation Score: {safety_score}")