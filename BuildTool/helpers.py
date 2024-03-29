"""
    Product Name: BuildTool
    Author: Aleksej Zaicev

    Copyright 2019
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime
import queue
from collections import namedtuple

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
    LOGS = ROOT + "Logs\\"
    CONFIG_FILE = ROOT + "config.json"
elif isUnix:
    ROOT = "/usr/local/bin/BuildTool/"
    WORKSPACE = ROOT + "Workspace/"
    LOGS = ROOT + "Logs/"
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
    CMD_TNS_DOCTOR = "CMD_10"
    CMD_TNS_BUNDLE_ANDROID = "CMD_11"
    CMD_TNS_BUNDLE_IOS = "CMD_12"

    # JOB TYPES
    JOB_GIT = "JOB_0"
    JOB_TNS = "JOB_1"

    MSG_INFO = "INFO"
    MSG_ERR = "ERROR"
    MSG_WARNING = "WARNING"

    def __new__(cls, *args, **kwargs):
        from interfaces import BuildToolError
        raise BuildToolError("Cannot instantiate static classes")

    def __init__(self):
        from interfaces import BuildToolError
        raise BuildToolError("Cannot instantiate static classes")

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
    def execute_pre_build_rules(cfg, worker_id, logger):
        """
            Pre-Build rules executor
        """

        logger.printer("Executing pre-build rules", Helpers.MSG_INFO)
        for br in Helpers.PRE_BUILD_RULES:
            br.execute_rule(cfg, worker_id, logger)

    @staticmethod
    def execute_post_build_rules(cfg, worker_id, logger):
        """
            Pre-Build rules executor
        """
        logger.printer("Executing post-build rules", Helpers.MSG_INFO)
        for br in Helpers.POST_BUILD_RULES:
            br.execute_rule(cfg, worker_id, logger)

    @staticmethod
    def remove_dir(name):
        """
            Directory removing function

            :param name: Directory path
        """

        from interfaces import BuildToolFileAccessError, BuildToolError
        failed, out = True, None
        try:
            if isWin:
                failed, out = Helpers.perform_command(("rmdir", "/Q", "/S", name), shell=True)
            elif isUnix:
                failed, out = Helpers.perform_command(("rm", "-rf", name))
            if failed:
                if "ACCESS" in out:
                    raise BuildToolFileAccessError()
                else:
                    raise BuildToolError("Failed to remove directory %s" % name)
        except subprocess.CalledProcessError:
            from interfaces import BuildToolError
            raise BuildToolError("Failed to remove directory %s" % name)

    @staticmethod
    def remove_file(name):
        """
            File removing function

            :param name: Directory path
        """

        from interfaces import BuildToolFileAccessError, BuildToolError
        failed, out = True, None
        try:
            if isWin:
                failed, out = Helpers.perform_command(("del", "/f", name), shell=True)
            elif isUnix:
                failed, out = Helpers.perform_command(("rm", "-f", name))
            if failed:
                if "ACCESS" in out:
                    raise BuildToolFileAccessError()
                else:
                    raise BuildToolError("Failed to remove file %s" % name)
        except subprocess.CalledProcessError:
            from interfaces import BuildToolError
            raise BuildToolError("Failed to remove file %s" % name)

    @staticmethod
    def json_converter(data, typename):
        def __json_object_hook(d):
            return namedtuple(typename=typename, field_names=d.keys())(*d.values())

        return json.load(data, object_hook=__json_object_hook)

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
                        "webpack": {
                            "bundle": False,
                            "uglify": False
                        },
                        "test": False
                    },
                    "ios": {
                        "build": False,
                        "webpack": {
                            "bundle": False,
                            "uglify": False
                        },
                        "test": False
                    }
                }
            ]
        }
        with open(CONFIG_FILE, 'w+') as f:
            json.dump(config, f, ensure_ascii=False)
        f.close()

    @staticmethod
    def read_config():
        """
            Configuration file reader

            :return: Configuration dictionary
        """

        from interfaces import BuildToolError
        try:
            with open(CONFIG_FILE, "r") as f:
                cfg = json.load(f)
            f.close()
        except json.JSONDecodeError or FileNotFoundError:
            raise BuildToolError(
                "Build Tool failed to load configuration. Ensure you set" +
                " your configuration correctly and re-run the Build Tool")
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
            Helpers.print_with_stamp("%sBUILD FAILED" % Helpers.RED, Helpers.MSG_ERR)
        else:
            if msg is not None:
                Helpers.print_with_stamp(msg, Helpers.MSG_INFO)
            Helpers.print_with_stamp("%sBUILD SUCCESS" % Helpers.GREEN, Helpers.MSG_INFO)
        print(Helpers.RESET)

    @staticmethod
    def perform_command(cmd=tuple(), shell=None, logger=None):
        """
            Shell command executor

            :param cmd: Command, option and argument list
            :param shell:  Is shell command
            :param logger: Worker logger
        """
        if shell is None:
            shell = isWin and not isUnix
        try:
            sp = subprocess.Popen(cmd, shell=shell, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT)
            while True:
                if sp.stderr is not None:
                    line = sp.stderr.readline()
                    if line:
                        if sp.returncode != 0 and sp.returncode is not None:
                            return True, "Build failed with status code {}".format(sp.returncode)

                line = str(sp.stdout.readline(), "UTF-8")[:-1]
                if not line and sp.poll() is not None:
                    break
                elif "BUILD" in line and "FAILED" in line:
                    return True, "Build failed with status code {}".format(sp.returncode)
                elif "process cannot access the file" in line:
                    return True, "ACCESS"

                if len(line) > 0:
                    if logger is None:
                        Helpers.print_with_stamp(msg=line, status=Helpers.MSG_INFO)
                    else:
                        logger.printer(msg=line, msg_type=Helpers.MSG_INFO)
            sp.kill()
        except subprocess.CalledProcessError as ex:
            return True, str(ex)
        return False, ""

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

        if not os.path.exists(LOGS):
            os.mkdir(LOGS)
