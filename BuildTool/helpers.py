import json
import os
import subprocess
import sys
from datetime import datetime
import queue

# DIRECTORIES
isWin = False
isUnix = False

if sys.platform.lower() == "win32" or sys.platform.lower() == "cygwin":
    isWin = True
elif "linux" in sys.platform.lower() or "darwin" in sys.platform.lower():
    isUnix = True

if isWin:
    ROOT = "C:\\Users\\%s\\AppData\\Local\\BuildTool\\" % os.environ.get('USERNAME')
    WORKSPACE = ROOT + "Workspace\\"
    CONFIG_FILE = ROOT + "config.json"
elif isUnix:
    ROOT = "/usr/local/bin/BuildTool/"
    WORKSPACE = ROOT + "Workspace/"
    CONFIG_FILE = ROOT + "config.json"

PROJECT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__))[:-4], "resources")


class Helpers:
    """
        Build Tool Helper singleton
    """

    PRE_BUILD_RULES = list()
    POST_BUILD_RULES = list()
    CONFIGURATION = None
    JOBS = queue.Queue()

    # TERMINAL COLORS
    RED = "\033[1;31m"
    BLUE = "\033[1;34m"
    CYAN = "\033[1;36m"
    GREEN = "\033[0;32m"
    RESET = "\033[0;0m"
    BOLD = "\033[;1m"
    REVERSE = "\033[;7m"

    # COMMANDS
    CMD_GIT_CLONE = "CMD_0"
    CMD_GIT_FETCH = "CMD_1"
    CMD_GIT_CHECKOUT = "CMD_2"
    CMD_GIT_PULL = "CMD_3"
    CMD_TNS_VERSION = "CMD_4"
    CMD_TNS_INSTALL = "CMD_5"
    CMD_TNS_BUILD_ANDROID = "CMD_6"
    CMD_TNS_BUILD_IOS = "CMD_7"
    CMD_TNS_TEST_ANDROID = "CMD_8"
    CMD_TNS_TEST_IOS = "CMD_9"

    # JOB TYPES
    JOB_GIT = "JOB_0"
    JOB_TNS = "JOB_1"

    MSG_INFO = "INFO"
    MSG_ERR = "ERROR"

    @staticmethod
    def cmd_list(cmd):
        return cmd.split(" ")

    @staticmethod
    def parse_repo(url, user, token):
        """
            Parse GIT repository(HTTPS) with username and token

            :param url: Repository url
            :param user: GitHub username
            :param token: GitHub Access Token
            :return: parsed Git HTTPS url
        """
        return "https://%s:%s@%s" % (
            user, token, url[8:]
        )

    @staticmethod
    def get_repo_name(url):
        """
        Get Repository name from url

        :param url: Repository url
        :return: Repository name
        """
        sa = url.split("/")
        return sa[len(sa) - 1].split(".")[0]

    @staticmethod
    def execute_pre_build_rules(worker_id):
        """
            Pre-Build rules executor
        """
        for br in Helpers.PRE_BUILD_RULES:
            br.execute_rule(worker_id)

    @staticmethod
    def execute_post_build_rules(worker_id):
        """
            Pre-Build rules executor
        """
        for br in Helpers.POST_BUILD_RULES:
            br.execute_rule(worker_id)

    @staticmethod
    def remove_dir(name):
        """
            Directory removing function

            :param name: Directory path
        """

        if isWin:
            os.system("rmdir /Q /S %s" % name)
        elif isUnix:
            os.system("rm -rf %s" % name)

    @staticmethod
    def create_config():
        """
            Generic config generator
        """

        config = {
            "jobs": [
                {
                    "type": None,
                    "name": None,
                    "repository": None,
                    "branch": "master",
                    "username": None,
                    "token": None,
                    "timer": 10,
                    "enabled": False,
                    "android": {
                        "build": False,
                        "test": False
                    },
                    "ios": {
                        "build": False,
                        "test": False
                    }
                }
            ]
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, ensure_ascii=False)
        f.close()

    @staticmethod
    def read_config():
        """
            Configuration file reader

            :return: Configuration dictionary
        """

        with open(CONFIG_FILE, "r") as f:
            cfg = json.load(f)
        f.close()
        return cfg

    @staticmethod
    def print_with_stamp(msg, status):
        """
            Method adds time stamp on the print output

            :param msg: Message to print
            :param status: Message status
        """
        print("%s   ---   %s   ---   %s" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), status, msg))

    @staticmethod
    def print_build_status(failed=True, msg=None):
        """
            Methods prints build status message

            :param failed: Build status
            :param msg: Message to print
        """

        if failed:
            if msg is not None:
                Helpers.print_with_stamp(msg, Helpers.MSG_ERR)
            print("\n\n%s  BUILD FAILED\n" % Helpers.RED)

            # Helpers.send_notification(msg="Build Failed\nSee logs for more details")
        else:
            if msg is not None:
                Helpers.print_with_stamp(msg, Helpers.MSG_INFO)
            print("\n\n%s BUILD SUCCESS\n" % Helpers.GREEN)

            # Helpers.send_notification(msg="Build Success\nSee logs for more details")
        print(Helpers.RESET)

    @staticmethod
    def perform_command(cmd=tuple(), shell=None):
        """
            Shell command executor

            :param cmd: Command, option and argument list
            :param shell:  Is shell command
        """
        if shell is None:
            shell = isWin and not isUnix
        try:
            # out = subprocess.check_output(cmd, shell=shell)
            # return False, str(out, "UTF-8")
            sp = subprocess.Popen(cmd, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            while True:
                line = sp.stdout.readline()
                if not line:
                    break
                print(str(line, "UTF-8"))
            if sp.returncode != 0 and sp.returncode is not None:
                return True, "Build failed with status code {}".format(sp.returncode)
            return False, ""
        except subprocess.CalledProcessError as ex:
            return True, str(ex)

    @staticmethod
    def check_dirs():
        """
            Workspace hierarchy checker
        """

        import interfaces
        if not os.path.exists(ROOT):
            os.mkdir(ROOT)
            os.mkdir(WORKSPACE)
        elif not os.path.exists(WORKSPACE):
            os.mkdir(WORKSPACE)
            Helpers.create_config()
        elif not os.path.exists(CONFIG_FILE):
            Helpers.create_config()
            raise interfaces.BuildToolError("Build Tool not configured")

    # @staticmethod
    # def send_notification(msg):
    #     import plyer
    #     title = "Build Tool Notification"
    #     if isWin:
    #         # from win10toast import ToastNotifier
    #         # tn = ToastNotifier()
    #         # tn.show_toast(title=title, msg=msg)
    #         plyer.notification.notify(
    #             title=title,
    #             message=msg,
    #             timeout=5,
    #             app_name="Build Tool"
    #         )
    #     elif isUnix:
    #         import pync
    #         if "linux" in sys.platform.lower():
    #             Helpers.perform_command(cmd=("notify-send", title, msg), shell=False)
    #         else:
    #             pync.notify(msg, title=title)
