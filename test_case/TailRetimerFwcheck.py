# !/usr/bin/python3
# -*- encoding: utf-8 -*-
'''
@Author  :   Lujuncheng
@Contact :   Juncheng.Lu@luxshare-ict.com
@Software:   TestCase
@File    :   TailRetimerFwcheck.py
@Time    :   2022/5/6
@Version :   1.0
@License :   Copyright ©LuxShare  2023 . All Rights Reserved.
@Desc    :   None
'''
import os
import sys
import re
import binascii

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


class TailRetimerFwcheck(TempItem):

    def __init__(self, options):
        super().__init__()
        self.name = "Tail Retimer fw check"
        self.expect = "This is Tail retimer fw check for normal case."
        self.options = options
        self.config = [
            {"file": "Device.yaml", "name": "UUT", "key": options.g_cfg.get_server()},
            {"file": "BmcDevice.yaml", "name": "BMC_TAIL", "key": options.g_cfg.get_jbog_bmc()},
            {"file": "BmcDevice.yaml", "name": "BMC_HEADER", "key": options.g_cfg.get_server_bmc()},
            {"file": "FwVersion.yaml", "name": "FwVsersion", "key": "FW-VERSION"},
        ]

    def exe(self):
        FwVsersion = self.config["FwVsersion"]

        with self.ssh_connect(uut=self.config["BMC_TAIL"]):
            parser = self.execute_run("ls /var/retimer/ | xargs")
            retimers = parser.get_origin_data().split(" ")
            for retimer in retimers:
                self.logger.info(retimer)
                from_ = 'tail_m' if 'm' in retimer else 'tail_a'
                parser = self.execute_run(f"ipmitool raw 0x3e 0x07 0x00 0x4c 0xa5 0x07 0x03 {retimer[-1]} 9")
                self.logger.info(str(binascii.a2b_hex(parser.get_origin_data().replace(' ', '')))[6:-1])
                current_ver = str(binascii.a2b_hex(parser.get_origin_data().replace(' ', '')))[6:-1]
                self.assertEqual("Tail retimer version", current_ver.strip().lower(),
                                 FwVsersion['retimer_ver'][from_].strip().lower())

        return Pass(self)


if __name__ == '__main__':
    TempRun.set_item(TailRetimerFwcheck)
    TempRun.suite_name = "test ancoan suite"
    TempRun.para_list = [("Param.yaml", {"exclude": ["PDU"]})]
    TempRun.main()
