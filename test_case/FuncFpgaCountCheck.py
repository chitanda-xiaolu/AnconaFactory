# !/usr/bin/python3
# -*- encoding: utf-8 -*-
'''
@Author  :   Lujuncheng
@Contact :   Juncheng.Lu@luxshare-ict.com
@Software:   TestCase
@File    :   FuncFpgaCountCheck.py
@Time    :   2023/5/23
@Version :   1.0
@License :   Copyright ©LuxShare  2022 . All Rights Reserved.
@Desc    :   功能检查/Memory测试  （机头）
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
from Utils.DataBuffer import StrParser


class FuncFpgaCountCheck(TempItem):

    def __init__(self, options):
        super().__init__()
        self.name = "Fpga Count"
        self.expect = "This is Fpga Count on the server"
        self.options = options
        self.config = [
            {"file": "Device.yaml", "name": "UUT", "key": options.g_cfg.get_server()},
            {"file": "UUT.yaml", "name": "cfg", "key": options.g_cfg.get_rk()},
            {"file": "UUT.yaml", "name": "path", "key": "InitPath"},
        ]

    def exe(self):
        jbog_cfg = self.config["cfg"]["JBOG"]
        fpga_count = jbog_cfg["fpga_count"]
        count = 0

        if fpga_count == "NA":
            return Pass(self)

        with self.ssh_connect(uut=self.config["UUT"]):
            parser = self.execute_run(f'lspci -Dnn | grep 0580 | grep -icE "1ded"')
            current_fpga_count = int(parser.get_origin_data())
            self.assertEqual("Fpga count", current_fpga_count, int(fpga_count*4))
        return Pass(self)


if __name__ == '__main__':
    TempRun.set_item(FuncFpgaCountCheck)
    TempRun.suite_name = "test AncoanFactory suite"
    TempRun.para_list = [("Param.yaml", {"exclude": ["PDU"]})]
    TempRun.main()
