"""
    Product Name: BuildTool
    Author: Aleksej Zaicev

    Copyright 2019
"""

from easypro_rules import EasyProRulePreBuild, EasyProRulePostBuild


def init():
    """
        Method contains custom rule constructors (PRE and POST build rules).
        Import the rule file and instantiate your custom rule. It will automatically
        load before or after the build
    """

    EasyProRulePreBuild()
    EasyProRulePostBuild()
