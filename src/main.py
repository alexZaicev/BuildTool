import os

from helpers import Helpers
from helpers import ROOT, WORKSPACE, CONFIG_FILE
from commands import CommandFactory
from interfaces import BuildToolError, RuleInitializer


def main():
    check_dirs()
    Helpers.CONFIGURATION = Helpers.read_config()
    Helpers.RULE_INITIALIZER = RuleInitializer()
    Helpers.RULE_INITIALIZER.initialize()
    # init first run
    job()
    # configure scheduler
    schedule.every(Helpers.CONFIGURATION.get("build").get("timer")).minutes.do(job)
    while True:
        schedule.run_pending()


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
    cmd = CommandFactory.get_command(Helpers.CMD_GIT_CLONE)
    cmd.execute()
    cmd = CommandFactory.get_command(Helpers.CMD_GIT_FETCH)
    cmd.execute()
    cmd = CommandFactory.get_command(Helpers.CMD_GIT_CHECKOUT)
    cmd.execute()
    cmd = CommandFactory.get_command(Helpers.CMD_GIT_PULL)
    cmd.execute()


def do_job():
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


if __name__ == "__main__":
    main()
