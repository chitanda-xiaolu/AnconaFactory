# !/usr/bin/python3
# -*- encoding: utf-8 -*-
'''
@Author  :   陈进文
@Contact :   jinwen.chen@luxshare-ict.com
@Software:   TestCase
@File    :   InitParams.py
@Time    :   2023/5/8
@Version :   1.0
@License :   Copyright ©LuxShare  2022 . All Rights Reserved.
@Desc    :   初始RK,必须要的参数
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

from Lib.Result import Pass, Fail
from Lib.Template import TempRun, TempItem
from Lib.Request import MesSocket
from Utils.GlobalConfig import InitLoadConfig
from Lib.Error import ErrItemFail
from Utils.GlobalConfig import GlobalConfig


class InitParams(TempItem):

    def __init__(self, options):
        super().__init__()
        self.name = "cpu"
        self.expect = "This is cpu function check test on the service"
        self.options = options
        # self.mes = MesSocket()
        # self.sn, self.put = InitLoadConfig.load_config(options.PUT)
        self.config = [
            {"file": "Device.yaml", "name": "UUT", "key": options.UUT},
            {"file": "BmcDevice.yaml", "name": "JBOG_BMC", "key": options.JBOG_BMC},
            {"file": "BmcDevice.yaml", "name": "SERVER_BMC", "key": options.SERVER_BMC},
            {"file": "PduDevice.yaml", "name": "PDU", "key": options.PDU},
            {"file": "BmcDevice.yaml", "name": "JBOG_ADMIN_USER", "key": "BMC_03"},
            {"file": "UUT.yaml", "name": "InitPath", "key": "InitPath"},
        ]
        self.global_config = GlobalConfig(self.config)

    def exe(self):
        print("****************hahaha*********************")
        # #  测试 RK
        # self.init_settings()
        # success = Pass(self)
        # rk, status = self.mes.save_mes_info(self.sn)
        # if status != 200:
        #     setattr(self.parent.options, "FailStop", "yes")
        #     return Fail(self, ErrItemFail(f"init params fail, RK[{rk}] error!"))
        # # rk = "RK0037030018"
        # self.global_config.rk = rk
        # self.global_config.put = self.put.strip()
        # self.global_config.sn = self.sn.strip()
        # success.g_cfg = self.global_config
        # return success
        return Pass(self)

    # def init_settings(self):
    #     user = {
    #         "ip_address": "localhost",
    #         "password": "1",
    #         "username": "root"
    #     }

    #     with self.ssh_connect(uut=user):
    #         # for host in [self.global_config.get_server(), self.global_config.get_server_bmc(),
    #         for host in [self.global_config.get_server(), self.global_config.get_jbog_bmc()]:
    #             ip = host["ip_address"]
    #             user = host["username"]
    #             password = host["password"]
    #             self.execute_run(f"cat /root/.ssh/known_hosts | grep -i '{ip}'", save_exit_code=True)
    #             if self.ssh.get_exit_code() == 0:
    #                 self.execute_run(f"sed -i '/{ip}/d' /root/.ssh/known_hosts", i_exit_code=True)

    #             self.sleep(3)
    #             # parser = self.invoke_run(f"ssh {user}@{ip}", end_with="yes/no|password", end_invoke=True)
    #             # ret = parser.check_field(r"yes/no")
    #             # if ret:
    #             #     self.invoke_run(f"ssh {user}@{ip}", end_with="yes/no")
    #             #     self.invoke_run("yes", end_with="password")
    #             self.invoke_run(f"ssh {user}@{ip}", end_with="yes/no")
    #             self.invoke_run("yes", end_with="password")
    #             self.invoke_run(f"{password}")
    #             self.invoke_run("exit", end_invoke=True)
    #             self.sleep(3)

    # def init_path(self):
    #     path = self.config["InitPath"]
    #     user = {
    #         "ip_address": "localhost",
    #         "password": "1",
    #         "username": "root"
    #     }
    #     with self.ssh_connect(uut=user):
    #         self.execute_run(
    #             f"[[ `df | grep -i {path.get('source_path')}` != '' ]] || mount -t cifs -o vers=2.0,username=Administrator,password=\`1q,sec=ntlmssp,cache=none,nobrl {path.get('source_path')} /mnt && echo 'mount success'")
    #         self.execute_run(
    #             f"[ ! -d {path.get('fw_path')} ] && mkdir -p {path.get('fw_path')} && echo 'create test dir success'")
    #         self.execute_run(f"cp -rf /mnt/FW/* {path.get('fw_path')} && echo 'copy FW file success'")

    #     with self.ssh_connect(uut=self.config["UUT"]):
    #         self.execute_run(
    #             f"[[ `df | grep -i {path.get('source_path')}` != '' ]] || mount -t cifs -o vers=2.0,username=Administrator,password=\`1q,sec=ntlmssp,cache=none,nobrl {path.get('source_path')} /mnt && echo 'mount success'")
    #         self.execute_run(
    #             f"[ ! -d {path.get('fru_path')} ] && mkdir -p {path.get('fru_path')} && echo 'create test dir success'",
    #             i_exit_code=True)
    #         self.execute_run(f"rm -rf {path.get('fru_path')}/* && echo 'clear fru dir success'")
    #         self.execute_run(f"cp -rf /mnt/fru/* {path.get('fru_path')} && echo 'copy fru file success'")
    #         self.execute_run(
    #             f"[ ! -d {path.get('fw_path')} ] && mkdir -p {path.get('fw_path')} && echo 'create test dir success'",
    #             i_exit_code=True)
    #         self.execute_run(f"rm -rf {path.get('fw_path')}/* && echo 'clear fru dir success'")
    #         self.execute_run(f"cp -rf /mnt/* {path.get('fw_path')} && echo 'copy FW file success'")
    #         self.execute_run("chmod -R 777 /opt/Alioam/")


if __name__ == '__main__':
    TempRun.set_item(InitParams)
    TempRun.suite_name = "test AncoanFactory suite"
    TempRun.para_list = [("Param.yaml", {"exclude": ["PDU"]})]
    TempRun.main()
