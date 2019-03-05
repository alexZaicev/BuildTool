from commands import CommandFactory
from helpers import Helpers
from interfaces import Job


class GitJob(Job):

    def work(self, worker_id):
        cmd = CommandFactory.get_command(Helpers.CMD_GIT_CLONE)
        cmd.execute(self.cfg)
        cmd = CommandFactory.get_command(Helpers.CMD_GIT_FETCH)
        cmd.execute(self.cfg)
        cmd = CommandFactory.get_command(Helpers.CMD_GIT_CHECKOUT)
        cmd.execute(self.cfg)
        cmd = CommandFactory.get_command(Helpers.CMD_GIT_PULL)
        cmd.execute(self.cfg)

    def __init__(self, name, cfg):
        Job.__init__(self, Helpers.JOB_GIT, "GIT_{}".format(name), cfg=cfg)


class TnsJob(Job):

    def work(self, worker_id):
        cmd = CommandFactory.get_command(Helpers.CMD_TNS_VERSION)
        cmd.execute(self.cfg)
        cmd = CommandFactory.get_command(Helpers.CMD_TNS_INSTALL)
        cmd.execute(self.cfg)

        Helpers.execute_pre_build_rules(worker_id)

        cmd = CommandFactory.get_command(Helpers.CMD_TNS_BUILD_ANDROID)
        cmd.execute(self.cfg)
        cmd = CommandFactory.get_command(Helpers.CMD_TNS_BUILD_IOS)
        cmd.execute(self.cfg)

        Helpers.execute_post_build_rules(worker_id)

        cmd = CommandFactory.get_command(Helpers.CMD_TNS_TEST_ANDROID)
        cmd.execute(self.cfg)
        cmd = CommandFactory.get_command(Helpers.CMD_TNS_TEST_IOS)
        cmd.execute(self.cfg)

    def __init__(self, name, cfg):
        Job.__init__(self, Helpers.JOB_TNS, "TNS_{}".format(name), cfg=cfg)
