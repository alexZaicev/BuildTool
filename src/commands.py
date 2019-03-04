import os

from helpers import Helpers, WORKSPACE
from interfaces import Utils, BuildToolError, Command


class CommandFactory(Utils):

    @staticmethod
    def get_command(cmd_type):
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

    def execute(self):
        Helpers.print_with_stamp("STARTING GIT CLONE")
        git_url = Helpers.parse_repo(Helpers.CONFIGURATION.get("repository"), Helpers.CONFIGURATION.get("username"),
                                     Helpers.CONFIGURATION.get("token"))
        print(git_url)
        failed, out = Helpers.perform_command(cmd=Helpers.cmd_list("git clone %s" % git_url))
        if failed:
            raise BuildToolError(
                "Failed to clone repository: %s." % Helpers.CONFIGURATION.get("repository"))
        else:
            Helpers.print_with_stamp(out)
        os.chdir(WORKSPACE + Helpers.get_repo_name(Helpers.CONFIGURATION.get("repository")))

    def __init__(self):
        Command.__init__(self)


class GitFetchCommand(Command):

    def execute(self):
        Helpers.print_with_stamp("STARTING GIT FETCH")
        failed, out = Helpers.perform_command(cmd=Helpers.cmd_list("git fetch"))
        if failed:
            raise BuildToolError("Failed to fetch from repository.")
        else:
            Helpers.print_with_stamp(out)

    def __init__(self):
        Command.__init__(self)


class GitCheckoutCommand(Command):

    def execute(self):
        Helpers.print_with_stamp("STARTING GIT CHECKOUT")
        failed, out = Helpers.perform_command(
            cmd=Helpers.cmd_list("git checkout %s" % Helpers.CONFIGURATION.get("branch")))
        if failed:
            raise BuildToolError(
                "Failed to checkout to branch [%s]." % Helpers.CONFIGURATION.get("branch"))
        else:
            Helpers.print_with_stamp(out)

    def __init__(self):
        Command.__init__(self)


class GitPullCommand(Command):

    def execute(self):
        Helpers.print_with_stamp("STARTING GIT PULL")
        failed, out = Helpers.perform_command(
            cmd=Helpers.cmd_list("git pull origin %s" % Helpers.CONFIGURATION.get("branch")))
        if failed:
            raise BuildToolError(
                "Failed to pull from branch [%s]." % Helpers.CONFIGURATION.get("branch"))
        else:
            Helpers.print_with_stamp(out)

    def __init__(self):
        Command.__init__(self)


class TnsVersionCommand(Command):
    def execute(self):
        # CHECK IF {NS} IS PRESENT BY CHECKING VERSION
        Helpers.print_with_stamp("STARTING {NS} VERSION CHECK")
        failed, out = Helpers.perform_command(cmd="tns --version", shell=True)
        if failed:
            raise BuildToolError("Check if {NS} is installed on your machine")
        else:
            Helpers.print_with_stamp(out)

    def __init__(self):
        Command.__init__(self)


class TnsInstallCommand(Command):
    def execute(self):
        # {NS} INSTALL DEPENDENCIES
        Helpers.print_with_stamp("STARTING {NS} INSTALL")
        failed, out = Helpers.perform_command(cmd="tns install", shell=True)
        if failed:
            raise BuildToolError("{NS} failed to install project dependencies")
        else:
            Helpers.print_with_stamp(out)

    def __init__(self):
        Command.__init__(self)


class TnsBuildAndroidCommand(Command):

    def execute(self):
        # ANDROID BUILD
        if Helpers.CONFIGURATION.get("build").get("android").get("build"):
            Helpers.print_with_stamp("STARTING BUILD ANDROID")
            failed, out = Helpers.perform_command(cmd=("tns build %s" % "android"), shell=True)
            if failed:
                raise BuildToolError("{NS} failed to build project for android")
            else:
                Helpers.print_with_stamp(out)
        else:
            Helpers.print_with_stamp("Android build is disabled in configuration file. Enable it and re-run the build")

    def __init__(self):
        Command.__init__(self)


class TnsBuildIosCommand(Command):

    def execute(self):
        # IOS BUILD
        if Helpers.CONFIGURATION.get("build").get("ios").get("build"):
            Helpers.print_with_stamp("STARTING BUILD IOS")
            failed, out = Helpers.perform_command(cmd=("tns build %s" % "ios"), shell=True)
            if failed:
                raise BuildToolError("{NS} failed to build project for iOS")
            else:
                Helpers.print_with_stamp(out)
        else:
            Helpers.print_with_stamp("iOS build is disabled in configuration file. Enable it and re-run the build")

    def __init__(self):
        Command.__init__(self)


class TnsTestAndroidCommand(Command):

    def execute(self):
        # ANDROID TEST
        if Helpers.CONFIGURATION.get("build").get("android").get("test"):
            Helpers.print_with_stamp("STARTING TEST ANDROID")
            failed, out = Helpers.perform_command(cmd=("tns test %s" % "android"), shell=True)
            if failed:
                raise BuildToolError("{NS} failed to test project for android")
            else:
                Helpers.print_with_stamp(out)
        else:
            Helpers.print_with_stamp("Android test is disabled in configuration file. Enable it and re-run the build")

    def __init__(self):
        Command.__init__(self)


class TnsTestIosCommand(Command):

    def execute(self):
        # ANDROID TEST
        if Helpers.CONFIGURATION.get("build").get("ios").get("test"):
            Helpers.print_with_stamp("STARTING TEST IOS")
            failed, out = Helpers.perform_command(cmd=("tns test %s" % "ios"), shell=True)
            if failed:
                raise BuildToolError("{NS} failed to test project for iOS")
            else:
                Helpers.print_with_stamp(out)
        else:
            Helpers.print_with_stamp("iOS test is disabled in configuration file. Enable it and re-run the build")

    def __init__(self):
        Command.__init__(self)





