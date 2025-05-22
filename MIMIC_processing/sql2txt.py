import csv
import os

# 替换为你的 CSV 路径
csv_file_path = 'chronic_diseases_38_with_rx.csv'
output_dir = 'txt_outputs'

# 创建输出目录（如果不存在）
os.makedirs(output_dir, exist_ok=True)

# 读取 CSV 文件
with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        subject_id = row['subject_id'].strip()
        text = row['text'].strip()

        # 定义文件名
        file_name = f"{subject_id}.txt"
        file_path = os.path.join(output_dir, file_name)

        # 保存文本到 .txt 文件
        with open(file_path, 'w', encoding='utf-8') as txt_file:
            txt_file.write(text)

print("所有文本已保存到 txt_outputs 目录中。")
