# !/usr/bin/python3
# -*- encoding: utf-8 -*-
'''
@Author  :   Lujuncheng
@Contact :   Juncheng.Lu@luxshare-ict.com
@Software:   TestCase
@File    :   testcase.py
@Time    :   2022/5/6
@Version :   1.0
@License :   Copyright ©LuxShare  2023 . All Rights Reserved.
@Desc    :   None
'''
import os
import sys

load_list = ["AnconaFactory"]


def load_package(path):
    parent_folder = os.path.dirname(path)
    for dirname in os.listdir(parent_folder):
        if dirname in load_list:
            sys.path.append(os.path.join(parent_folder, dirname))
            load_list.pop(load_list.index(dirname))
        if not load_list:
            return None
    else:
        return load_package(parent_folder)


load_package(os.path.abspath(__file__))

from Lib.Result import Pass
from Lib.Template import TempRun, TempItem


class testcase(TempItem):

    def __init__(self, options):
        super().__init__()
        self.name = "pcie oam switch"
        self.expect = "This is pcie oam switch function check test on the server"
        self.options = options
        self.config = [
            # {"file": "Device.yaml", "name": "UUT", "key": options.g_cfg.get_server()},
            # {"file": "UUT.yaml", "name": "cfg", "key": options.g_cfg.get_rk()},
            {"file": "UUT.yaml", "name": "path", "key": "InitPath"},
        ]

    def exe(self):
        print("======heiheihei=========")
        return Pass(self)


if __name__ == '__main__':
    TempRun.set_item(testcase)
    TempRun.suite_name = "test ancoan suite"
    TempRun.para_list = [("Param.yaml", {"exclude": ["PDU"]})]
    TempRun.main()
