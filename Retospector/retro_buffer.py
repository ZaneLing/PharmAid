class ReplayBuffer:
    def __init__(self, capacity=100000):
        self.buffer = []
        self.capacity = capacity

    def add(self, case_id, state, action, score, next_state):
        if len(self.buffer) >= self.capacity:
            self.buffer.pop(0)
        self.buffer.append((case_id, state, action, score, next_state))

    def sample(self, batch_size):
        import random
        return random.sample(self.buffer, min(batch_size, len(self.buffer)))
