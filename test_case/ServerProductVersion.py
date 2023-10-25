# !/usr/bin/python3
# -*- encoding: utf-8 -*-
'''
@Author  :   Harvey
@Software:   TestCase
@Time    :   2023/5/5
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
from Lib.Request import MesSocket



class ServerProductVersion(TempItem):

    def __init__(self, options):
        super().__init__()
        self.name = "Server Product Version check"
        self.expect = "This is Server Product Version check for normal case."
        self.options = options
        self.config = [
            {"file": "Device.yaml", "name": "UUT", "key":self.options.g_cfg.get_server()},
        ]

    def exe(self):
        with self.ssh_connect(uut=self.config["UUT"]):
            # 差一段三段码
            _mes = MesSocket()
            write_info = "X01"
            data = self.execute_run("ipmitool fru print 0 ").data.strip()
            parser = self.execute_run(f"ipmitool fru edit 0 field p 3 '{write_info}' ")
            data = self.execute_run("ipmitool fru print 0 ").data.strip()
            parser = _mes.json_filter(data, "Product Version" )
            self.assertEqual(f"Server Product Version ", write_info, parser)

        return Pass(self)


if __name__ == '__main__':
    TempRun.set_item(ServerProductVersion)
    TempRun.suite_name = "test ancoan suite"
    TempRun.para_list = [("Param.yaml", {"exclude": ["PDU"]})]
    TempRun.main()
