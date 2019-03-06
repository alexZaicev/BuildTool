"""
    Product Name: BuildTool
    Author: Aleksej Zaicev

    Copyright 2019
"""

import os

from helpers import Helpers, WORKSPACE
from interfaces import Utils, BuildToolError, Command


class CommandFactory(Utils):
    """
        Command Factory Singleton
    """

    @staticmethod
    def get_command(cmd_type):
        """
            Method ro create new Build Tool command

            :param cmd_type: Command type
            :return: Build Tool Command
        """

        commands = {
            Helpers.CMD_GIT_CLONE: GitCloneCommand,
            Helpers.CMD_GIT_FETCH: GitFetchCommand,
            Helpers.CMD_GIT_CHECKOUT: GitCheckoutCommand,
            Helpers.CMD_GIT_PULL: GitPullCommand,
            Helpers.CMD_TNS_VERSION: TnsVersionCommand,
            Helpers.CMD_TNS_INSTALL: TnsInstallCommand,
            Helpers.CMD_TNS_BUILD_ANDROID: TnsBuildAndroidCommand,
            Helpers.CMD_TNS_BUILD_IOS: TnsBuildIosCommand,
            Helpers.CMD_TNS_TEST_ANDROID: TnsTestAndroidCommand,
            Helpers.CMD_TNS_TEST_IOS: TnsTestIosCommand
        }
        try:
            return commands.get(cmd_type)()
        except AttributeError:
            raise BuildToolError("Command of type %s does not exist" % cmd_type)


class GitCloneCommand(Command):
    """
        Git Clone Command:
            git clone {url}
    """

    def execute(self, cfg=None, worker_id=0, logger=None):
        logger.printer("STARTING GIT CLONE", Helpers.MSG_INFO)

        git_url = Helpers.parse_repo(cfg["repository"], cfg["username"], cfg["token"])
        path = os.path.join(WORKSPACE, "{}_{}".format(cfg["name"], worker_id))
        failed, out = Helpers.perform_command(cmd=Helpers.cmd_list("git clone %s %s" % (git_url, path)))
        if failed:
            raise BuildToolError(
                "Failed to clone repository: %s." % cfg["repository"])
        else:
            logger.printer(out, Helpers.MSG_INFO)

    def __init__(self):
        Command.__init__(self)


class GitFetchCommand(Command):
    """
        Git Fetch Command:
            git fetch
    """

    def execute(self, cfg=None, worker_id=0, logger=None):
        logger.printer("STARTING GIT FETCH", Helpers.MSG_INFO)
        path = os.path.join(WORKSPACE, "{}_{}".format(cfg["name"], worker_id),
                            ".git")
        failed, out = Helpers.perform_command(cmd=Helpers.cmd_list("git --git-dir=%s fetch" % path))
        if failed:
            raise BuildToolError("Failed to fetch from repository.")
        else:
            logger.printer(out, Helpers.MSG_INFO)

    def __init__(self):
        Command.__init__(self)


class GitCheckoutCommand(Command):
    """
        Git Checkout Command:
            git checkout {branch}
    """

    def execute(self, cfg=None, worker_id=0, logger=None):
        logger.printer("STARTING GIT CHECKOUT", Helpers.MSG_INFO)
        path = os.path.join(WORKSPACE, "{}_{}".format(cfg["name"], worker_id), ".git")
        failed, out = Helpers.perform_command(
            cmd=Helpers.cmd_list("git --git-dir=%s checkout %s" % (path, cfg["branch"])))
        if failed:
            raise BuildToolError(
                "Failed to checkout to branch [%s]." % cfg["branch"])
        else:
            logger.printer(out, Helpers.MSG_INFO)

    def __init__(self):
        Command.__init__(self)


class GitPullCommand(Command):
    """
        Git Pull Command:
            git pull origin {branch}
    """

    def execute(self, cfg=None, worker_id=0, logger=None):
        logger.printer("STARTING GIT PULL", Helpers.MSG_INFO)
        path = os.path.join(WORKSPACE, "{}_{}".format(cfg["name"], worker_id), ".git")
        failed, out = Helpers.perform_command(
            cmd=Helpers.cmd_list("git --git-dir=%s pull origin %s" % (path, cfg["branch"])))
        if failed:
            raise BuildToolError(
                "Failed to pull from branch [%s]." % cfg["branch"])
        else:
            logger.printer(out, Helpers.MSG_INFO)

    def __init__(self):
        Command.__init__(self)


