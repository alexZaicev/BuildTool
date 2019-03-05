from commands import CommandFactory
from helpers import Helpers
from interfaces import Job


class GitJob(Job):

    def work(self):
        cmd = CommandFactory.get_command(Helpers.CMD_GIT_CLONE)
        cmd.execute()
        cmd = CommandFactory.get_command(Helpers.CMD_GIT_FETCH)
        cmd.execute()
        cmd = CommandFactory.get_command(Helpers.CMD_GIT_CHECKOUT)
        cmd.execute()
        cmd = CommandFactory.get_command(Helpers.CMD_GIT_PULL)
        cmd.execute()

    def __init__(self, name):
        Job.__init__(self, Helpers.JOB_GIT, "GIT_%s".format(name))


class TnsJob(Job):

    def work(self):
        cmd = CommandFactory.get_command(Helpers.CMD_TNS_VERSION)
        cmd.execute()
        cmd = CommandFactory.get_command(Helpers.CMD_TNS_INSTALL)
        cmd.execute()

        Helpers.execute_pre_build_rules()

        cmd = CommandFactory.get_command(Helpers.CMD_TNS_BUILD_ANDROID)
        cmd.execute()
        cmd = CommandFactory.get_command(Helpers.CMD_TNS_BUILD_IOS)
        cmd.execute()

        Helpers.execute_post_build_rules()

        cmd = CommandFactory.get_command(Helpers.CMD_TNS_TEST_ANDROID)
        cmd.execute()
        cmd = CommandFactory.get_command(Helpers.CMD_TNS_TEST_IOS)
        cmd.execute()

    def __init__(self, name):
        Job.__init__(self, Helpers.JOB_TNS, "TNS_%s".format(name))
