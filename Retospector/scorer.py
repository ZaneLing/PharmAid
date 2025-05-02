# scorer.py
class PrescriptionScorer:
    def __init__(self, guidelines, risk_rules, allergy_db):
        self.guidelines = guidelines        # 临床指南推荐药物集
        self.risk_rules = risk_rules        # 高风险组合与剂量规则
        self.allergy_db = allergy_db        # 患者过敏药物列表

    def score(self, recommended, ground_truth, patient):
        score = 0
        # 指南推荐药物
        for drug in recommended:
            if drug in self.guidelines:
                score += 1
        # 与真实处方重合度
        overlap = set(recommended) & set(ground_truth)
        score += 0.5 * len(overlap)
        # 高风险组合扣分
        for combo in self.risk_rules:
            if combo.issubset(recommended):
                score -= self.risk_rules[combo]
        # 过敏药物严重扣分
        for drug in recommended:
            if drug in self.allergy_db.get(patient.id, []):
                score -= 3
        return score