import os
import re

def sanitize_filename(name: str, max_length: int = 255) -> str:
    name = name.strip()
    name = re.sub(r"\s+", "_", name)
    name = re.sub(r"[^\w\-\.]+", "", name)
    return name[:max_length]

def split_file(input_path: str, output_dir: str) -> None:
    """
    按照空白行（包括仅包含空格或Tab）将输入文本分割成多个段落，并保存到输出目录中。
    
    参数:
        input_path: 输入文本文件路径
        output_dir: 输出文件夹路径
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 匹配：一行只包含空格、Tab 或换行符的多行作为分隔符
    segments = re.split(r"(?:\r?\n\s*\r?\n)+", content)
    seen = {}

    for idx, segment in enumerate(segments, start=1):
        lines = [line for line in segment.splitlines() if line.strip()]
        if not lines:
            continue
        first_line = lines[0]
        base_name = sanitize_filename(first_line)
        if not base_name:
            base_name = f"segment_{idx}"

        count = seen.get(base_name, 0) + 1
        seen[base_name] = count
        if count > 1:
            filename = f"{base_name}_{count}.txt"
        else:
            filename = f"{base_name}.txt"

        output_path = os.path.join(output_dir, filename)
        with open(output_path, 'w', encoding='utf-8') as out_f:
            out_f.write(segment.strip() + '\n')
        print(f"Written: {output_path}")


# 示例调用方式
if __name__ == '__main__':
    for patient_id in range(1032, 1042):
        input_file = f"./L1/{patient_id}.txt"
        output_folder = f"./L1/{patient_id}"
        split_file(input_file, output_folder)
