

    # topic1["Topic: PatientInfoReady"]
    # topic2["Topic: DiagnosisReady"]
    # topic3["Topic: DrugCandidatesReady"]
    # topic4["Topic: InteractionCheckReady"]
    # topic5["Topic: PatientConflictReady"]
    # topic6["Topic: ADEReportReady"]
    # topic7["Topic: DoseRecommendationReady"]


class PubSubBroker:
    def __init__(self):
        self.subscribers = {}

    def subscribe(self, topic, handler):
        self.subscribers.setdefault(topic, []).append(handler)

    def publish(self, topic, message):
        print(f"[Broker] 发布到主题 '{topic}': {message}")
        for handler in self.subscribers.get(topic, []):
            handler(message)

# 初始化消息总线
broker = PubSubBroker()

# 1. 信息处理 Agent
def info_processing_agent(raw_text):
    # 简单示例：解析字符串，生成 PatientInfo 字典
    patient_info = {
        'patientId': 'P001',
        'age': 65,
        'sex': 'M',
        'history': ['HTN', 'T2DM'],
        'labs': {'BP': '160/95', 'Cr': 2.1}
    }
    broker.publish('PatientInfoReady', patient_info)

# 2. 诊断 Agent
def diagnosis_agent(patient_info):
    diagnoses = [
        {'diag': 'Uncontrolled Hypertension', 'conf': 0.85},
        {'diag': 'CKD Stage 3', 'conf': 0.75}
    ]
    broker.publish('DiagnosisReady', diagnoses)

# 3. 药物初选 Agent
def drug_initial_selection_agent(diagnoses):
    candidates = ['Lisinopril', 'Amlodipine']
    broker.publish('DrugCandidatesReady', candidates)

# 4. 药物–药物交互 Agent
def drug_interaction_check_agent(candidates):
    report = [{'pair': ['Lisinopril', 'Amlodipine'], 'severity': 'low'}]
    broker.publish('InteractionCheckReady', report)

# 5. 药物–患者冲突 Agent
def patient_conflict_check_agent(candidates):
    # 假设无冲突
    filtered = candidates
    broker.publish('PatientConflictReady', filtered)

# 6. 不良反应检索 Agent
def ade_retrieval_agent(candidates):
    ade_report = [
        {'drug': 'Lisinopril', 'ADEs': [{'event': 'Cough', 'prob': 0.2}]},
        {'drug': 'Amlodipine', 'ADEs': [{'event': 'Peripheral edema', 'prob': 0.15}]}  
    ]
    broker.publish('ADEReportReady', ade_report)

# 7. 剂量推荐 Agent
def dose_recommendation_agent(data):
    # data 包含 patient_conflicts 和 ade_reports
    patient_conflicts, ade_reports = data
    doses = [
        {'drug': 'Lisinopril', 'dose': '10 mg QD'},
        {'drug': 'Amlodipine', 'dose': '5 mg QD'}
    ]
    broker.publish('DoseRecommendationReady', doses)

# 8. 协调器 Agent
def orchestrator_agent(doses):
    prescription = [f"{d['drug']} {d['dose']}" for d in doses]
    notes = "监测咳嗽与血钾水平"
    result = {'prescription': prescription, 'notes': notes}
    print(f"[Orchestrator] 最终处方建议: {result}")

# 订阅主题
broker.subscribe('PatientInfoReady', diagnosis_agent)
broker.subscribe('DiagnosisReady', drug_initial_selection_agent)
broker.subscribe('DrugCandidatesReady', drug_interaction_check_agent)
broker.subscribe('DrugCandidatesReady', patient_conflict_check_agent)
broker.subscribe('DrugCandidatesReady', ade_retrieval_agent)
# 将 patient_conflict 和 ade_report 联合传入剂量推荐 agent
# 简单实现：在两个结果均准备好后调用
_ready = {}
def _combine_and_publish(topic, payload, key):
    _ready[key] = payload
    if 'conflicts' in _ready and 'ades' in _ready:
        dose_recommendation_agent((_ready['conflicts'], _ready['ades']))

broker.subscribe('PatientConflictReady', lambda p: _combine_and_publish('PatientConflictReady', p, 'conflicts'))
broker.subscribe('ADEReportReady', lambda p: _combine_and_publish('ADEReportReady', p, 'ades'))

broker.subscribe('DoseRecommendationReady', orchestrator_agent)

if __name__ == '__main__':
    raw_text = "患者，男，65 岁，主诉乏力；既往高血压 10 年，2 型糖尿病 8 年；近期血压 160/95 mmHg，血肌酐 2.1 mg/dL。"
    info_processing_agent(raw_text)
