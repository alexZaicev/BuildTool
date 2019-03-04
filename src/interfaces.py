from abc import ABC, abstractmethod

from helpers import Helpers


class BuildToolError(Exception):
    """
        Build Tool specific exception
    """


class Command(ABC):
    """
        Built Tool command object to store command execution logic
    """

    def __init__(self):
        ABC.__init__(self)

    @abstractmethod
    def execute(self):
        raise BuildToolError("Command executor is not implemented")


class Rule(ABC):
    """
        Build Tool rule object to store project specific build logic
    """

    def __init__(self, name=None):
        ABC.__init__(self)
        if name is None:
            raise BuildToolError("Rule name cannot be None")
        for br in Helpers.BUILD_RULES:
            if br.name == name:
                raise BuildToolError("Rule with name %s already exists" % name)
        self.name = name
        Helpers.BUILD_RULES.append(self)

    @abstractmethod
    def execute_rule(self):
        raise BuildToolError("Rule logic has not been implemented")


class Initializer(ABC):
    """
        Build Tool init object to initialize all project build rules
    """

    def __init__(self):
        ABC.__init__(self)

    @abstractmethod
    def initialize(self):
        raise BuildToolError("Initialize has not been implemented")


class Utils(object):
    """
        Built Tool utility singleton
    """

    def __new__(cls, *args, **kwargs):
        raise BuildToolError("Utility classes cannot be instantiated")

    def __init__(self, *args, **kwargs):
        raise BuildToolError("Utility classes cannot be instantiated")


class RuleInitializer(Initializer):
    """
        Build tool custom built rule initializer class
    """

    def initialize(self):
        from easypro_rules import EasyProRule
        EasyProRule()

    def __init__(self):
        Initializer.__init__(self)
