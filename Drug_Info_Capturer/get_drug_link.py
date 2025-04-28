import os
import pandas as pd
from crewai_tools import WebsiteSearchTool
from pydantic import BaseModel
import requests

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

oak = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = oak

# csv_file = 'fda_drugbank.csv'

class Drug2WebLink():
    # 读取 CSV 文件
    def get_drug_fda_link(self, drug_name: str, csv_file: str) -> str:
        try:
            df = pd.read_csv(csv_file, encoding='ISO-8859-1', encoding_errors='ignore')
            
            drug_row = df[
                (df['Generic/Proper Name(s)'].str.lower() == drug_name.lower()) |
                (df['Trade Name'].str.lower() == drug_name.lower())
            ]

            if not drug_row.empty:
                return drug_row.iloc[0]['DailyMed SPL Link']
            else:
                raise ValueError(f"Drug '{drug_name}' not found in the CSV file.")
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return None
        
    def get_drug_dailymed_link(self, drug_name: str, csv_file: str) -> str:
        try:
            df = pd.read_csv(csv_file, encoding='ISO-8859-1', encoding_errors='ignore')
            
            drug_row = df[
                (df['Generic/Proper Name(s)'].str.lower() == drug_name.lower()) |
                (df['Trade Name'].str.lower() == drug_name.lower())
            ]

            if not drug_row.empty:
                return drug_row.iloc[0]['FDALabel Link']
            else:
                raise ValueError(f"Drug '{drug_name}' not found in the CSV file.")
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return None
        
    def download_drug_pdf_from_csv(self, drug_name: str, csv_file: str, output_dir: str = 'drug_instruction_pdfs') -> None:
        try:

            print(f"Drug name: {drug_name}")
            print(f"CSV file: {csv_file}")
            
            df = pd.read_csv(csv_file, encoding='ISO-8859-1', encoding_errors='ignore')
            
            print("Search...")

            # 查找匹配的药物行
            drug_row = df[
                (df['Generic/Proper Name(s)'].str.lower() == drug_name.lower()) |
                (df['Trade Name'].str.lower() == drug_name.lower())
            ]

            if not drug_row.empty:
                # 获取 DailyMed PDF Link
                pdf_link = drug_row.iloc[0]['DailyMed PDF Link']
                
                print("pdf link:", pdf_link)

                if not pdf_link or not pdf_link.startswith("http"):
                    print(f"No valid PDF link found for drug '{drug_name}'.")
                    return
                
                # 创建输出目录（如果不存在）
                os.makedirs(output_dir, exist_ok=True)
                
                # 下载 PDF 文件
                response = requests.get(pdf_link, stream=True)
                if response.status_code == 200:
                    pdf_path = os.path.join(output_dir, f"{drug_name}.pdf")
                    with open(pdf_path, 'wb') as pdf_file:
                        for chunk in response.iter_content(chunk_size=1024):
                            pdf_file.write(chunk)
                    print(f"PDF for drug '{drug_name}' has been downloaded and saved to '{pdf_path}'.")
                else:
                    print(f"Failed to download PDF for drug '{drug_name}'. HTTP Status Code: {response.status_code}")
            else:
                print(f"Drug '{drug_name}' not found in the CSV file.")
        except Exception as e:
            print(f"Error processing drug '{drug_name}': {e}")

# drug_name = "ibuprofen"
# csv_file = "fda_drugbank.csv"
# ex1 = Drug2WebLink()

# #ex1.download_drug_pdf_from_csv(drug_name, csv_file)

# dmlink = ex1.get_drug_dailymed_link(drug_name, csv_file)
# print("dmlink:", dmlink)

# fdalink = ex1.get_drug_fda_link(drug_name, csv_file)
# print("fdalink:", fdalink)