# -*- coding:utf-8 -*-
"""
    1. create a ExpectValue.py file
    2. create a CheckValue.yaml file
    3.python GenerateData.py --module TestCase\OEM_CMD --random --exclude_module stability
"""

import os
import sys
import argparse
import types
import re
import importlib
from pathlib import PurePath
import random

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

from Utils.Login import SshConnect
from Lib.Config import YamlLoadConfig
from Lib.Logging import LoggerGet
from Utils.DataBuffer import StrParser
from Utils.BmcUtility import multi_column
from Lib.Config import CsvLoader


def colloect_psu_info(key, data):
    psu_list = data.split("\n")
    indexs = []
    psu_dict = {}
    for i in range(1, 3):
        index = psu_list.index(f"========PSU {i}========")
        indexs.append(index)

    if key == "psu1":
        for psu1_info in psu_list[indexs[0] + 1:indexs[1]]:
            ps = psu1_info.split(":")
            key = ps[0].strip()
            val = ps[1].strip()
            psu_dict[key] = val
    else:
        for psu2_info in psu_list[indexs[1] + 1:]:
            ps = psu2_info.split(":")
            key = ps[0].strip()
            val = ps[1].strip()
            psu_dict[key] = val
    return psu_dict


# [ # {"cmd":"","expect_key":"", "expect_val":"", "UUT":"UUT_01"}]
# 不指定cmd , 直接从key, val获取 期望键和期望值

execute_cmd = {
    "UUT_02": [
        {"cmd": "ipmitool bmc info", "key": ["ipmi_version", "product_name"],
         "val": [r"ipmi version[ :]+(\d+\.\d+)", r"Product Name[ :]+([\w\.-]+)"]},
        {"cmd": "dmidecode -t 4 | grep -iE 'Processor Information' | wc -l", "key": "cpu_count",
         "val": lambda key, x: int(x)},
        {"cmd": "dmidecode -t 17 | grep -iE 'serial number' | grep -ivc 'no dimm'", "key": "memory_count",
         "val": lambda key, x: int(x)},
        {"key": ["system_health_ok", "system_health_minor", "system_health_major", "system_health_critical",
                 "_12_v_deviation", "_rtc_v_deviation"],
         "val": ["ok", "minor", "major", "critical", 0.05, 0.01]}
    ],
    "UUT_01": [
        {"cmd": "ipmitool alioem getdeviceinformation", "key": ["psu1", "psu2"],
         "val": [colloect_psu_info, colloect_psu_info]}
    ]
}


class GenerateExpectVal:

    def __init__(self, cmd) -> None:
        self.execute_cmd = cmd
        self.data = None
        self.file = "./ExpectValue.py"

    def build_data(self, data_dict):
        data = ""
        for key, val in data_dict.items():
            if isinstance(val, str):
                template_str = '{} = "{}"\n'.format(key, val)
            elif isinstance(val, int):
                template_str = '{} = {}\n'.format(key, val)
            else:
                template_str = '{} = {}\n'.format(key, val)
            data += template_str
        return data

    def write_data(self, file, data):
        with open(file, "w") as f:
            f.write(self.build_data(data))

    def gen_expect_val_data(self):
        execute_cmd = self.execute_cmd
        data_dict = {}
        config = YamlLoadConfig()
        logger_get = LoggerGet(GenerateExpectVal.__name__, "debug")
        logger = logger_get.logger
        for uut_name, cmds in execute_cmd.items():
            uut_cnf = config.data(uut_name)
            host = uut_cnf.get("ip_address")
            user = uut_cnf.get("username")
            pwd = uut_cnf.get("password")

            with SshConnect(ip=host, user=user, password=pwd, logger=logger) as ssh:
                for cmd_info in cmds:
                    cmd = cmd_info.get("cmd", None)
                    if cmd:
                        out_data = ssh.run(cmd)
                        parser = out_data.str_parser()
                        keys = cmd_info["key"]
                        if isinstance(keys, list):
                            vals = cmd_info["val"]
                            for i in range(len(keys)):
                                key = keys[i]
                                val = vals[i]
                                if isinstance(val, types.FunctionType):
                                    data = parser.get_origin_data().strip()
                                    data_dict[key] = val(key, data)
                                elif val:
                                    data = parser.get_value(val)
                                    data_dict[key] = data
                                else:
                                    data = parser.get_origin_data().strip()
                                    data_dict[key] = data
                        else:
                            val = cmd_info["val"]
                            if isinstance(val, types.FunctionType):
                                data = parser.get_origin_data().strip()
                                data_dict[keys] = val(key, data)
                            elif val:
                                data = parser.get_value(val)
                                data_dict[keys] = data
                            else:
                                data = parser.get_origin_data().strip()
                                data_dict[keys] = data
                    else:
                        keys = cmd_info["key"]
                        vals = cmd_info["val"]
                        for i in range(len(keys)):
                            data_dict[keys[i]] = vals[i]

        self.data = data_dict

    def run(self):
        self.gen_expect_val_data()
        self.write_data(self.file, self.data)


