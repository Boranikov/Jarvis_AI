class Memory:
    def __init__(self):
        self.history = []
        self.pending_action = None
        self.pending_params = []

    def add(self, user, jarvis):
        self.history.append({"user": user, "jarvis": jarvis})
        if len(self.history) > 10:
            self.history = self.history[-10:]

    def set_pending(self, action, params):
        self.pending_action = action
        self.pending_params = params.copy()

    def has_pending(self):
        return self.pending_action is not None

    def fill_pending(self, user_input):
        if not self.pending_action or not self.pending_params:
            return None

        value = user_input.strip()

        param = self.pending_params.pop(0)
        params = {param: value}

        if not self.pending_params:
            action = self.pending_action
            self.pending_action = None
            return action, params

        return None
