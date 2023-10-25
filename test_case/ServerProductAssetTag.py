
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


class ServerProductAssetTag(TempItem):

    def __init__(self, options):
        super().__init__()
        self.name = "cpu config check"
        self.expect = "This is cpu config check for normal case."
        self.options = options
        self.config = [
            {"file": "Device.yaml", "name": "UUT", "key":self.options.g_cfg.get_server()},
            
            {"file": "BmcDevice.yaml", "name": "JBMC", "key":self.options.g_cfg.get_jbog_admin()},
        ]

    def exe(self):
        with self.ssh_connect(uut=self.config["UUT"]):
            _mes = MesSocket()
            #查看机头的三段码
            write_info =  _mes.get_mes_info(self.options.g_cfg.get_sn())["Results"]["server_tdid"]
            data = self.execute_run("ipmitool fru print 0 ")
            parser = self.execute_run(f" ipmitool fru edit 0 field p 5 {write_info}")
            data = self.execute_run("ipmitool fru print 0 ")
            parser = _mes.json_filter(data, "Product Asset Tag" )
            self.assertEqual(f"Product Asset Tag ", write_info, parser)
            # self.assertEqual(f"clear Server bmc sel log", int(1), len(count))
        return Pass(self)


if __name__ == '__main__':
    TempRun.set_item(ServerProductAssetTag)
    TempRun.suite_name = "test ancoan suite"
    TempRun.para_list = [("Param.yaml", {"exclude": ["PDU"]})]
    TempRun.main()
