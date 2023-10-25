# !/usr/bin/python3
# -*- encoding: utf-8 -*-
'''
@Author  :   陈进文
@Contact :   jinwen.chen@luxshare-ict.com
@Software:   TestCase
@File    :   FuncNvmeCheck.py
@Time    :   2023/5/8
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


class FuncNvmeCheck(TempItem):

    def __init__(self, options):
        super().__init__()
        self.name = "nvme"
        self.expect = "This is nvme function check test on the server"
        self.options = options
        self.config = [
            {"file": "Device.yaml", "name": "UUT", "key": options.g_cfg.get_server()},
            {"file": "UUT.yaml", "name": "cfg", "key": options.g_cfg.get_rk()},
            {"file": "UUT.yaml", "name": "path", "key": "InitPath"},
        ]

    def exe(self):
        jbog_cfg = self.config["cfg"]["JBOG"]
        nvme_size = jbog_cfg["nvme_size"]
        nvme_count = jbog_cfg["nvme_count"]
        count = 0

        if nvme_size == "NA":
            return Pass(self)

        with self.ssh_connect(uut=self.config["UUT"]):
            self.step(1, "get nvme info")
            parser = self.execute_run(f"{self.config['path']['nvme_tool']} list")
            nvmes = parser.filter_list(r"(/dev/nvme.*)")
            for nvme in nvmes:
                p1 = StrParser(nvme)
                l = p1.split(r"[ ]+")
                self.assertIn(f"{l[0]} size", nvme_size, l[6] + l[7])
                count += 1

            self.assertEqual("nvme count", count, nvme_count)
        return Pass(self)


if __name__ == '__main__':
    TempRun.set_item(FuncNvmeCheck)
    TempRun.suite_name = "test AncoanFactory suite"
    TempRun.para_list = [("Param.yaml", {"exclude": ["PDU"]})]
    TempRun.main()
