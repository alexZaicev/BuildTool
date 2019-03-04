import os

from helpers import WORKSPACE, Helpers
from interfaces import PreBuildRule


class EasyProRule(PreBuildRule):

    def execute_rule(self):
        path = os.path.join(self.base_dir, "node_modules", "nativescript-zxing", "platforms", "android")
        if os.path.exists(path):
            Helpers.remove_dir(path)

    def __init__(self):
        PreBuildRule.__init__(self, name=__name__)
        self.base_dir = WORKSPACE + Helpers.get_repo_name(Helpers.CONFIGURATION.get("repository"))
