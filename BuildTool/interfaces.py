"""
    Product Name: BuildTool
    Author: Aleksej Zaicev

    Copyright 2019
"""

import os
from abc import ABC, abstractmethod
from threading import Thread

from helpers import Helpers


class BuildToolError(Exception):
    """
        Build Tool specific exception
    """


class BuildToolFileAccessError(Exception):
    """
        Build Tool File Access exception
    """


class Command(ABC):
    """
        Built Tool command object to store command execution logic
    """

    def __init__(self):
        ABC.__init__(self)

    @abstractmethod
    def execute(self, cfg=None, worker_id=0, logger=None):
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
    def execute_rule(self, cfg, worker_id, logger):
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
    def execute_rule(self, cfg, worker_id, logger):
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
    def execute_rule(self, cfg, worker_id, logger):
        raise BuildToolError("Rule logic has not been implemented")


class Job(ABC):
    """
        Build Tool job object to contain execution sequence for a specific job
    """

    def __init__(self, job_type, name, cfg=None):
        if job_type is None:
            raise BuildToolError("Job type cannot be None")
        self.name = name
        self.type = job_type
        self.cfg = cfg

    @abstractmethod
    def work(self, worker_id, logger):
        raise BuildToolError("Job work not implemented")


class JobContainer(object):
    """
        Build Tool job container object, stores jobs to execute for a specific build and
        and executes the build job set
    """

    def __init__(self, jobs=(), cfg=None, rules=()):
        object.__init__(self)
        self.jobs = jobs
        self.cfg = cfg
        self.rules = rules

    def execute_job_set(self, worker_id):
        from helpers import WORKSPACE
        from logger import Logger

        logger = Logger(name="{}_{}".format(self.cfg["name"], worker_id))
        p = os.path.join(WORKSPACE, "{}_{}".format(self.cfg["name"], worker_id))
        if os.path.exists(p):
            logger.printer(msg="Removing previous workspace directory", msg_type=Helpers.MSG_INFO)
            try:
                Helpers.remove_dir(p)
            except BuildToolFileAccessError:
                new_name = "{}_{}".format(self.cfg["name"], "AccessDeniedCopy")
                self.cfg["name"] = new_name
                p = os.path.join(WORKSPACE, "{}_{}".format(self.cfg["name"], worker_id))
                logger.printer(msg="Workspace %s is locked and cannot be removed. Changing workspace name to %s" % (
                    "{}_{}".format(self.cfg["name"], "AccessDeniedCopy"), new_name), msg_type=Helpers.MSG_WARNING)
        os.mkdir(p)

        logger.printer(msg="WORKER {} INITIALIZED. Building....".format(worker_id), msg_type=Helpers.MSG_INFO)
        try:
            for job in self.jobs:
                job.work(worker_id=worker_id, logger=logger)
            Helpers.print_build_status(failed=False)
            logger.printer(msg="BUILD SUCCESS", msg_type=Helpers.MSG_INFO)
        except BuildToolError as ex:
            Helpers.print_build_status(msg=str(ex))
            logger.printer(msg="BUILD FAILED", msg_type=Helpers.MSG_ERR)
        logger.kill()


class JobInitializer(Initializer):
    """
        Build tool custom built rule initializer class
    """

    def initialize(self):
        import schedule
        from rules import init
        init()
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
        """
            Telerik Nativescript {NS} job initialization function

            :param cfg: Build configuration
        """
        import jobs
        list_jobs = []
        if cfg["name"] is None or len(cfg["name"]) == 0:
            raise BuildToolError("Invalid build name. Check your configuration file and re-run Build Tool")
        # CHECK FOR GIT CONFIG
        list_jobs.append(JobInitializer.__init_git_job(cfg))
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
    def __init_git_job(cls, cfg):
        """

        :param cfg:
        :return:
        """

        import jobs
        if cfg["repository"] is not None and \
                cfg["username"] is not None and \
                cfg["token"] is not None:
            if cfg["branch"] is None or type(cfg["branch"]) != str or len(cfg["branch"]) == 0:
                cfg["branch"] = "master"
            return jobs.GitJob(cfg["name"], cfg=cfg)
        else:
            raise BuildToolError("Cannot create Git job. Check your configuration file and re-run Build Tool")

    @classmethod
    def __check_timer(cls, cfg):
        if cfg["timer"] is None or type(cfg["timer"]) != int:
            raise BuildToolError("Timer for build %s is not a valid integer" % cfg["name"])

    def __init__(self):
        Initializer.__init__(self)


class WorkerThread(Thread):
    """
        Build Tool worker thread object, representing a single build executor
    """

    def __init__(self, worker_id):
        Thread.__init__(self)
        self.worker_id = worker_id

    def run(self):
        while True:
            executor = Helpers.JOBS.get()
            executor(self.worker_id)
            Helpers.JOBS.task_done()
