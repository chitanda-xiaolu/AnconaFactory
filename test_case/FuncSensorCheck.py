# !/usr/bin/python3
# -*- encoding: utf-8 -*-
'''
@Author  :   陈进文
@Contact :   jinwen.chen@luxshare-ict.com
@Software:   TestCase
@File    :   FuncSensorCheck.py
@Time    :   2023/5/6
@Version :   1.0
@License :   Copyright ©LuxShare  2022 . All Rights Reserved.
@Desc    :   功能检查/Sensor测试/sensor检查
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


class FuncSensorCheck(TempItem):

    def __init__(self, options):
        super().__init__()
        self.name = "uart"
        self.expect = "This is uart function check test"
        self.options = options
        self.config = [
            {"file": "Device.yaml", "name": "UUT", "key": options.g_cfg.get_server()},
            {"file": "BmcDevice.yaml", "name": "JBOG_BMC", "key": options.g_cfg.get_jbog_bmc()},
        ]

    def exe(self):
        # 获取机头的sdr
        with self.ssh_connect(uut=self.config["UUT"]):
            self.execute_run("ipmitool sdr")

        # 获取机尾的sdr
        with self.ssh_connect(uut=self.config["JBOG_BMC"]):
            self.execute_run("ipmitool sdr")

        return Pass(self)


if __name__ == '__main__':
    TempRun.set_item(FuncSensorCheck)
    TempRun.suite_name = "test AncoanFactory suite"
    TempRun.para_list = [("Param.yaml", {"exclude": ["PDU"]})]
    TempRun.main()
