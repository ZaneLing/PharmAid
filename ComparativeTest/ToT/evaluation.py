#!/usr/bin/env python3
import json
import os,sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def load_rxcuis(path):
    """从 JSON 文件中读取 RxCUI 列表，去重后返回集合。"""
    with open(path, 'r', encoding='utf-8') as f:
        lst = json.load(f)
    return set(lst)

def precision_recall_f1(truth_set, pred_set):
    """计算并返回 (precision, recall, f1)."""
    tp = len(truth_set & pred_set)
    fp = len(pred_set - truth_set)
    fn = len(truth_set - pred_set)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1        = (2 * precision * recall / (precision + recall)
                 if (precision + recall) > 0 else 0.0)
    return precision, recall, f1

def main(id):
    # 文件路径
    patient_id = str(id)

    truth_path = os.path.join(PROJECT_ROOT, f"ComparativeTest/Single_Agent/evaluation/{patient_id}/hospital_rxcuis.json")
    pred_path  = os.path.join(PROJECT_ROOT, f"ComparativeTest/Single_Agent/evaluation/{patient_id}/output_rxcuis.json")

    # 加载并去重
    truth = load_rxcuis(truth_path)
    pred  = load_rxcuis(pred_path)

    # 计算
    precision, recall, f1 = precision_recall_f1(truth, pred)

    # 输出结果
    print(f"True Positives (TP): {len(truth & pred)}")
    print(f"False Positives (FP): {len(pred - truth)}")
    print(f"False Negatives (FN): {len(truth - pred)}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1 Score:  {f1:.4f}")

    # 将结果存储到 JSON 文件
    output_path = os.path.join(PROJECT_ROOT, f"ComparativeTest/Single_Agent/evaluation/{patient_id}/metrics.json")
    metrics = {
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "true_positives": len(truth & pred),
        "false_positives": len(pred - truth),
        "false_negatives": len(truth - pred)
    }
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("[Error] 请提供参数")
        sys.exit(1)

    patient_id = sys.argv[1]

    main(patient_id)
