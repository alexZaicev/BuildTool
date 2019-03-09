"""
    Product Name: BuildTool
    Author: Aleksej Zaicev

    Copyright 2019
"""

import os

from helpers import WORKSPACE, Helpers, isWin
from interfaces import PreBuildRule, PostBuildRule


class EasyProRulePreBuild(PreBuildRule):

    def execute_rule(self, cfg, worker_id, logger):
        base_dir = os.path.join(WORKSPACE, "{}_{}".format(cfg["name"], worker_id))
        path = os.path.join(base_dir, "node_modules", "nativescript-zxing", "platforms", "android")
        if os.path.exists(path):
            Helpers.remove_dir(path)
            logger.printer("Nativescript-Zxing Android platform removed", Helpers.MSG_INFO)

    def __init__(self):
        PreBuildRule.__init__(self)


class EasyProRulePostBuild(PostBuildRule):

    def execute_rule(self, cfg, worker_id, logger):

        base_dir = os.path.join(WORKSPACE, "{}_{}".format(cfg["name"], worker_id))
        for i in range(0, 2, 1):
            path = None
            if i == 0:
                if cfg["android"]["build"]:
                    path = os.path.join(base_dir, "platforms", "android", "app", "build", "outputs", "apk")
            else:
                if cfg["ios"]["build"]:
                    pass

            if path is not None:
                if not os.path.exists(path):
                    raise FileNotFoundError("Output build files not found")

                if isWin:
                    root = "C:\\Users\\{}\\AppBuildFiles".format(os.environ.get('USERNAME'))
                    if not os.path.exists(root):
                        os.mkdir(root)
                    build_root = os.path.join(root, cfg["name"])
                    if os.path.exists(build_root):
                        Helpers.remove_dir(build_root)
                    os.mkdir(build_root)

                    if i == 0:
                        destination = os.path.join(build_root, "Android")
                    else:
                        destination = os.path.join(build_root, "iOS")
                    cmd = "xcopy {} {} /E /C /I /Y".format(path, destination)
                else:
                    root = "/Users/{}/AppBuildFiles".format(os.environ.get('USERNAME'))
                    if not os.path.exists(root):
                        os.mkdir(root)
                    build_root = os.path.join(root, cfg["name"])
                    if os.path.exists(build_root):
                        Helpers.remove_dir(build_root)
                    os.mkdir(build_root)

                    if i == 0:
                        destination = os.path.join(build_root, "Android")
                    else:
                        destination = os.path.join(build_root, "iOS")
                    cmd = "cp -a {} {}".format(path, destination)

                Helpers.perform_command(Helpers.cmd_list(cmd), shell=True, logger=logger)

    def __init__(self):
        PostBuildRule.__init__(self)
