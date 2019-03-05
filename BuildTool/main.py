import os
import time

import schedule

from helpers import Helpers
from helpers import WORKSPACE
from interfaces import BuildToolError, JobInitializer


def main():
    Helpers.send_notification(msg="Initializing Build Tool Environment")
    try:
        Helpers.check_dirs()
        Helpers.CONFIGURATION = Helpers.read_config()
        job_init = JobInitializer()
        job_init.initialize()
        # configure scheduler
        schedule.every(Helpers.CONFIGURATION.get("build").get("nativescript").get("timer")).minutes.do(job)
        schedule.run_all(5)
        while True:
            schedule.run_pending()
            time.sleep(10)
    except BuildToolError as ex:
        Helpers.print_build_status(msg=str(ex))


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
