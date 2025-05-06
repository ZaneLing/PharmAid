import os
import json

def split_json_by_subtitles(input_file, output_folder):
    try:
        # 读取输入 JSON 文件
        with open(input_file, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # 确保输出文件夹存在
        os.makedirs(output_folder, exist_ok=True)

        # 遍历 JSON 数据的每个子标题
        for subtitle, content in data.items():
            # 构造输出文件路径
            output_file = os.path.join(output_folder, f"{subtitle}.json")

            # 将子标题内容写入单独的 JSON 文件
            with open(output_file, 'w', encoding='utf-8') as outfile:
                json.dump({subtitle: content}, outfile, ensure_ascii=False, indent=4)

            print(f"[INFO] 已保存: {output_file}")

    except Exception as e:
        print(f"[ERROR] 处理文件时出错: {e}")

if __name__ == "__main__":
    # 输入 JSON 文件路径
    patient_id = 2  # 替换为你的患者 ID
    print(f"[INFO] 处理患者 ID: {patient_id}")
    
    #input_file = ".../Patient_Info_Cleaner/patient_info_reports/{patient_id}_patient_info.json"  # 替换为你的 JSON 文件路径
    #input_file = ".../Patient_Info_Cleaner/patient_info_reports/1_patient_info.json"
    input_file = '/Users/lingziyang/Desktop/PharmAid-main/Patient_Info_Cleaner/patient_info_reports/1_patient_info.json'  # 替换为你的 JSON 文件路径
    # 输出文件夹路径
    output_folder = f'../Contents/{patient_id}'  # 替换为你的输出文件夹路径

    split_json_by_subtitles(input_file, output_folder)