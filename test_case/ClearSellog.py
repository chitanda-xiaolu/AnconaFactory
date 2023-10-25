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
import time

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


class ClearSellog(TempItem):

    def __init__(self, options):
        super().__init__()
        self.name = "cpu config check"
        self.expect = "This is cpu config check for normal case."
        self.options = options
        self.config = [
            {"file": "Device.yaml", "name": "UUT", "key":self.options.g_cfg.get_server()},
            {"file": "BmcDevice.yaml", "name": "JBOG_BMC", "key": options.g_cfg.get_jbog_bmc()},
            {"file": "BmcDevice.yaml", "name": "SERVER_BMC", "key": options.g_cfg.get_server_bmc()},
            {"file": "BmcDevice.yaml", "name": "JBMC", "key":self.options.g_cfg.get_jbog_admin()},
        ]

    def exe(self):
        #清除机尾alioem sel
        with self.ssh_connect(uut=self.config["JBOG_BMC"]):
            parser = self.execute_run("touch /logs/restorefactory")
            parser = self.execute_run("ipmitool raw 6 2")

        self.sleep(30)

        #清除机头alioem sel
        with self.ssh_connect(uut=self.config["SERVER_BMC"]):
            parser = self.execute_run("touch /logs/restorefactory")
            parser = self.execute_run("ipmitool raw 6 2")

        self.sleep(30)

        with self.ssh_connect(uut=self.config["UUT"]):
            jbmc_ip = self.config["JBMC"]["ip_address"]
            jbmc_user = self.config["JBMC"]["username"]
            jbmc_passwd = self.config["JBMC"]["password"]
            time.sleep(10)
            parser = self.execute_run(f"ipmitool -I lanplus -H {jbmc_ip} -U {jbmc_user} -P {jbmc_passwd} sel clear ")
            count = self.execute_run(f"ipmitool -I lanplus -H {jbmc_ip} -U {jbmc_user} -P {jbmc_passwd} sel list").data.strip().split('\n')
            self.assertEqual(f"clear Jbog bmc sel log", int(1), len(count))
            parser = self.execute_run("ipmitool sel clear ")
            count = self.execute_run("ipmitool sel list ").data.strip().split('\n')
            self.assertEqual(f"clear Server bmc sel log", int(1), len(count))
        return Pass(self)


if __name__ == '__main__':
    TempRun.set_item(ClearSellog)
    TempRun.suite_name = "test ancoan suite"
    TempRun.para_list = [("Param.yaml", {"exclude": ["PDU"]})]
    TempRun.main()
