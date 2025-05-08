# evaluator.py
from scorer import PrescriptionScorer
from replay_buffer import ReplayBuffer

class RetrospectAgent:
    def __init__(self, guidelines, risk_rules, allergy_db):
        self.scorer = PrescriptionScorer(guidelines, risk_rules, allergy_db)
        self.buffer = ReplayBuffer()

    def evaluate_case(self, case):
        state = case.patient_profile
        ground_truth = case.actual_prescription
        recommended = case.agent_recommendation
        next_state = case.outcome_profile

        score = self.scorer.score(recommended, ground_truth, case.patient)
        self.buffer.add(case.id, state, recommended, score, next_state)
        return score

    def generate_report(self):
        # 汇总所有打分，并输出低分案例与统计
        scores = [entry[3] for entry in self.buffer.buffer]
        avg_score = sum(scores) / len(scores) if scores else 0
        low_cases = [entry for entry in self.buffer.buffer if entry[3] < 0]
        return {
            "average_score": avg_score,
            "low_performance_count": len(low_cases),
            "low_cases": low_cases
        }
