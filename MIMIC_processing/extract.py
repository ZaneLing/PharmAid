import re
import os

def extract_social_history_and_family_history(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # 使用正则表达式匹配 "Social History:" 和 "Family History:" 部分
        pattern = r"Social History:\s*(.*?)\s*Family History:\s*(.*?)(?=\n\n|\Z)"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            social_history = match.group(1).strip()
            family_history = match.group(2).strip()
            return social_history, family_history
        else:
            raise ValueError("未找到 'Social History:' 和 'Family History:' 部分的内容。")
    except Exception as e:
        print(f"[Error] 无法提取 'Social History:' 和 'Family History:' 部分: {e}")
        return "", ""

def extract_past_medical_history(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # 使用正则表达式匹配 "Medications on Admission:" 部分
        pattern = r"Past Medical History:\s*(.*?)\s*Social History:"
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            medications = match.group(1).strip()
            return medications
        else:
            raise ValueError("未找到 'Past Medical History:' 部分的内容。")
    except Exception as e:
        print(f"[Error] 无法提取 'Past Medical History:' 部分: {e}")
        return ""

def extract_medications_on_admission(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # 使用正则表达式匹配 "Medications on Admission:" 部分
        pattern = r"Medications on Admission:\s*(.*?)\s*Discharge Medications:"
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            medications = match.group(1).strip()
            return medications
        else:
            raise ValueError("未找到 'Medications on Admission:' 部分的内容。")
    except Exception as e:
        print(f"[Error] 无法提取 'Medications on Admission:' 部分: {e}")
        return ""
    
def extract_discharge_medications(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # 使用正则表达式匹配 "Medications on Admission:" 部分
        pattern = r"Discharge Medications:\s*(.*?)\s*Discharge Disposition:"
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            medications = match.group(1).strip()
            return medications
        else:
            raise ValueError("未找到 'Discharge Medications:' 部分的内容。")
    except Exception as e:
        print(f"[Error] 无法提取 'Discharge Medications:' 部分: {e}")
        return ""  

def extract_discharge_diagnosis(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # 使用正则表达式匹配 "Medications on Admission:" 部分
        pattern = r"Discharge Diagnosis:\s*(.*?)\s*Discharge Condition:"
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            medications = match.group(1).strip()
            return medications
        else:
            raise ValueError("未找到 'Discharge Diagnosis:' 部分的内容。")
    except Exception as e:
        print(f"[Error] 无法提取 'Discharge Diagnosis:' 部分: {e}")
        return ""

def extract_physical_exam(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # 使用正则表达式匹配 "Medications on Admission:" 部分
        pattern = r"Physical Exam:\s*(.*?)\s*Pertinent Results:"
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            medications = match.group(1).strip()
            return medications
        else:
            raise ValueError("未找到 'Physical Exam:' 部分的内容。")
    except Exception as e:
        print(f"[Error] 无法提取 'Physical Exam:' 部分: {e}")
        return ""



# social_history_and_family_history = extract_social_history_and_family_history(file_path)
# past_medical_history = extract_past_medical_history(file_path)
# medications_on_admission = extract_medications_on_admission(file_path)
# discharge_medications = extract_discharge_medications(file_path)
# discharge_diagnosis = extract_discharge_diagnosis(file_path)
# physical_exam = extract_physical_exam(file_path)

# if medications_on_admission:
#     print("\nMedications on Admission:")
#     print(medications_on_admission)
# else:
#     print("未能提取 'Medications on Admission:' 部分的内容。")

# if discharge_medications:
#     print("\nDischarge Medications:")
#     print(discharge_medications)
# else:
#     print("未能提取 'Discharge Medications:' 部分的内容。")

# if discharge_diagnosis:
#     print("\nDischarge Diagnosis:")
#     print(discharge_diagnosis)
# else:
#     print("未能提取 'Discharge Diagnosis:' 部分的内容。")

# if physical_exam:
#     print("\nPhysical Exam:")
#     print(physical_exam)
# else:
#     print("未能提取 'Physical Exam:' 部分的内容。")

# if past_medical_history:
#     print("\nPast Medical History:")
#     print(past_medical_history)
# else:
#     print("未能提取 'Past Medical History:' 部分的内容。")

# if social_history_and_family_history:
#     print("\nSocial History and Family History:")
#     print(social_history_and_family_history)
# else:
#     print("未能提取 'Social History:' 和 'Family History:' 部分的内容。")


    # 定义输入和输出文件夹路径
input_folder = "./txt_outputs"
output_folder = "./processed_outputs"

    # 创建输出文件夹（如果不存在）
os.makedirs(output_folder, exist_ok=True)

    # 遍历输入文件夹中的所有txt文件
for file_name in os.listdir(input_folder):
    if file_name.endswith(".txt"):
        file_path = os.path.join(input_folder, file_name)
        patient_id = os.path.splitext(file_name)[0]
        patient_folder = os.path.join(output_folder, patient_id)
            
            # 为每个病人创建一个文件夹
        os.makedirs(patient_folder, exist_ok=True)
            
            # 提取信息
        social_history_and_family_history = extract_social_history_and_family_history(file_path)
        past_medical_history = extract_past_medical_history(file_path)
        medications_on_admission = extract_medications_on_admission(file_path)
        discharge_medications = extract_discharge_medications(file_path)
        discharge_diagnosis = extract_discharge_diagnosis(file_path)
        physical_exam = extract_physical_exam(file_path)
            
            # 保存提取的信息到对应的txt文件
        if social_history_and_family_history:
            with open(os.path.join(patient_folder, "social_history_and_family_history.txt"), "w", encoding="utf-8") as f:
                f.write("\n".join(social_history_and_family_history))
            
        if past_medical_history:
            with open(os.path.join(patient_folder, "past_medical_history.txt"), "w", encoding="utf-8") as f:
                f.write(past_medical_history)
            
        if medications_on_admission:
            with open(os.path.join(patient_folder, "medications_on_admission.txt"), "w", encoding="utf-8") as f:
                f.write(medications_on_admission)
            
        if discharge_medications:
            with open(os.path.join(patient_folder, "discharge_medications.txt"), "w", encoding="utf-8") as f:
                f.write(discharge_medications)
            
        if discharge_diagnosis:
            with open(os.path.join(patient_folder, "discharge_diagnosis.txt"), "w", encoding="utf-8") as f:
                f.write(discharge_diagnosis)
            
        if physical_exam:
            with open(os.path.join(patient_folder, "physical_exam.txt"), "w", encoding="utf-8") as f:
                f.write(physical_exam)