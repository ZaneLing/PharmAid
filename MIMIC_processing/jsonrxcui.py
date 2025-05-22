import json
import requests

# 1. Load the input JSON
with open("Hospital_prescriptions.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# 2. Prepare RxNorm API endpoint and a simple in‑memory cache
RXNORM_URL = "https://rxnav.nlm.nih.gov/REST/rxcui.json?name={}"
rxcui_cache = {}

def get_rxcui(drug_name):
    """
    Return the first RxCUI for a given drug_name using RxNav API.
    Caches results to avoid duplicate requests.
    """
    name_key = drug_name.lower()
    if name_key in rxcui_cache:
        return rxcui_cache[name_key]
    resp = requests.get(RXNORM_URL.format(drug_name))
    if resp.ok:
        ids = resp.json().get("idGroup", {}).get("rxnormId", [])
        rxcui = ids[0] if ids else None
    else:
        rxcui = None
    rxcui_cache[name_key] = rxcui
    return rxcui

# 3. Iterate over each prescription entry and map drugs → RxCUIs
for entry in data.get("Prescription", []):  # assume top‑level "Prescription" key
    drugs = entry.get("drugs", [])
    # Map each drug string to its RxCUI
    entry["drugsrxcui"] = [get_rxcui(drug) for drug in drugs]

# 4. Write out the augmented JSON
with open("output_prescriptions.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Converted drugs to RxCUI and saved to output_prescriptions.json")
