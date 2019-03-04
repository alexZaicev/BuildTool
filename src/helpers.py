import json
import os
import subprocess
import sys
from datetime import datetime

"""
    Directories
"""
isWin = False
isUnix = False

if sys.platform.lower() == "win32" or sys.platform.lower() == "cygwin":
    isWin = True
elif sys.platform.lower() == "linux" or sys.platform.lower() == "darwin":
    isUnix = True

if isWin:
    ROOT = "C:\\Users\\%s\\AppData\\Local\\BuildTool\\" % os.environ.get('USERNAME')
    WORKSPACE = ROOT + "Workspace\\"
    CONFIG_FILE = ROOT + "config.json"
elif isUnix:
    ROOT = "/usr/local/bin/BuildTool/"
    WORKSPACE = ROOT + "Workspace/"
    CONFIG_FILE = ROOT + "config.json"


class Helpers:
    BUILD_RULES = list()
    RULE_INITIALIZER = None
    CONFIGURATION = None

    """
        Terminal Colors
    """
    RED = "\033[1;31m"
    BLUE = "\033[1;34m"
    CYAN = "\033[1;36m"
    GREEN = "\033[0;32m"
    RESET = "\033[0;0m"
    BOLD = "\033[;1m"
    REVERSE = "\033[;7m"

    """
        Git Commands
    """
    GIT_CLONE = "git clone %s"
    GIT_FETCH = "git fetch"
    GIT_PULL = "git pull origin %s"
    GIT_CHECKOUT = "git checkout %s"

    """
        {NS} commands
    """
    TNS_VERSION = "tns --version"
    TNS_INSTALL = "tns install"
    TNS_BUILD = "tns build %s"
    TNS_TEST = "tns test %s"
    ANDROID = "android"
    IOS = "ios"

    """
        COMMANDS
    """
    CMD_GIT_CLONE = "CMD_0"

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
    def execute_build_rules():
        """
            Build rules executor
        """
        for br in Helpers.BUILD_RULES:
            br.execute_rule()

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
            "repository": "",
            "branch": "",
            "username": "",
            "token": "",
            "build": {
                "timer": 10,
                "android": {
                    "build": False,
                    "test": False
                },
                "ios": {
                    "build": False,
                    "test": False
                }
            }
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, ensure_ascii=False)
        f.close()

    @staticmethod
    def read_config():
        """
            Configuration file reader
        """

        with open(CONFIG_FILE, "r") as f:
            cfg = json.load(f)
        f.close()
        return cfg

    @staticmethod
    def print_with_stamp(msg):
        """
            Method adds time stamp on the print output

            :param msg: Message to print
        """
        print("%s  ---  %s" % (datetime.now().strftime("%Y-%m-%d  %H:%M:%S"), msg))

    @staticmethod
    def print_build_status(failed=True, msg=None):
        """
            Methods prints build status message

            :param failed: Build status
            :param msg: Message to print
        """

        if failed:
            if msg is not None:
                Helpers.print_with_stamp(msg)
            print("\n\n%s  BUILD FAILED\n" % Helpers.RED)
        else:
            if msg is not None:
                Helpers.print_with_stamp(msg)
            print("\n\n%s BUILD SUCCESS\n" % Helpers.GREEN)
        print(Helpers.RESET)

    @staticmethod
    def perform_command(cmd=list(), shell=False):
        """
            Shell command executor

            :param cmd: Command, option and argument list
            :param shell:  Is shell command
        """

        try:
            out = subprocess.check_output(cmd, shell=shell)
            return False, str(out, "UTF-8")
        except subprocess.CalledProcessError as ex:
            return True, str(ex)
