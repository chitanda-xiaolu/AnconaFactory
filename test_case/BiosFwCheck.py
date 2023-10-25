# !/usr/bin/python3
# -*- encoding: utf-8 -*-
'''
@Author  :   陈进文
@Contact :   jinwen.chen@luxshare-ict.com
@Software:   TestCase
@File    :   BiosFwCheck.py
@Time    :   2022/2/1
@Version :   1.0
@License :   Copyright ©LuxShare  2022 . All Rights Reserved.
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


class BiosFwCheck(TempItem):

    def __init__(self, options):
        super().__init__()
        self.name = "bios fw check"
        self.expect = "This is bios fw check."
        self.options = options
        self.config = [
            {"file": "Device.yaml", "name": "UUT", "key": options.g_cfg.get_server()},
            {"file": "BmcDevice.yaml", "name": "BMC", "key": options.g_cfg.get_jbog_bmc()},
            {"file": "FwVersion.yaml", "name": "FwVsersion", "key": "FW-VERSION"},
        ]

    def exe(self):
        target_bios_ver = self.config["FwVsersion"]["bios_ver"]
        with self.ssh_connect(uut=self.config["UUT"]):
            parser = self.execute_run("dmidecode -t bios | grep -i version | awk '{print $2}'")
            self.assertEqual("check bios fw version", parser.get_origin_data(), target_bios_ver)
        return Pass(self)


if __name__ == '__main__':
    TempRun.set_item(BiosFwCheck)
    TempRun.suite_name = "test ancoan suite"
    TempRun.para_list = [("Param.yaml", {"exclude": ["PDU"]})]
    TempRun.main()
