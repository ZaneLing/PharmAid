import numpy as np

def dynamic_weight_update(w_t, scores, alpha=0.8, beta=0.05):
    # alpha (float): 平滑系数，越大越保留历史权重
    # beta (float): softmax温度因子，越大越敏感于得分差异
    w_t = np.array(w_t)
    s = np.array(scores)

    #  Softmax-based raw weights from scores
    raw_w = np.exp(beta * s)
    raw_w /= raw_w.sum()  # Normalize (Z)

    #  Exponential smoothing fusion
    w_t1 = alpha * w_t + (1 - alpha) * raw_w

    return w_t1.tolist()