class TnsVersionCommand(Command):
    """
        {NS} Version Command:
            tns --version
    """

    def execute(self, cfg=None, worker_id=0, logger=None):
        # CHECK IF {NS} IS PRESENT BY CHECKING VERSION
        logger.printer("STARTING {NS} VERSION CHECK", Helpers.MSG_INFO)
        path = os.path.join(WORKSPACE, "{}_{}".format(cfg["name"], worker_id))
        cmd = "tns --version --path {}".format(path)
        failed, out = Helpers.perform_command(cmd=cmd, shell=True)
        if failed:
            raise BuildToolError("Check if {NS} is installed on your machine")
        else:
            logger.printer(out, Helpers.MSG_INFO)

    def __init__(self):
        Command.__init__(self)


class TnsInstallCommand(Command):
    """
        {NS} Install Command:
            tns install
    """

    def execute(self, cfg=None, worker_id=0, logger=None):
        # {NS} INSTALL DEPENDENCIES
        logger.printer("STARTING {NS} INSTALL", Helpers.MSG_INFO)
        path = os.path.join(WORKSPACE, "{}_{}".format(cfg["name"], worker_id))
        cmd = "tns install --path {}".format(path)
        failed, out = Helpers.perform_command(cmd=cmd, shell=True)
        if failed:
            raise BuildToolError("{NS} failed to install project dependencies")
        else:
            logger.printer(out, Helpers.MSG_INFO)

    def __init__(self):
        Command.__init__(self)


class TnsBuildAndroidCommand(Command):
    """
        {NS} Build Android Command:
            tns build android
    """

    def execute(self, cfg=None, worker_id=0, logger=None):
        # ANDROID BUILD
        if cfg["android"]["build"]:
            logger.printer("STARTING BUILD ANDROID", Helpers.MSG_INFO)
            path = os.path.join(WORKSPACE, "{}_{}".format(cfg["name"], worker_id))
            cmd = "tns build android --path {}".format(path)
            failed, out = Helpers.perform_command(cmd=cmd, shell=True)
            if failed:
                raise BuildToolError("{NS} failed to build project for android")
            else:
                logger.printer(out, Helpers.MSG_INFO)
        else:
            logger.printer("Android build is disabled in configuration file. Enable it and re-run the build",
                           Helpers.MSG_INFO)

    def __init__(self):
        Command.__init__(self)


class TnsBuildIosCommand(Command):
    """
        {NS} Build iOS Command:
            tns build ios
    """

    def execute(self, cfg=None, worker_id=0, logger=None):
        # IOS BUILD
        if cfg["ios"]["build"]:
            logger.printer("STARTING BUILD IOS", Helpers.MSG_INFO)
            path = os.path.join(WORKSPACE, "{}_{}".format(cfg["name"], worker_id))
            cmd = "tns build ios --path {}".format(path)
            failed, out = Helpers.perform_command(cmd=cmd, shell=True)
            if failed:
                raise BuildToolError("{NS} failed to build project for iOS")
            else:
                logger.printer(out, Helpers.MSG_INFO)
        else:
            logger.printer("iOS build is disabled in configuration file. Enable it and re-run the build",
                           Helpers.MSG_INFO)

    def __init__(self):
        Command.__init__(self)


class TnsTestAndroidCommand(Command):
    """
        {NS} Test Android Command:
            tns test android
    """

    def execute(self, cfg=None, worker_id=0, logger=None):
        # ANDROID TEST
        if cfg["android"]["test"]:
            logger.printer("STARTING TEST ANDROID", Helpers.MSG_INFO)
            path = os.path.join(WORKSPACE, "{}_{}".format(cfg["name"], worker_id))
            cmd = "tns test android --path {}".format(path)
            failed, out = Helpers.perform_command(cmd=cmd, shell=True)
            if failed:
                raise BuildToolError("{NS} failed to test project for android")
            else:
                logger.printer(out, Helpers.MSG_INFO)
        else:
            logger.printer("Android test is disabled in configuration file. Enable it and re-run the build",
                           Helpers.MSG_INFO)

    def __init__(self):
        Command.__init__(self)


class TnsTestIosCommand(Command):
    """
        {NS} Test iOS Command:
            tns test iOS
    """

    def execute(self, cfg=None, worker_id=0, logger=None):
        # ANDROID TEST
        if cfg["ios"]["test"]:
            logger.printer("STARTING TEST IOS", Helpers.MSG_INFO)
            path = os.path.join(WORKSPACE, "{}_{}".format(cfg["name"], worker_id))
            cmd = "tns test ios --path {}".format(path)
            failed, out = Helpers.perform_command(cmd=cmd, shell=True)
            if failed:
                raise BuildToolError("{NS} failed to test project for iOS")
            else:
                logger.printer(out, Helpers.MSG_INFO)
        else:
            logger.printer("iOS test is disabled in configuration file. Enable it and re-run the build",
                           Helpers.MSG_INFO)

    def __init__(self):
        Command.__init__(self)
