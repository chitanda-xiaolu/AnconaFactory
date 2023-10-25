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
import re
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


class HibProductManufacturer(TempItem):

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
            jbmc_ip = self.config["JBMC"]["ip_address"]
            jbmc_user = self.config["JBMC"]["username"]
            jbmc_passwd = self.config["JBMC"]["password"]
            _mes = MesSocket()
            model_str =  _mes.get_mes_info(self.options.g_cfg.get_sn())["Results"]["rk_customer_part_number"]
            match = re.search('^T', model_str)
            if match:
                write_info = "luxshare-DC"
            else:
                write_info = "AlibabaCloud"
            # 差一段三段码
            data = self.execute_run("ipmitool  -I lanplus -H %s -U %s -P %s  fru print 0 " % (jbmc_ip, jbmc_user ,jbmc_passwd), i_exit_code=True)
            parser = self.execute_run(f"ipmitool -I lanplus -H {jbmc_ip} -U {jbmc_user} -P {jbmc_passwd} fru edit 0 field p 0 {write_info} ", i_exit_code=True)
            data = self.execute_run("ipmitool  -I lanplus -H %s -U %s -P %s  fru print 0 " % (jbmc_ip, jbmc_user ,jbmc_passwd), i_exit_code=True)
            parser = _mes.json_filter(data, "Product Manufacturer" )
            self.assertEqual(f"Hib Product Manufacturer ", write_info, parser)
            # self.assertEqual(f"clear bmc sel log", int(1), len(count))
        return Pass(self)

if __name__ == '__main__':
    TempRun.set_item(HibProductManufacturer)
    TempRun.suite_name = "test ancoan suite"
    TempRun.para_list = [("Param.yaml", {"exclude": ["PDU"]})]
    TempRun.main()
