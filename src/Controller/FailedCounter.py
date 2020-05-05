class FailedCounter(object):
    _instance = None

    @staticmethod
    def get_instance():
        """
        :return: if instance does not exists return new instance else return existing instance
        """
        if FailedCounter._instance is None:
            return FailedCounter()
        return FailedCounter._instance

    def __init__(self):
        """
        initialize class and set count to 0
        """
        if FailedCounter._instance is None:
            self.count = 0
        FailedCounter._instance = self

    def __del__(self):
        """
        deleting object
        """
        del self.count

    def clear_count(self):
        """
        reseting counter
        """
        self.count = 0

    def add(self):
        """
        increasing counter
        """
        self.count += 1

    def get_count(self):
        """
        :return: getting object
        """
        return self.count

    def is_valid(self):
        """
        checking valid of counter
        :return: True is counter is valid or False if counter is not valid
        """
        if self.count < 3:
            return True
        else:
            return False
