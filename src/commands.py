import os

from helpers import Helpers, WORKSPACE
from interfaces import Utils, BuildToolError, Command


class CommandFactory(Utils):

    @staticmethod
    def get_command(cmd_type):
        commands = {
            Helpers.CMD_GIT_CLONE: GitCloneCommand
        }
        try:
            return commands.get(cmd_type)()
        except AttributeError:
            raise BuildToolError("Command of type %s does not exist" % cmd_type)


class GitCloneCommand(Command):

    def execute(self):
        Helpers.print_with_stamp("STARTING GIT CLONE")
        git_url = Helpers.parse_repo(Helpers.CONFIGURATION.get("repository"), Helpers.CONFIGURATION.get("username"),
                                     Helpers.CONFIGURATION.get("token"))
        failed, out = Helpers.perform_command(cmd=Helpers.cmd_list(Helpers.GIT_CLONE % git_url), shell=True)
        if failed:
            raise BuildToolError(
                "Failed to clone repository: %s." % Helpers.CONFIGURATION.get("repository"))
        else:
            Helpers.print_with_stamp(out)
        os.chdir(WORKSPACE + Helpers.get_repo_name(Helpers.CONFIGURATION.get("repository")))

    def __init__(self):
        Command.__init__(self)
