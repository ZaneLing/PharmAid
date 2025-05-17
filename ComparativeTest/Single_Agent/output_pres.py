import json
import requests
import os, sys
import re
# RxNorm API endpoint
RXNORM_BASE_URL = "https://rxnav.nlm.nih.gov/REST/rxcui.json?name="
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


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

if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("[Error] 请提供参数")
        sys.exit(1)

    patient_id = sys.argv[1]

    target_subject = patient_id
    input_file = os.path.join(PROJECT_ROOT, f"ComparativeTest/Single_Agent/evaluation/{target_subject}/output_prescription.json")
    with open(input_file, "r") as f:
        input_data = json.load(f)
    output_data = clean_drug_json(input_data)
    print(json.dumps(output_data, indent=2))
    rxcuis = convert_drugs_to_rxcui_list(input_file)
    print(rxcuis)

    final_rxcuis = remove_none_entries(rxcuis)
    print(final_rxcuis)

    output_rxcuis = os.path.join(PROJECT_ROOT, f"ComparativeTest/Single_Agent/evaluation/{target_subject}/output_rxcuis.json")

    with open(output_rxcuis, "w", encoding="utf-8") as fw:
        json.dump(final_rxcuis, fw, ensure_ascii=False, indent=2)

