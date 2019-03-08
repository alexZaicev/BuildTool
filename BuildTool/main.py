"""
    Product Name: BuildTool
    Author: Aleksej Zaicev

    Copyright 2019
"""

import time

from helpers import Helpers
from interfaces import BuildToolError, JobInitializer, WorkerThread


worker_1 = WorkerThread(1)
worker_2 = WorkerThread(2)
worker_3 = WorkerThread(3)


def main():
    """
        Main application start up method
    """

    Helpers.print_with_stamp(msg="Initializing Build Tool Environment", status=Helpers.MSG_INFO)
    try:
        """ Prepare working directories and load configuration file
        """
        Helpers.check_dirs()
        Helpers.CONFIGURATION = Helpers.read_config()
        """ Initialize jobs and workers
        """
        job_init = JobInitializer()
        scheduler = job_init.initialize()

        worker_1.start()
        # worker_2.start()
        # worker_3.start()
        scheduler.run_all(60)
        while True:
            """ Build tool loop
            """
            scheduler.run_pending()
            time.sleep(10)

    except BuildToolError as ex:
        Helpers.print_build_status(msg=str(ex))
    except AttributeError:
        Helpers.print_build_status(
            msg="Invalid configuration file format. Check the format of the file and re-run the tool")


if __name__ == "__main__":
    main()
