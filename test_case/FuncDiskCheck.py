# !/usr/bin/python3
# -*- encoding: utf-8 -*-
'''
@Author  :   陈进文
@Contact :   jinwen.chen@luxshare-ict.com
@Software:   TestCase
@File    :   FuncDiskCheck.py
@Time    :   2023/5/5
@Version :   1.0
@License :   Copyright ©LuxShare  2022 . All Rights Reserved.
@Desc    :   功能检查/硬盘测试(机头)
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
from Utils.DataBuffer import StrParser


class FuncDiskCheck(TempItem):

    def __init__(self, options):
        super().__init__()
        self.name = "disk"
        self.expect = "This is disk function check test on the service"
        self.options = options
        self.config = [
            {"file": "Device.yaml", "name": "UUT", "key": options.g_cfg.get_server()},
            {"file": "UUT.yaml", "name": "cfg", "key": options.g_cfg.get_rk()},
        ]

    def exe(self):
        server = self.config["cfg"]["SERVER"]
        e_m2_count = server["m2_count"]
        e_m2_size = server["m2_size"]
        e_m2_type = server["m2_type"]
        c = 0
        if e_m2_size == "NA":
            return Pass(self)

        with self.ssh_connect(uut=self.config["UUT"]):
            self.step(1, "get m.2 info")
            parser = self.execute_run("lsblk | grep sd", i_exit_code=True, retry_expt=1)
            self.step(2, "check m.2 info")

            if parser.get_origin_data() != "Null":
                m2s = multi_column(parser.get_origin_data(), column_index=[0, 3, 5], separator=" ")
                for m in m2s:
                    m2_name = m[0]
                    m2_type = m[2]
                    if m2_type == 'disk':
                        m2_size = float(m[1][:-1])
                        if m2_size >= 100.0:
                            val = round(float(e_m2_size[:-1]) - m2_size, 1)
                            self.assertLess(f"m2 {m2_name} size difference value", val, 50)
                            c += 1
                        else:
                            u_disk = m2_name
            self.assertEqual("m2 count", c, e_m2_count)

            parser = self.execute_run(f"lsscsi | grep -i '/dev/sd' | grep -iv '{u_disk}'")
            lines = parser.split("\r\n")
            m2_data = []
            for line in lines:
                if line:
                    line_list = StrParser(line).split(r" +")
                    line_list = [l for l in line_list if l]
                    m2_data.append((line_list[-3], line_list[-1]))

            for m2_type, m2_name in m2_data:
                self.assertIn(f"{m2_name}", m2_type, e_m2_type)
        return Pass(self)


if __name__ == '__main__':
    TempRun.set_item(FuncDiskCheck)
    TempRun.suite_name = "test ancoan suite"
    TempRun.para_list = [("Param.yaml", {"exclude": ["PDU"]})]
    TempRun.main()