class GenerateSensorCheckValue:

    def __init__(self, uut_file, uut_name) -> None:
        self.data = {}
        self.uut_file = uut_file
        self.uut_name = uut_name
        self.write_file = "Config.yaml"
        self.update_data = {}

    def init_value(self):
        self.update_data["volts"] = {}
        self.update_data["watts"] = {}

    def gen_sdr_elist_value(self):
        config = YamlLoadConfig(cfg_name=self.uut_file)
        logger_get = LoggerGet(GenerateExpectVal.__name__, "debug")
        logger = logger_get.logger

        uut_cnf = config.data(self.uut_name)
        host = uut_cnf.get("ip_address")
        user = uut_cnf.get("username")
        pwd = uut_cnf.get("password")

        with SshConnect(ip=host, user=user, password=pwd, logger=logger) as ssh:
            out_data = ssh.run("ipmitool sensor list | grep -iE 'rpm|Watts|degrees C|Volts'")
            parser = out_data.str_parser()
            sensors = multi_column(parser.get_origin_data(), [0, 1, 2])

            for name, val, unit in sensors:
                if "volts" == unit.lower():
                    #  收集 电压基准值
                    self.collect_vlots(name, val)
                elif "watts" == unit.lower():
                    self.collect_watts(name, val)

        logger.info(self.update_data)

    def collect_vlots(self, name, val):
        # 获取基准值
        s_val = re.search(r"(\d+V\d*)", name, re.I)
        if s_val is None:
            s_val = 0.0
        else:
            v = s_val.group(1).strip()
            vs = v.lower().split("v")
            s_val = float("{0}.{1}".format(vs[0], vs[1]))
        self.update_data["volts"][name] = s_val

    def collect_watts(self, name, val):
        self.update_data["watts"][name] = float(val)

    def write_data(self):
        load_parser = YamlLoadConfig(cfg_name=self.write_file)
        config = load_parser.get_config()
        config["sensor"] = self.update_data
        load_parser.yaml_dump(config)

    def run(self):
        self.init_value()
        self.gen_sdr_elist_value()
        self.write_data()


class GenerateSuiteCSV:
    parameters = {
        "module": {
            "dest": "module",
            "action": 'append',
            "default": [],
            "help": "batch run case module",
        },
        "exclude_module": {
            "dest": "exclude_module",
            "action": 'append',
            "default": [],
            "help": "batch run case exclude module",
        },
        "random": {
            "dest": "random",
            'action': 'store_true',
            "help": "random test bmc case",
        },
    }

    def __init__(self):
        self.module = None
        self.exclude_module = None
        self.random = False
        self.data = []
        self.run()

    def run(self):
        self.cmd_paras()
        self.suite_csv()
        self.write_csv()

    def cmd_paras(self):
        optparser = argparse.ArgumentParser()
        for key, opt in self.parameters.items():
            optparser.add_argument("--" + key, **opt)
        args = optparser.parse_args()
        self.module = args.module
        self.exclude_module = args.exclude_module
        self.random = args.random

    def write_csv(self):
        file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Config", "Suite.csv")
        if os.path.isfile(file):
            os.remove(file)
        # csv = CsvLoader(file, ["CaseName", "CaseClassName", "Params", "Path"])
        csv = CsvLoader(file, ["CaseName", "Params", "Path"])

        def _sort(d):
            name = d["CaseName"]
            # n = name.split("_", 1)[0]
            # print(n)
            # return int(n[1:])
            return name

        if self.random:
            random.shuffle(self.data)
        else:
            self.data.sort(key=_sort)
        csv.writerow_dict(self.data)

    def suite_csv(self):

        def recursion(abcpath):
            for name in os.listdir(abcpath):
                if name == "__pycache__":
                    continue
                new_abcpath = os.path.join(abcpath, name)
                if os.path.isdir(new_abcpath) and name not in self.exclude_module:
                    recursion(new_abcpath)
                else:
                    p = PurePath(abcpath)
                    index = p.parts.index("test_case")
                    path = ".".join(p.parts[index:])
                    name = name.split('.')[0]
                    file = importlib.import_module(f"{path}.{name}")
                    for d in dir(file):
                        d = getattr(file, d)
                        if type(d) is type:
                            from Lib.Template import TempItem
                            if issubclass(d, TempItem) and d.__name__ not in ["TempItem", "BiosTempItem"]:
                                data = {
                                    "CaseName": name,
                                    # "CaseClassName": d.__name__,
                                    "Params": "",
                                    "Path": path,
                                }
                                self.data.append(data)

        for m in self.module:
            m = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), m)
            print(m)
            recursion(m)


def main():
    # GenerateExpectVal(execute_cmd).run()
    # GenerateSensorCheckValue("BmcDevice.yaml", "BMC_01").run()
    GenerateSuiteCSV()


if __name__ == "__main__":
    main()
