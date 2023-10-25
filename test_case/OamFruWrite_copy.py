# !/usr/bin/python3
# -*- encoding: utf-8 -*-
'''
@Author  :   Lujuncheng
@Contact :   Juncheng.Lu@luxshare-ict.com
@Software:   TestCase
@File    :   OamFruWrite_copy.py
@Time    :   2022/5/6
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
from Lib.Request import MesSocket


class OamFruWrite_copy(TempItem):

    def __init__(self, options):
        super().__init__()
        self.name = "oam fru write"
        self.expect = "This is oam oam fru write."
        self.options = options
        self.config = [
            {"file": "Device.yaml", "name": "UUT", "key": options.g_cfg.get_server()},
            {"file": "UUT.yaml", "name": "InitPath", "key": "InitPath"},
            {"file": "BmcDevice.yaml", "name": "BMC_TAIL", "key": options.g_cfg.get_jbog_bmc()},
            {"file": "UUT.yaml", "name": "relation", "key": "relation_info"},
        ]

    def exe(self):
        tail_bmc_ip = self.config["BMC_TAIL"]["ip_address"]
        path = self.config["InitPath"]
        relation = self.config["relation"]
        with self.ssh_connect(uut=self.config["UUT"]):
            # btv端烧录
            '''
                1. 根据sn生成oam 对应的.ini文件
                eg: sn= KS140800012BQ0102 cat fru_oam.ini >  KS140800012BQ0102.ini
                2. 将sn 写入.ini文件
                eg: cat KS140800012BQ0102.ini  grep -wn oam_sn | cut -d: -f1 | xargs -I line sed -i "lines/oam_sn/KS140800012BQ0102/g KS140800012BQ0102.ini
                3. 将part_num写入.ini文件
                4. 生成bin文件
                5. 烧录bin文件
            '''
            # 从mes获取sn信息
            _mes = MesSocket()
            fru_info = _mes.get_mes_info(self.options.g_cfg.get_sn())["Results"]["oam_sn"]
            bmcfru_infos = []
            print(fru_info)
            for fru in fru_info:
                # # 根据sn生成oam 对应的ini文件
                parser = self.execute_run(
                    f'cat {path.get("fru_path")}fru_oam.ini > {path.get("fru_path")}{fru["oam_sn"]}.ini')
                # 将sn 写入.ini文件
                parser = self.execute_run(
                    f'cat {path.get("fru_path")}{fru["oam_sn"]}.ini | grep -wn oam_sn | cut -d: -f1 | xargs -I line sed -i "lines/oam_sn/{fru["oam_sn"]}/g" {path.get("fru_path")}{fru["oam_sn"]}.ini')
                parser = self.execute_run(
                    f'cat {path.get("fru_path")}{fru["oam_sn"]}.ini | grep -wn part_num | cut -d: -f1 | xargs -I line sed -i "lines/part_num/{fru["oam_part_no"]}/g" {path.get("fru_path")}{fru["oam_sn"]}.ini')
                parser = self.execute_run(
                    f'python3 {path.get("fru_path")}fru.py {path.get("fru_path")}{fru["oam_sn"]}.ini {path.get("fru_path")}{fru["oam_sn"]}.bin --cmd')
                parser = self.execute_run(
                    f'python3 {path.get("fru_path")}ppudbg_load_fru.py --function=write --device={relation[fru["slot"]]["dev_id"]} --binfile={path.get("fru_path")}{fru["oam_sn"]}.bin')
                
                # 生成bmc端写入数据列表
                bmcfru_info = {}
                parser = self.execute_run(
                    f'python3 {path.get("fru_path")}transition.py {path.get("fru_path")}{fru["oam_sn"]}.bin')
                hex_string = ['0x' + parser.get_origin_data().strip()[i:i + 2] for i in
                              range(0, len(parser.get_origin_data().strip()), 2)]
                items_ = [' '.join(hex_string[j:j + 32]) for j in range(0, len(hex_string), 32)]
                offset = ['0x00', '0x20', '0x40', '0x60', '0x80', '0xa0', '0xc0', '0xe0']
                write_list = [offset[k] + ' ' + items_[k] for k in range(0, 8)]
                target_hex = ' '.join(items_)
                bmcfru_info['device'] = relation[fru["slot"]]["dev_id"]
                bmcfru_info['chanel'] = relation[fru['slot']]['chanel']
                bmcfru_info['write_list'] = write_list
                bmcfru_info['target_hex'] = target_hex
                bmcfru_infos.append(bmcfru_info)

                # 读取sn信息
                self.sleep(3)
                parser = self.execute_run(
                    f'python3 {path.get("fru_path")}ppudbg_load_fru.py --function=read --device={relation[fru["slot"]]["dev_id"]} | grep -E "serial|part" | head -n2 | cut -d= -f2 | xargs')
                current_fruinfo = parser.get_origin_data().split(" ")
                if current_fruinfo[0] != fru["oam_sn"]:
                    self.logger.info(f"Device {relation[fru['slot']]['dev_id']} Sn number is not match")
                    self.fail("Device {relation[fru['slot']]['dev_id']} Sn number is not match")
                if current_fruinfo[1] != fru["oam_part_no"]:
                    self.logger.info("Device {relation[fru['slot']]['dev_id']} Sn Part number is not match")
                    self.fail("Device {relation[fru['slot']]['dev_id']} Sn Part number is not match")

        # # bmc端烧录
        with self.ssh_connect(uut=self.config["BMC_TAIL"]):    
            parser = self.execute_run("/etc/init.d/ipmistack stop")
            self.sleep(90)
            parser = self.execute_run("i2ctransfer -y 10 w1@0x70 0x00")
            print(bmcfru_infos)
            for bmc_fru in bmcfru_infos:
                parser = self.execute_run(f"i2ctransfer -y 10 w1@0x70 {bmc_fru['chanel']}")
                self.sleep(2)
                for data in bmc_fru["write_list"]:
                    parser = self.execute_run(f"i2ctransfer -y 10 w34@0x56 0x00 {data}")
                    self.sleep(2)
                # 对比bmc fru 信息
                parser = self.execute_run(f"i2ctransfer -y 10 w2@0x56 0x00 0x00 r256")
                print(bmc_fru["target_hex"])
                print("======================================")
                print(parser.get_origin_data().strip())
                if bmc_fru["target_hex"] not in parser.get_origin_data().strip():
                    self.logger.info("Hex code not match bmc fru write fail")
                    self.fail("Hex code not match bmc fru write fail")
                parser = self.execute_run("i2ctransfer -y 10 w1@0x70 0x00")
            # parser = self.execute_run("reboot")
            self.execute_run("/etc/init.d/ipmistack start")
            self.sleep(90)
        return Pass(self)

    def tearDown(self):
        with self.ssh_connect(uut=self.config["BMC_TAIL"]):
            for i in range(5):
                self.execute_run("/etc/init.d/ipmistack start")
                self.sleep(10)

    def tearError(self):
        with self.ssh_connect(uut=self.config["BMC_TAIL"]):
            self.execute_run("/etc/init.d/ipmistack start")
            self.sleep(90)


if __name__ == '__main__':
    TempRun.set_item(OamFruWrite_copy)
    TempRun.suite_name = "test ancoan suite"
    TempRun.para_list = [("Param.yaml", {"exclude": ["PDU"]})]
    TempRun.main()
