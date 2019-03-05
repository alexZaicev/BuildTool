import os

from helpers import WORKSPACE, Helpers
from interfaces import PreBuildRule


class EasyProRule(PreBuildRule):

    def execute_rule(self, cfg, worker_id):
        base_dir = os.path.join(WORKSPACE, "{}_{}".format(cfg["name"], worker_id),
                                Helpers.get_repo_name(cfg["repository"]))
        path = os.path.join(base_dir, "node_modules", "nativescript-zxing", "platforms", "android")
        if os.path.exists(path):
            Helpers.remove_dir(path)

    def __init__(self):
        PreBuildRule.__init__(self)
