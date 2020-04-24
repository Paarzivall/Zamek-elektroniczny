class FailedCounter(object):
    _instance = None

    @staticmethod
    def get_instance():
        if FailedCounter._instance is None:
            return FailedCounter()
        return FailedCounter._instance

    def __init__(self):
        if FailedCounter._instance is None:
            self.count = 0
        FailedCounter._instance = self

    def __del__(self):
        del self.count

    def clear_count(self):
        self.count = 0

    def add(self):
        self.count += 1

    def get_count(self):
        return self.count

    def is_valid(self):
        if self.count < 3:
            return True
        else:
            return False
