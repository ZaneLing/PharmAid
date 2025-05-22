import pandas as pd
import requests

# 1. 修改为你的 CSV 文件实际路径
csv_path = 'chronic_diseases_38_with_rx.csv'

# 2. 读取 CSV
df = pd.read_csv(csv_path)

# 3. RxNorm API endpoint
RXNORM_BASE_URL = "https://rxnav.nlm.nih.gov/REST/rxcui.json?name="

# 建立缓存
rxcui_cache = {}

def get_rxcui_cached(drug_name):
    drug_name = drug_name.lower()
    if drug_name in rxcui_cache:
        return rxcui_cache[drug_name]
    resp = requests.get(f"https://rxnav.nlm.nih.gov/REST/rxcui.json?name={drug_name}")
    if resp.status_code == 200:
        data = resp.json()
        ids = data.get("idGroup", {}).get("rxnormId", [])
        rxcui = ids[0] if ids else None
    else:
        rxcui = None
    rxcui_cache[drug_name] = rxcui
    return rxcui

def map_drugs_to_rxcui(drugs_str):
    names = [d.strip() for d in drugs_str.split(',')]
    return [get_rxcui_cached(name) for name in names]

# 4. 应用转换，生成新列 'drugsrxcui'
df['drugsrxcui'] = df['drugs'].apply(map_drugs_to_rxcui)

print(f"Converted RxCUI list saved to: {output_path}")
