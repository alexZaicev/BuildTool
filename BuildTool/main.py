import time

from helpers import Helpers
from interfaces import BuildToolError, JobInitializer, WorkerThread


def main():
    # Helpers.send_notification(msg="Initializing Build Tool Environment")
    Helpers.print_with_stamp(msg="Initializing Build Tool Environment", status=Helpers.MSG_INFO)
    try:
        Helpers.check_dirs()
        Helpers.CONFIGURATION = Helpers.read_config()

        job_init = JobInitializer()
        scheduler = job_init.initialize()

        worker_1 = WorkerThread(1)
        worker_2 = WorkerThread(2)
        worker_3 = WorkerThread(3)

        worker_1.start()
        worker_2.start()
        worker_3.start()

        while True:
            scheduler.run_pending()
            time.sleep(1)

    except BuildToolError as ex:
        Helpers.print_build_status(msg=str(ex))
    except AttributeError:
        Helpers.print_build_status(
            msg="Invalid configuration file format. Check the format of the file and re-run the tool")


if __name__ == "__main__":
    main()
