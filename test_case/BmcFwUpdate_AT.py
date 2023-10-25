# !/usr/bin/python3
# -*- encoding: utf-8 -*-
'''
@Author  :   Lujunchdng
@Contact :   Juncheng.Lu@luxshare-ict.com
@Software:   TestCase
@File    :   BmcFwUpdate_AT.py
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


class BmcFwUpdate_AT(TempItem):

    def __init__(self, options):
        super().__init__()
        self.name = "bmc fw update for at"
        self.expect = "This is bmc fw update for at."
        self.options = options
        self.config = [
            {"file": "Device.yaml", "name": "UUT", "key": options.g_cfg.get_server()},
            {"file": "BmcDevice.yaml", "name": "HEADER_TAIL", "key": options.g_cfg.get_server_bmc()},
            {"file": "BmcDevice.yaml", "name": "BMC_TAIL", "key": options.g_cfg.get_jbog_bmc()},
            {"file": "FwVersion.yaml", "name": "FwVsersion", "key": "FW-VERSION"},
            {"file": "UUT.yaml", "name": "InitPath", "key": "InitPath"},
        ]

    def exe(self):
        header_bmc_ip = self.config["HEADER_TAIL"]["ip_address"]
        tail_bmc_ip = self.config["BMC_TAIL"]["ip_address"]
        target_header_ver = self.config["FwVsersion"]["header_bmc_ver_for_at"]
        target_tail_ver = self.config["FwVsersion"]["tail_bmc_ver"]
        path = self.config["InitPath"]
        with self.ssh_connect(uut=self.config["UUT"]):
            
            parser = self.execute_run("ls -l /opt/Alioam/")
            if 'x' not in parser.get_origin_data():
                self.execute_run("chmod -R 777 /opt/Alioam/")

            # 检查机头bmc fw版本
            parser = self.execute_run("ipmitool mc info | grep -i 'Firmware Revision' | awk '{print $4}'")
            current_header_ver = re.search(r'\d+.\d+', parser.get_origin_data()).group().strip()
            self.logger.info(f"Current head bmc version is {current_header_ver}, target version is {target_header_ver}")
            if current_header_ver != target_header_ver:
            #if True:
                #parser = self.execute_run("chmod -R 777 /opt/Alioam/")
                parser = self.execute_run(
                    f"{path['bmc_header_script']} {header_bmc_ip} taobao 9ijn0okm {path['bmc_header_fw_for_at']} BMCAndConf 1")
                if not re.search(r'Flash\s*Complete', parser.get_origin_data(), re.I):
                    self.logger.info("Header bmc flash bure fail")
                    self.fail("Header bmc flash bure fail")
            timeout = 0
            flag1 = False
            flag2 = False
            while True:
                self.sleep(30)
                timeout += 30
                parser = self.execute_run(f"ping {header_bmc_ip} -c4", i_exit_code=True)
                if re.search(r' 0\%\s*packet\s*loss', parser.get_origin_data(), re.I):
                    flag1 = True
                parser = self.execute_run(f"ping {tail_bmc_ip} -c4", i_exit_code=True)
                if re.search(r' 0\%\s*packet\s*loss', parser.get_origin_data(), re.I):
                    flag2 = True
                if flag1 and flag2:
                    break
                if timeout > 300:
                    self.fail("Bmc restart fail")
            self.sleep(60)
            self.execute_run("ipmitool chassis policy always-on")
        return Pass(self)
    
    def tearDown(self):
        self.sleep(60)
        user = {
            "ip_address": "localhost",
            "password": "1",
            "username": "root"
        }
        host = self.config["HEADER_TAIL"]
        with self.ssh_connect(uut=user):
            ip = host["ip_address"]
            user = 'taobao'
            password = '9ijn0okm'
            self.execute_run(f"cat /root/.ssh/known_hosts | grep -i '{ip}'", save_exit_code=True)
            if self.ssh.get_exit_code() == 0:
                self.execute_run(f"sed -i '/{ip}/d' /root/.ssh/known_hosts", i_exit_code=True)
            self.invoke_run(f"ssh {user}@{ip}", end_with="yes/no")
            self.invoke_run("yes", end_with="password")
            self.invoke_run(f"{password}", end_with="$")
            self.invoke_run("exit", end_invoke=True)
            self.sleep(3)


if __name__ == '__main__':
    TempRun.set_item(BmcFwUpdate_AT)
    TempRun.suite_name = "test ancoan suite"
    TempRun.para_list = [("Param.yaml", {"exclude": ["PDU"]})]
    TempRun.main()
