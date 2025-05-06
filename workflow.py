import os
from dotenv import load_dotenv

from Patient_Info_Cleaner.Patient_info_cleaner import patient_info_clean_process
from ADR_Detector.adr_detector import ADR_Detector
from Diagnosis_Module.diagnosis import generate_diagnosis
from Drug_Selection_Module.drug_selector import select_initial_drugs
from Interaction_Check_Module.interaction_checker import check_drug_interactions
from Patient_Conflict_Module.conflict_checker import check_patient_conflicts
from ADE_Module.ade_retriever import retrieve_ade_reports
from Dose_Recommendation_Module.dose_recommender import recommend_doses

# 加载环境变量
load_dotenv()
oak = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = oak

# 黑板实现
class Blackboard:
    def __init__(self):
        self.data = {}

    def write(self, key, value):
        print(f"[Blackboard] 写入: {key} -> {value}")
        self.data[key] = value

    def read(self, key):
        value = self.data.get(key)
        print(f"[Blackboard] 读取: {key} -> {value}")
        return value

# 初始化黑板
blackboard = Blackboard()

# 1. 信息处理 Agent
def info_processing_agent(raw_text):
    try:
        patient_info = clean_patient_info(raw_text)
        blackboard.write('PatientInfo', patient_info)
    except Exception as e:
        print(f"[Info Processing Agent] 处理患者信息时出错: {e}")

# 2. 诊断 Agent
def diagnosis_agent():
    try:
        patient_info = blackboard.read('PatientInfo')
        diagnoses = generate_diagnosis(patient_info)
        blackboard.write('Diagnosis', diagnoses)
    except Exception as e:
        print(f"[Diagnosis Agent] 生成诊断时出错: {e}")

# 3. 药物初选 Agent
def drug_initial_selection_agent():
    try:
        diagnoses = blackboard.read('Diagnosis')
        candidates = select_initial_drugs(diagnoses)
        blackboard.write('DrugCandidates', candidates)
    except Exception as e:
        print(f"[Drug Initial Selection Agent] 药物初选时出错: {e}")

# 4. 药物–药物交互 Agent
def drug_interaction_check_agent():
    try:
        candidates = blackboard.read('DrugCandidates')
        interaction_report = check_drug_interactions(candidates)
        blackboard.write('InteractionCheck', interaction_report)
    except Exception as e:
        print(f"[Drug Interaction Check Agent] 检查药物交互时出错: {e}")

# 5. 药物–患者冲突 Agent
def patient_conflict_check_agent():
    try:
        candidates = blackboard.read('DrugCandidates')
        filtered_candidates = check_patient_conflicts(candidates)
        blackboard.write('PatientConflict', filtered_candidates)
    except Exception as e:
        print(f"[Patient Conflict Check Agent] 检查患者冲突时出错: {e}")

# 6. 不良反应检索 Agent
def ade_retrieval_agent():
    try:
        candidates = blackboard.read('DrugCandidates')
        ade_report = retrieve_ade_reports(candidates)
        blackboard.write('ADEReport', ade_report)
    except Exception as e:
        print(f"[ADE Retrieval Agent] 检索不良反应时出错: {e}")

# 7. 剂量推荐 Agent
def dose_recommendation_agent():
    try:
        patient_conflicts = blackboard.read('PatientConflict')
        ade_reports = blackboard.read('ADEReport')
        doses = recommend_doses(patient_conflicts, ade_reports)
        blackboard.write('DoseRecommendation', doses)
    except Exception as e:
        print(f"[Dose Recommendation Agent] 推荐剂量时出错: {e}")

# 8. 协调器 Agent
def orchestrator_agent():
    try:
        doses = blackboard.read('DoseRecommendation')
        prescription = [f"{d['drug']} {d['dose']}" for d in doses]
        notes = "监测咳嗽与血钾水平"
        result = {'prescription': prescription, 'notes': notes}
        blackboard.write('FinalDecision', result)
        print(f"[Orchestrator] 最终处方建议: {result}")
    except Exception as e:
        print(f"[Orchestrator Agent] 生成最终决策时出错: {e}")

# 主流程
if __name__ == '__main__':
    raw_text = "患者，男，65 岁，主诉乏力；既往高血压 10 年，2 型糖尿病 8 年；近期血压 160/95 mmHg，血肌酐 2.1 mg/dL。"

    # 按顺序调用各个 Agent
    print("---------Patient Information Extraction---------")
    info_processing_agent(raw_text)

    print("---------Diagnosis---------")
    diagnosis_agent()

    print("---------Drug Initial Selection---------")
    drug_initial_selection_agent()

    print("---------Drug Interaction Check---------")
    drug_interaction_check_agent()

    print("---------Patient Conflict Check---------")
    patient_conflict_check_agent()

    print("---------ADE Retrieval---------")
    ade_retrieval_agent()

    print("---------Dose Recommendation---------")
    dose_recommendation_agent()

    print("---------Final Decision---------")
    orchestrator_agent()

    #喵

    