import csv
import json

input_csv = 'chronic_diseases_38_with_rx.csv'      # 替换为你的 CSV 文件路径
output_json = 'Hosipital_prescriptions.json'  # 输出 JSON 文件路径

prescriptions = []

with open(input_csv, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        subject = row.get('subject_id') or row.get('subject—id')  # 支持不同列名
        drugs_field = row['drugs']
        # 将 drugs 字符串按逗号拆分，并去除两端空白
        drugs_list = [d.strip() for d in drugs_field.split(',') if d.strip()]
        prescriptions.append({
            'subject_id': subject,
            'drugs': drugs_list
        })

# 构造最终结构
output = {
    'Prescription': prescriptions
}

# 写入 JSON 文件
with open(output_json, 'w', encoding='utf-8') as jf:
    json.dump(output, jf, indent=2, ensure_ascii=False)

print(f"Converted {len(prescriptions)} records to JSON → {output_json}")
