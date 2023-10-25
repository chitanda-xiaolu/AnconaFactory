# !/usr/bin/python3
# -*- encoding: utf-8 -*-
'''
@Author  :   陈进文
@Contact :   jinwen.chen@luxshare-ict.com
@Software:   TestCase
@File    :   FuncGpuLinkTest.py
@Time    :   2023/5/6
@Version :   1.0
@License :   Copyright ©LuxShare  2022 . All Rights Reserved.
@Desc    :   功能检查/GPULinkTest
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
from Lib.Error import ErrItemFail


class FuncGpuLinkTest(TempItem):

    def __init__(self, options):
        super().__init__()
        self.name = "GPU Link"
        self.expect = "This is GPU Link function check test"
        self.options = options
        self.config = [
            {"file": "Device.yaml", "name": "UUT", "key": options.g_cfg.get_server()},
            {"file": "UUT.yaml", "name": "oam_conf", "key": "OAM"},
            {"file": "UUT.yaml", "name": "cfg", "key": options.g_cfg.get_rk()},
        ]

    def exe(self):
        jbog = self.config["cfg"]["JBOG"]
        oam_config = self.config["oam_conf"]
        links = oam_config['Link']
        with self.ssh_connect(uut=self.config["UUT"]):

            if jbog["config"] == "W/O scaleout":
                for n in oam_config["Num"]:
                    with self.action(f"device: {n}"):
                        for p in links["not-scale-out"]:
                            parser = self.execute_run(f"ppudbg --device {n} --micnop stat {p}")
                            status = parser.get_value("Link Status[: ]+(up)")
                            self.assertEqual(f"oam device {n} ICN link state:", status.lower(), "up")

            else:
                # logger 日志器删除 StreamHandler
                # hander = self.logger.parent.handlers[0]
                # self.logger.parent.removeHandler(self.logger.parent.handlers[0])

                # 人工插入200G光纤线将光口两两相连
                # self.sleep(2)
                # print(self.tips_msg("插入200G光纤线将光口两两相连"))
                # ret = input(self.tips_msg("请输入Y/N(Y已接入) :"))

                # logger日志器添加StreamHandler
                # self.logger.parent.addHandler(hander)

                # if ret.lower() == "y":
                for n in oam_config["Num"]:
                    with self.action("device: {n}"):
                        for p in links["scale-out"]:
                            parser = self.execute_run(f"ppudbg --device {n} --micnop stat {p}")
                            status = parser.get_value("Link Status[: ]+(up)")
                            self.assertEqual(f"oam device {n} ICN link state:", status.lower(), "up")
                # else:
                #     return Fail(self, ErrItemFail("插入200G光纤失败"))

        return Pass(self)


if __name__ == '__main__':
    TempRun.set_item(FuncGpuLinkTest)
    TempRun.suite_name = "test AncoanFactory suite"
    TempRun.para_list = [("Param.yaml", {"exclude": ["PDU"]})]
    TempRun.main()
