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
        self.name = name

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


class PreBuildRule(Rule):
    """
        Build Tool rule object to store project specific build logic that will be executed
        before project build
    """

    def __init__(self, name=None):
        Rule.__init__(self, name)
        for br in Helpers.PRE_BUILD_RULES:
            if br.name == name:
                raise BuildToolError("Rule with name %s already exists" % name)
        Helpers.PRE_BUILD_RULES.append(self)

    @abstractmethod
    def execute_rule(self):
        raise BuildToolError("Rule logic has not been implemented")


class PostBuildRule(Rule):
    """
        Build Tool rule object to store project specific build logic that will be executed
        after project build
    """

    def __init__(self, name=None):
        Rule.__init__(self, name)
        for br in Helpers.POST_BUILD_RULES:
            if br.name == name:
                raise BuildToolError("Rule with name %s already exists" % name)
        Helpers.POST_BUILD_RULES.append(self)

    @abstractmethod
    def execute_rule(self):
        raise BuildToolError("Rule logic has not been implemented")


class Job(ABC):

    def __init__(self, job_type, name):
        if job_type is None:
            raise BuildToolError("Job type cannot be None")
        for job in Helpers.JOBS:
            if job.name == name:
                raise BuildToolError("Job with name %s already exists" % name)
        self.name = name
        self.type = job_type
        Helpers.JOBS.append(self)

    @abstractmethod
    def work(self):
        raise BuildToolError("Job work not implemented")


class JobInitializer(Initializer):
    """
        Build tool custom built rule initializer class
    """

    def initialize(self):
        import jobs
        # CHECK FOR GIT CONFIG
        if Helpers.CONFIGURATION.get("repository") is not None and \
                Helpers.CONFIGURATION.get("branch") is not None and \
                Helpers.CONFIGURATION.get("username") is not None and \
                Helpers.CONFIGURATION.get("token") is not None:
            jobs.GitJob()
        else:
            raise BuildToolError("Cannot create Git job. Check your configuration file and re-run Build Tool")
        # CHECK FOR {NS} CONFIG
        if Helpers.CONFIGURATION.get("build").get("nativescript").get("enabled") is not None and \
                Helpers.CONFIGURATION.get("build").get("nativescript").get("enabled") and \
                Helpers.CONFIGURATION.get("build").get("nativescript").get("timer") is not None and \
                Helpers.CONFIGURATION.get("build").get("nativescript").get("android").get("build") is not None and \
                Helpers.CONFIGURATION.get("build").get("nativescript").get("android").get("test") is not None and \
                Helpers.CONFIGURATION.get("build").get("nativescript").get("ios").get("build") is not None and \
                Helpers.CONFIGURATION.get("build").get("nativescript").get("ios").get("test") is not None:
            jobs.TnsJob()

    def __init__(self):
        Initializer.__init__(self)
