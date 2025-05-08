import os
import re
from typing import List, Dict

def sanitize_filename(name: str, max_length: int = 255) -> str:
    """
    将任意字符串转换为安全的文件名，移除或替换非法字符，并截断长度。
    """
    name = name.strip()
    # 连续空白转下划线
    name = re.sub(r"\s+", "_", name)
    # 非字母数字、下划线、连字符、点号的字符都去除
    name = re.sub(r"[^\w\-\.\u4e00-\u9fa5]+", "", name)
    return name[:max_length]

def extract_sections(text: str, headers: List[str]) -> Dict[str, str]:
    """
    从文本中提取以 headers 中任一字符串为整行开头，
    并一直读取到遇到完整空行前的所有内容。

    返回值：{标题: 对应内容}（不含标题行本身）。
    """
    # 构造匹配整行“标题名”的正则
    header_re = re.compile(rf"^({'|'.join(re.escape(h) for h in headers)})\s*$")
    sections: Dict[str, str] = {}
    lines = text.splitlines()
    current = None
    buffer: List[str] = []

    # 在末尾追加一个空行，用于触发最后一个段落的保存
    for line in lines + [""]:
        if current:
            if line.strip() == "":
                # 遇到空行，段落结束
                sections[current] = "\n".join(buffer).strip()
                current = None
                buffer = []
            else:
                buffer.append(line)
        else:
            m = header_re.match(line)
            if m:
                # 找到新标题，开始收集
                current = m.group(1)
                buffer = []
    return sections

def save_sections(sections: Dict[str, str], output_dir: str) -> None:
    """
    将提取的每个段落保存为单独的 TXT 文件。
    """
    os.makedirs(output_dir, exist_ok=True)
    for title, content in sections.items():
        fname = sanitize_filename(title) or "section"
        path = os.path.join(output_dir, f"{fname}.txt")
        with open(path, "w", encoding="utf-8") as fw:
            fw.write(title + "\n")
            fw.write(content + "\n")
        print(f"Saved: {path}")

if __name__ == "__main__":
    # 配置：输入文件、输出目录和待提取的标题列表
    input_file = "./L1/1041.txt"  # 替换为你的输入文件路径
    output_folder = "./L1/1041"
    headers_to_extract = [
        "Medications on Admission",
        "Discharge Medications",
        "Discharge Diagnosis",
        "PHYSICAL EXAM",
        "Family History",
        "Social History",
        "Past Medical History",
        "History of Present Illness",
        "Allergies",
        "Chief Complaint",
        "Major Surgical or Invasive Procedure"
    ]

    # 读取全文
    with open(input_file, "r", encoding="utf-8") as f:
        full_text = f.read()

    print(f"[INFO] 读取文件: {full_text}")
    # 提取并保存
    secs = extract_sections(full_text, headers_to_extract)
    print(f"[INFO] 提取到的段落: {secs}")
    save_sections(secs, output_folder)
