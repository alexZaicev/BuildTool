import os
from abc import ABC, abstractmethod
from threading import Thread

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
    def execute(self, cfg=None):
        raise BuildToolError("Command executor is not implemented")


class Utils(object):
    """
        Built Tool utility singleton
    """

    def __new__(cls, *args, **kwargs):
        raise BuildToolError("Utility classes cannot be instantiated")

    def __init__(self, *args, **kwargs):
        raise BuildToolError("Utility classes cannot be instantiated")


class Rule(ABC):
    """
        Build Tool rule object to store project specific build logic
    """

    def __init__(self):
        ABC.__init__(self)

    @abstractmethod
    def execute_rule(self, cfg, worker_id):
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


class PreBuildRule(Rule):
    """
        Build Tool rule object to store project specific build logic that will be executed
        before project build
    """

    def __init__(self, name=None):
        Rule.__init__(self)
        for rule in Helpers.PRE_BUILD_RULES:
            if rule == "PRE_B_{}".format(name):
                raise BuildToolError("Pre-Build Rule with name %s already exists" % rule)
        self.name = "PRE_B_{}".format(name)
        Helpers.PRE_BUILD_RULES.append(self)

    @abstractmethod
    def execute_rule(self, cfg, worker_id):
        raise BuildToolError("Rule logic has not been implemented")


class PostBuildRule(Rule):
    """
        Build Tool rule object to store project specific build logic that will be executed
        after project build
    """

    def __init__(self, name=None):
        Rule.__init__(self)
        for rule in Helpers.POST_BUILD_RULES:
            if rule == "POST_B_{}".format(name):
                raise BuildToolError("Post-Build Rule with name %s already exists" % rule)
        self.name = "POST_B_{}".format(name)
        Helpers.POST_BUILD_RULES.append(self)

    @abstractmethod
    def execute_rule(self, cfg, worker_id):
        raise BuildToolError("Rule logic has not been implemented")


class Job(ABC):

    def __init__(self, job_type, name, cfg=None):
        if job_type is None:
            raise BuildToolError("Job type cannot be None")
        self.name = name
        self.type = job_type
        self.cfg = cfg

    @abstractmethod
    def work(self, worker_id):
        raise BuildToolError("Job work not implemented")


class JobContainer(object):

    def __init__(self, jobs=(), cfg=None, rules=()):
        object.__init__(self)
        self.jobs = jobs
        self.cfg = cfg
        self.rules = rules

    def execute_job_set(self, worker_id):
        from helpers import WORKSPACE
        os.chdir(WORKSPACE)
        p = os.path.join(WORKSPACE, "{}_{}".format(Helpers.get_repo_name(self.cfg["name"]), worker_id))
        if os.path.exists(p):
            Helpers.remove_dir(p)
        os.mkdir("{}_{}".format(Helpers.get_repo_name(self.cfg["name"]), worker_id))
        os.chdir(p)

        try:
            for job in self.jobs:
                job.work(worker_id)
            Helpers.print_build_status(failed=False)
        except BuildToolError as ex:
            Helpers.print_build_status(msg=str(ex))


class JobInitializer(Initializer):
    """
        Build tool custom built rule initializer class
    """

    def initialize(self):
        import schedule
        job_types = {
            "tns": JobInitializer.__init_tns_job
        }
        for cfg in Helpers.CONFIGURATION["jobs"]:
            # check for job type
            try:
                jc = JobContainer(jobs=job_types[cfg["type"]](cfg), cfg=cfg)
                """
                    SCHEDULER
                """
                schedule.every(cfg["timer"]).seconds.do(Helpers.JOBS.put, jc.execute_job_set)
            except AttributeError:
                raise BuildToolError("Unknown job type %s specified in configuration file" % cfg["type"])
        return schedule

    @classmethod
    def __init_tns_job(cls, cfg):
        import jobs
        list_jobs = []
        if cfg["name"] is None or len(cfg["name"]) == 0:
            raise BuildToolError("Invalid build name. Check your configuration file and re-run Build Tool")
        # CHECK FOR GIT CONFIG
        if cfg["repository"] is not None and \
                cfg["branch"] is not None and \
                cfg["username"] is not None and \
                cfg["token"] is not None:
            list_jobs.append(jobs.GitJob(cfg["name"], cfg=cfg))
        else:
            raise BuildToolError("Cannot create Git job. Check your configuration file and re-run Build Tool")
        # CHECK FOR {NS} CONFIG
        if cfg["android"]["build"] is not None and \
                cfg["android"]["test"] is not None and \
                cfg["ios"]["build"] is not None and \
                cfg["ios"]["test"] is not None and \
                cfg["enabled"]:
            JobInitializer.__check_timer(cfg)
            list_jobs.append(jobs.TnsJob(cfg["name"], cfg=cfg))
        else:
            if cfg["enabled"] is not None and not cfg["enabled"]:
                raise BuildToolError("{NS} job %s is disabled" % cfg["name"])
            else:
                raise BuildToolError("Cannot create {NS} job. Check your configuration file and re-run Build Tool")
        return list_jobs

    @classmethod
    def __check_timer(cls, cfg):
        if cfg["timer"] is None or type(cfg["timer"]) != int:
            raise BuildToolError("Timer for build %s is not a valid integer" % cfg["name"])

    def __init__(self):
        Initializer.__init__(self)


class WorkerThread(Thread):

    def __init__(self, worker_id):
        Thread.__init__(self)
        self.worker_id = worker_id

    def run(self):
        while True:
            executor = Helpers.JOBS.get()
            executor(self.worker_id)
            Helpers.JOBS.task_done()
