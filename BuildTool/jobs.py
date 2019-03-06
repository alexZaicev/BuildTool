from commands import CommandFactory
from helpers import Helpers
from interfaces import Job


class GitJob(Job):

    def work(self, worker_id, logger):
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

    def work(self, worker_id, logger):
        cmd = CommandFactory.get_command(Helpers.CMD_TNS_VERSION)
        cmd.execute(self.cfg, worker_id, logger)
        cmd = CommandFactory.get_command(Helpers.CMD_TNS_INSTALL)
        cmd.execute(self.cfg, worker_id, logger)

        Helpers.execute_pre_build_rules(self.cfg, worker_id, logger)

        cmd = CommandFactory.get_command(Helpers.CMD_TNS_BUILD_ANDROID)
        cmd.execute(self.cfg, worker_id, logger)
        cmd = CommandFactory.get_command(Helpers.CMD_TNS_BUILD_IOS)
        cmd.execute(self.cfg, worker_id, logger)

        Helpers.execute_post_build_rules(self.cfg, worker_id, logger)

        cmd = CommandFactory.get_command(Helpers.CMD_TNS_TEST_ANDROID)
        cmd.execute(self.cfg, worker_id, logger)
        cmd = CommandFactory.get_command(Helpers.CMD_TNS_TEST_IOS)
        cmd.execute(self.cfg, worker_id, logger)

    def __init__(self, name, cfg):
        Job.__init__(self, Helpers.JOB_TNS, "TNS_{}".format(name), cfg=cfg)
