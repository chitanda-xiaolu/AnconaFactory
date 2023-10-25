# !/usr/bin/python3
# -*- encoding: utf-8 -*-
'''
@Author  :   陈进文
@Contact :   jinwen.chen@luxshare-ict.com
@Software:   TestCase
@File    :   FuncPsuCheck.py
@Time    :   2023/5/6
@Version :   1.0
@License :   Copyright ©LuxShare  2022 . All Rights Reserved.
@Desc    :   功能检查/PSU测试
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
from Utils.BmcUtility import multi_column


class FuncPsuCheck(TempItem):

    def __init__(self, options):
        super().__init__()
        self.name = "psu"
        self.expect = "This is psu function check test"
        self.options = options
        self.config = [
            {"file": "Device.yaml", "name": "UUT", "key": options.g_cfg.get_server()},
            {"file": "BmcDevice.yaml", "name": "JBOG_BMC", "key": options.g_cfg.get_jbog_bmc()},
            {"file": "UUT.yaml", "name": "cfg", "key": options.g_cfg.get_rk()},
        ]

    def exe(self):
        server = self.config["cfg"]["SERVER"]
        JBOG = self.config["cfg"]["JBOG"]

        # 获取机头的psu
        with self.ssh_connect(uut=self.config["UUT"]):
            parser = self.execute_run("ipmitool sdr elist | egrep -i 'PS1_Status|PS2_Status'")
            psus = multi_column(parser.get_origin_data(), column_index=[0, 4])

            with self.action(level="server psu info check"):
                self.assertEqual("server psu count", len(psus), server["psu_count"])
                for p_name, status in psus:
                    self.assertEqual(f"{p_name} status", status.lower(), "presence detected")

        # 获取机尾的psu
        with self.ssh_connect(uut=self.config["JBOG_BMC"]):
            parser = self.execute_run("ipmitool sdr elist | egrep -i 'PS[1-6]_Status'")
            psus = multi_column(parser.get_origin_data(), column_index=[0, 4])

            with self.action(level="JBOG psu info check"):
                self.assertEqual("JBOG psu count", len(psus), JBOG["psu_count"])
                for p_name, status in psus:
                    self.assertEqual(f"{p_name} status", status.lower(), "presence detected")

        return Pass(self)


if __name__ == '__main__':
    TempRun.set_item(FuncPsuCheck)
    TempRun.suite_name = "test AncoanFactory suite"
    TempRun.para_list = [("Param.yaml", {"exclude": ["PDU"]})]
    TempRun.main()
