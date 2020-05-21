"""
Main class to management failed counter.
May have just one instance
"""


class FailedCounter(object):
    _instance = None

    @staticmethod
    def get_instance():
        """
        Management method  to create class. Thanks this method we got Singleton and just one instance of this class.

        :return: instance of this class: if not exist return new instance
        :rtype: FailedCounter
        """
        if FailedCounter._instance is None:
            return FailedCounter()
        return FailedCounter._instance

    def __init__(self):
        """
            constructor of this class. Setting counter to 0
        """
        if FailedCounter._instance is None:
            self.count = 0
        FailedCounter._instance = self

    def __del__(self):
        r"""
        deleting object
        """
        del self.count

    def clear_count(self):
        """
        setting counter to 0

        :return: None
        :rtype: None
        """
        self.count = 0

    def add(self):
        """
        increased counter

        :return: None
        :rtype: None
        """
        self.count += 1

    def get_count(self):
        """
        method to getting object of this class

        :return: counter who is object in this class
        :rtype: int
        """
        return self.count

    def is_valid(self):
        """
        checking valid of counter.

        :return: True is counter is valid or False if counter is not valid
        :rtype: bool
        """
        if self.count < 3:
            return True
        else:
            return False
