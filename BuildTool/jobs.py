"""
    Product Name: BuildTool
    Author: Aleksej Zaicev

    Copyright 2019
"""

from commands import CommandFactory
from helpers import Helpers
from interfaces import Job
import time


class GitJob(Job):
    """
        Git command executing job. Clones the repository and pulls the latest changes from specified branch
    """

    def work(self, worker_id, logger):
        """
            Job executor containing sequence of command needed to be performed

            :param worker_id: Working thread ID
            :param logger: Working thread logger
        """
        cmd = CommandFactory.get_command(Helpers.CMD_GIT_CLONE)
        cmd.execute(self.cfg, worker_id, logger)
        cmd = CommandFactory.get_command(Helpers.CMD_GIT_FETCH)
        cmd.execute(self.cfg, worker_id, logger)
        cmd = CommandFactory.get_command(Helpers.CMD_GIT_CHECKOUT)
        cmd.execute(self.cfg, worker_id, logger)
        cmd = CommandFactory.get_command(Helpers.CMD_GIT_PULL)
        cmd.execute(self.cfg, worker_id, logger)

    def __init__(self, name, cfg):
        Job.__init__(self, Helpers.JOB_GIT, "GIT_{}".format(name), cfg=cfg)


class TnsJob(Job):
    """
        Telerik Nativescript {NS} command executing job. Job installs project dependencies specified in `package.json`
        file, build and test project for both Android and iOS.
    """

    def work(self, worker_id, logger):
        from interfaces import BuildToolError

        cmd = CommandFactory.get_command(Helpers.CMD_TNS_VERSION)
        cmd.execute(self.cfg, worker_id, logger)

        cmd = CommandFactory.get_command(Helpers.CMD_TNS_DOCTOR)
        cmd.execute(self.cfg, worker_id, logger)

        cmd = CommandFactory.get_command(Helpers.CMD_TNS_INSTALL)
        cmd.execute(self.cfg, worker_id, logger)

        try:
            Helpers.execute_pre_build_rules(self.cfg, worker_id, logger)
            time.sleep(5)
        except Exception:
            raise BuildToolError("Build Tool failed to execute pre-build rule for build %s" % self.cfg["name"])

        cmd = CommandFactory.get_command(Helpers.CMD_TNS_BUILD_ANDROID)
        cmd.execute(self.cfg, worker_id, logger)
        cmd = CommandFactory.get_command(Helpers.CMD_TNS_BUILD_IOS)
        cmd.execute(self.cfg, worker_id, logger)

        try:
            Helpers.execute_post_build_rules(self.cfg, worker_id, logger)
            time.sleep(5)
        except Exception:
            raise BuildToolError("Build Tool failed to execute post-build rule for build %s" % self.cfg["name"])

        cmd = CommandFactory.get_command(Helpers.CMD_TNS_BUNDLE_ANDROID)
        cmd.execute(self.cfg, worker_id, logger)
        cmd = CommandFactory.get_command(Helpers.CMD_TNS_BUNDLE_IOS)
        cmd.execute(self.cfg, worker_id, logger)

        cmd = CommandFactory.get_command(Helpers.CMD_TNS_TEST_ANDROID)
        cmd.execute(self.cfg, worker_id, logger)
        cmd = CommandFactory.get_command(Helpers.CMD_TNS_TEST_IOS)
        cmd.execute(self.cfg, worker_id, logger)

    def __init__(self, name, cfg):
        Job.__init__(self, Helpers.JOB_TNS, "TNS_{}".format(name), cfg=cfg)
