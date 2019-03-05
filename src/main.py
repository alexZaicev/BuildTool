import os
import time

import schedule

from helpers import Helpers
from helpers import WORKSPACE
from interfaces import BuildToolError, RuleInitializer, JobInitializer


def main():
    Helpers.send_notification(title="Builder Started", msg="Initializing Build Tool Environment")

    Helpers.check_dirs()
    Helpers.CONFIGURATION = Helpers.read_config()
    rule_init = RuleInitializer()
    rule_init.initialize()

    job_init = JobInitializer()
    job_init.initialize()
    # configure scheduler
    schedule.every(Helpers.CONFIGURATION.get("build").get("nativescript").get("timer")).minutes.do(job)
    schedule.run_all(5)
    while True:
        schedule.run_pending()
        time.sleep(10)


def job():
    os.chdir(WORKSPACE)
    if os.path.exists(WORKSPACE + Helpers.get_repo_name(Helpers.CONFIGURATION.get("repository"))):
        Helpers.remove_dir(WORKSPACE + Helpers.get_repo_name(Helpers.CONFIGURATION.get("repository")))
    try:
        Helpers.trigger_jobs()
        Helpers.print_build_status(failed=False)
    except BuildToolError as ex:
        Helpers.print_build_status(msg=str(ex))


if __name__ == "__main__":
    main()
