import json
import requests
import re, sys
import os

# RxNorm API endpoint
RXNORM_BASE_URL = "https://rxnav.nlm.nih.gov/REST/rxcui.json?name="
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def extract_drugs_by_subject(input_json, target_id):
    prescriptions = input_json.get("Prescription", [])
    result = []
    for entry in prescriptions:
        if entry.get("subject_id") == target_id:
            drugs = entry.get("drugs", [])
            result.extend(drugs)
    return result

def get_rxcui(drug_name):
    """Query RxNorm API to get the RxCUI for a drug name."""
    resp = requests.get(RXNORM_BASE_URL + drug_name)
    if resp.status_code == 200:
        data = resp.json()
        ids = data.get("idGroup", {}).get("rxnormId", [])
        return ids[0] if ids else None
    return None

def convert_drugs_to_rxcui_list(input_json_path):
    """Load JSON and return a list of RxCUI codes corresponding to DrugName."""
    with open(input_json_path, "r") as f:
        drug_data = json.load(f)

    rxcui_list = []
    for name in drug_data.get("DrugName", []):
        rxcui = get_rxcui(name)
        rxcui_list.append(rxcui)

    return rxcui_list

def clean_drug_name(name):
    match = re.match(r'^([A-Za-z]+)', name)
    return match.group(1).lower() if match else ''

def clean_drug_json(input_json):
    original_list = input_json.get("DrugName", [])
    cleaned_list = [clean_drug_name(drug) for drug in original_list]
    return {"DrugName": cleaned_list}

def remove_none_entries(input_list):
    """
    返回一个新列表，去除所有值为 None 的元素。
    """
    return [item for item in input_list if item is not None]

def transform_drugs(input_record):
    """
    将输入记录中的 'drugs' 字段重命名为 'DrugName'，并去掉 'subject_id'。
    Args:
      input_record (dict): 
        {
          "subject_id": "...",
          "drugs": [ ... ]
        }
    Returns:
      dict: {"DrugName": [...]}
    """
    # 从输入记录中提取 drugs 列表
    drugs_list = input_record.get("drugs", [])
    # 构造新的字典，只保留 DrugName
    return {"DrugName": drugs_list}

if __name__ == "__main__":
    # 1. 读取已有 JSON 文件

    if len(sys.argv) != 2:
        print("[Error] 请提供参数")
        sys.exit(1)

    patient_id = sys.argv[1]

    json_path = os.path.join(PROJECT_ROOT, "CCMDataset/Hospital_prescriptions.json")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 2. 指定要查询的 subject_id
    target_subject = patient_id  # 将其替换为你实际的 subject_id

    # 3. 调用函数，获取对应的 drugs 列表
    drugs_list = extract_drugs_by_subject(data, target_subject)

    # 4. 如果需要去重，可取消下面注释
    # drugs_list = list(dict.fromkeys(drugs_list))

    # 5. 将结果保存到新的数组或写出为文件
    output = {"subject_id": target_subject, "drugs": drugs_list}
    print(output)

    final_output = transform_drugs(output)
    print(final_output)

    # 如需写入 JSON 文件：
    with open("output_drugs.json", "w", encoding="utf-8") as fw:
        json.dump(output, fw, ensure_ascii=False, indent=2)

    rxcui_data = clean_drug_json(final_output)
    print(json.dumps(rxcui_data, indent=2))

    with open("output_drugs.json", "w", encoding="utf-8") as fw:
        json.dump(rxcui_data, fw, ensure_ascii=False, indent=2)

    print("Converting into rxcui list...")
    rxcuis = convert_drugs_to_rxcui_list("output_drugs.json")
    print(rxcuis)

    final_rxcuis = remove_none_entries(rxcuis)
    print(final_rxcuis)

    hospital_rxcuis = os.path.join(PROJECT_ROOT, f"ComparativeTest/Single_Agent/evaluation/{target_subject}/hospital_rxcuis.json")

    with open(hospital_rxcuis, "w", encoding="utf-8") as fw:
        json.dump(final_rxcuis, fw, ensure_ascii=False, indent=2)

    