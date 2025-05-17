import re
import os
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def extract_info(text):
    # 初始化结果字典
    result = {
        "medications_on_admission": [],
        "discharge_medications": [],
        "diagnosis": "",
        "treatment_process": "",
        "other_info": ""
    }

    # 分割文本到各个部分
    parts = re.split(r'\n\s*\n', text.strip())

    # 提取入院药物信息
    if "Medications on Admission:" in parts[0]:
        admission_meds = re.findall(r'\d+\.\s+(.+)', parts[0])
        result["medications_on_admission"] = admission_meds

    # 提取出院药物信息
    discharge_section = None
    for part in parts[1:]:
        if "Discharge Medications:" in part:
            discharge_section = part
            break

    if discharge_section:
        discharge_meds = re.findall(r'\d+\.\s+(.+)', discharge_section)
        result["discharge_medications"] = discharge_meds

    # 提取诊断和治疗过程等其他信息
    other_info_section = None
    for part in parts:
        if "DX:" in part or "PX:" in part:
            other_info_section = part
            break

    if other_info_section:
        # 提取诊断
        dx_match = re.search(r'DX:\s*(.+)', other_info_section)
        if dx_match:
            result["diagnosis"] = dx_match.group(1)

        # 提取治疗过程
        px_match = re.search(r'PX:\s*(.+)', other_info_section)
        if px_match:
            result["treatment_process"] = px_match.group(1)

        # 提取其他信息
        other_info = re.sub(r'DX:.+|PX:.+', '', other_info_section)
        result["other_info"] = other_info.strip()

    return result

def read_txt_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        print(f"文件未找到：{file_path}")
        return None
    except Exception as e:
        print(f"读取文件时发生错误：{e}")
        return None

# 示例文本
text_path = os.path.join(PROJECT_ROOT, "CCMDataset/L1/1030.txt")
print(text_path)


text = read_txt_file(text_path)
print(text)

# 提取信息
info = extract_info(text)
print(info)