# !/usr/bin/python3
# -*- encoding: utf-8 -*-
'''
@Author  :   陈进文
@Contact :   jinwen.chen@luxshare-ict.com
@Software:   TestCase
@File    :   BiosFwCheck_AT.py
@Time    :   2022/2/1
@Version :   1.0
@License :   Copyright ©LuxShare  2022 . All Rights Reserved.
@Desc    :   None
'''
import os
import sys
import re

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


class BiosFwCheck_AT(TempItem):

    def __init__(self, options):
        super().__init__()
        self.name = "bios fw check for at"
        self.expect = "This is bios fw check for at."
        self.options = options
        self.config = [
            {"file": "Device.yaml", "name": "UUT", "key": options.g_cfg.get_server()},
            {"file": "BmcDevice.yaml", "name": "BMC_HEADER", "key": options.g_cfg.get_server_bmc()},
            {"file": "FwVersion.yaml", "name": "FwVsersion", "key": "FW-VERSION"},
        ]

    def exe(self):
        target_bios_ver = self.config["FwVsersion"]["bios_ver_for_at"]
        os_ip = self.config["UUT"]["ip_address"]
        server_bmc = {
            'ip_address': self.config["BMC_HEADER"]["ip_address"],
            'username': 'taobao',
            'password': '9ijn0okm',
        }
        with self.ssh_connect(uut=self.config["UUT"]):
            parser = self.execute_run("ipmitool power cycle")
        self.sleep(420)
        with self.ssh_connect(uut=server_bmc, login_retry=10):
            parser = self.execute_run("ipmitool alioem version | grep -i bios1 | awk '{print $NF}'")
            current_ver = re.search(r'\d+.\S*\d', parser.get_origin_data(), re.I)
            self.assertEqual("check bios fw version", current_ver.group(), target_bios_ver)
        return Pass(self)


if __name__ == '__main__':
    TempRun.set_item(BiosFwCheck_AT)
    TempRun.suite_name = "test ancoan suite"
    TempRun.para_list = [("Param.yaml", {"exclude": ["PDU"]})]
    TempRun.main()
