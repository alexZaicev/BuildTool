"""
    Product Name: BuildTool
    Author: Aleksej Zaicev

    Copyright 2019
"""

import os

from helpers import Helpers
from helpers import LOGS
from datetime import datetime


class Logger(object):

    def __init__(self, name=None):
        object.__init__(self)
        path = os.path.join(LOGS, "{}_{}.log".format(name, datetime.now().strftime("%Y%m%d%H%M%S")))
        if os.path.exists(path):
            Helpers.print_with_stamp(msg=("Log with name %s already exists. Overriding existing file" % name),
                                     status=Helpers.MSG_ERR)
            Helpers.remove_file(path)
        self.clean_logs()
        self.file_out = open(file=path, mode="w+", )

    def printer(self, msg, msg_type):
        self.file_out.write(
            "%s   ---   %s   ---   %s\r" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg_type, msg))
        Helpers.print_with_stamp(msg, msg_type)

    def kill(self):
        self.file_out.close()

    def clean_logs(self):
        logs = os.listdir(LOGS)
        wl_1, wl_2, wl_3 = 0, 0, 0
        for log in logs:
            sa = log.split("_")
            if type(sa[-2]) is not None:
                wid = int(sa[-2])
                if wid == 1:
                    wl_1 += 1
                elif wid == 2:
                    wl_2 += 1
                elif wid == 3:
                    wl_3 += 1
        if wl_1 >= 10:
            self.__remove_worker_logs(logs, 1)
        if wl_2 >= 10:
            self.__remove_worker_logs(logs, 2)
        if wl_3 >= 10:
            self.__remove_worker_logs(logs, 3)

    def __remove_worker_logs(self, logs, wid):
        log_dict = dict()
        for log in logs:
            sa = log.split("_")
            if type(sa[-2]) is not None and int(sa[-2]) == wid:
                try:
                    sdt = sa[-1].split(".")[0]
                    datetime.strptime(sdt, "%Y%m%d%H%M%S")
                    log_dict[log] = int(sdt)
                except ValueError:
                    Helpers.remove_file(os.path.join(LOGS, log))
        if len(log_dict) > 0:
            log_dict = sorted(log_dict.items(), key=lambda kv: kv[1])
            dic_len = len(log_dict)
            for k, v in log_dict:
                if dic_len >= 10:
                    Helpers.remove_file(os.path.join(LOGS, k))
                    dic_len -= 1
                else:
                    break
