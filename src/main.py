import os

from helpers import Helpers
from helpers import ROOT, WORKSPACE, CONFIG_FILE
from commands import CommandFactory
from interfaces import BuildToolError, RuleInitializer


# a8fad7ba40c641658ab5e4db1332c139fb0376a0


def main():
    check_dirs()
    Helpers.CONFIGURATION = Helpers.read_config()
    Helpers.RULE_INITIALIZER = RuleInitializer()
    Helpers.RULE_INITIALIZER.initialize()
    # init first run
    job()
    # run every 10 minutes
    # schedule.every(Helpers.CONFIGURATION.get("build").get("timer")).minutes.do(job)
    # while True:
    #     schedule.run_pending()


def check_dirs():
    if not os.path.exists(ROOT):
        os.mkdir(ROOT)
        os.mkdir(WORKSPACE)
    elif not os.path.exists(WORKSPACE):
        os.mkdir(WORKSPACE)
        Helpers.create_config()
    elif not os.path.exists(CONFIG_FILE):
        Helpers.create_config()
        raise BuildToolError("Build Tool not configured")


def job():
    os.chdir(WORKSPACE)
    if os.path.exists(WORKSPACE + Helpers.get_repo_name(Helpers.CONFIGURATION.get("repository"))):
        Helpers.remove_dir(WORKSPACE + Helpers.get_repo_name(Helpers.CONFIGURATION.get("repository")))
    try:
        do_git()
        do_job()
        Helpers.print_build_status(failed=False)
    except BuildToolError as ex:
        Helpers.print_build_status(msg=str(ex))


def do_git():
    # GIT CLONE
    cmd = CommandFactory.get_command(Helpers.CMD_GIT_CLONE)
    cmd.execute()
    # Helpers.print_with_stamp("STARTING GIT CLONE")
    # git_url = Helpers.parse_repo(Helpers.CONFIGURATION.get("repository"), Helpers.CONFIGURATION.get("username"),
    #                              Helpers.CONFIGURATION.get("token"))
    # failed, out = Helpers.perform_command(cmd=Helpers.cmd_list(Helpers.GIT_CLONE % git_url), shell=True)
    # if failed:
    #     raise BuildToolError(
    #         "Failed to clone repository: %s." % Helpers.CONFIGURATION.get("repository"))
    # else:
    #     Helpers.print_with_stamp(out)
    # os.chdir(Helpers.WORKSPACE + Helpers.get_repo_name(Helpers.CONFIGURATION.get("repository")))

    # GIT FETCH
    Helpers.print_with_stamp("STARTING GIT FETCH")
    failed, out = Helpers.perform_command(cmd=Helpers.cmd_list(Helpers.GIT_FETCH), shell=True)
    if failed:
        raise BuildToolError("Failed to fetch from repository.")
    else:
        Helpers.print_with_stamp(out)

    # GIT CHECKOUT
    Helpers.print_with_stamp("STARTING GIT CHECKOUT")
    failed, out = Helpers.perform_command(
        cmd=Helpers.cmd_list(Helpers.GIT_CHECKOUT % Helpers.CONFIGURATION.get("branch")),
        shell=True)
    if failed:
        raise BuildToolError(
            "Failed to checkout to branch [%s]." % Helpers.CONFIGURATION.get("branch"))
    else:
        Helpers.print_with_stamp(out)

    # GIT PULL
    Helpers.print_with_stamp("STARTING GIT PULL")
    failed, out = Helpers.perform_command(cmd=Helpers.cmd_list(Helpers.GIT_PULL % Helpers.CONFIGURATION.get("branch")),
                                          shell=True)
    if failed:
        raise BuildToolError(
            "Failed to pull from branch [%s]." % Helpers.CONFIGURATION.get("branch"))
    else:
        Helpers.print_with_stamp(out)


def do_job():
    # CHECK IF {NS} IS PRESENT BY CHECKING VERSION
    Helpers.print_with_stamp("STARTING {NS} VERSION CHECK")
    failed, out = Helpers.perform_command(cmd=Helpers.TNS_VERSION, shell=True)
    if failed:
        raise BuildToolError("Check if {NS} is installed on your machine")
    else:
        Helpers.print_with_stamp(out)

    # {NS} INSTALL DEPENDENCIES
    Helpers.print_with_stamp("STARTING {NS} INSTALL")
    failed, out = Helpers.perform_command(cmd=Helpers.TNS_INSTALL, shell=True)
    if failed:
        raise BuildToolError("{NS} failed to install project dependencies")
    else:
        Helpers.print_with_stamp(out)

    # EXECUTE BUILD SPECIFIC RULES
    Helpers.print_with_stamp("EXECUTING BUILD RULES")
    Helpers.execute_build_rules()

    # {NS} BUILD AND TEST
    if Helpers.CONFIGURATION.get("build").get("android").get("build"):
        Helpers.print_with_stamp("STARTING BUILD ANDROID")
        failed, out = Helpers.perform_command(cmd=(Helpers.TNS_BUILD % Helpers.ANDROID), shell=True)
        if failed:
            raise BuildToolError("{NS} failed to build project for android")
        else:
            Helpers.print_with_stamp(out)

        # ANDROID TEST
        Helpers.print_with_stamp("STARTING TEST ANDROID")
        if Helpers.CONFIGURATION.get("build").get("android").get("test"):
            failed, out = Helpers.perform_command(cmd=(Helpers.TNS_TEST % Helpers.ANDROID), shell=True)
            if failed:
                raise BuildToolError("{NS} failed to test project for android")
            else:
                Helpers.print_with_stamp(out)

    if Helpers.CONFIGURATION.get("build").get("ios").get("build"):
        Helpers.print_with_stamp("STARTING BUILD IOS")
        failed, out = Helpers.perform_command(cmd=(Helpers.TNS_BUILD % Helpers.IOS), shell=True)
        if failed:
            raise BuildToolError("{NS} failed to build project for iOS")
        else:
            Helpers.print_with_stamp(out)

        # IOS TEST
        Helpers.print_with_stamp("STARTING BUILD IOS")
        if Helpers.CONFIGURATION.get("build").get("android").get("test"):
            failed, out = Helpers.perform_command(cmd=(Helpers.TNS_TEST % Helpers.IOS), shell=True)
            if failed:
                raise BuildToolError("{NS} failed to test project for iOS")
            else:
                Helpers.print_with_stamp(out)


if __name__ == "__main__":
    main()
