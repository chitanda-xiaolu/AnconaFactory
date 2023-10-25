#! /usr/bin/python3
# coding=utf-8
"""
@Author  :   陈进文
@Contact :   jinwen.chen@luxshare-ict.com
@Software:   V2
@File    :   Template.py
@Time    :   2022/8/17
@Version :   1.0
@License :   Copyright ©LuxShare  2022 . All Rights Reserved.
@Desc    :   None
"""

import importlib
import os
import time
import contextlib

# from test_case import InitParams
from Utils.Utility import trans_format
from .Case import Item, Suite
from .Error import OverrideError, SSHSessionError, TimeoutError
from .Utility import set_options
from .Logging import LoggerGet
from .Config import CsvLoader
from Utils.Login import SshConnect, BmcConnect
from Cmd.Cmd import get_bios_boot_stage, Chassis, build_cmd
from Utils.DataBuffer import StrParser


class TempItem(Item):

    def __init__(self):
        super(TempItem, self).__init__()
        # Expected PN
        # The max retry number.
        self.ssh = None
        self._errors_flag = False
        self.errors = []
        self.__options = None

    @property
    def options(self):
        return self.__options

    @options.setter
    def options(self, options):
        self.__options = options

    @property
    def logger(self):
        return self.get_logger()

    def exe(self):
        """Run the case.
        This is a virtual method.

        :return: the test result
        :rtype: Result
        """
        raise OverrideError("Must be Override exe()")

    def execute_run(self, cmd, parser_type="str_parser", logger=None, **kwargs) -> StrParser:
        """
        :param cmd: os 系统命令
        :param parser_type:  解析器类型 [str_parser/raw_parser], 默认 str_parser
        :param kwargs:  Login.SshConnect.run 中的参数 retry_expt=3, ipmi_I=False, i_exit_code=False, i_record_cmd=False,
                        save_exit_code=False, 参数详解看 Login.SshConnect.run
        :return: DataBuffer.StrParser/DataBuffer.RawParser 实例对象
        """
        if self.ssh is None:
            raise SSHSessionError("init self.ssh")
        desc = kwargs.pop("desc", False)

        logger = self.get_logger() if logger is None else logger
        if desc and desc != "":
            logger.info(f"{cmd} description info: {desc}")

        out_data = self.ssh.run(cmd, **kwargs)
        parser = getattr(out_data, parser_type)()
        i_record_cmd = kwargs.get("i_record_cmd", False)
        if not i_record_cmd:
            logger.info("SSH Execute command ok, Output below: \n%s" % parser.get_origin_data())

        return parser

    def outband_run(self, cmd, parser_type="str_parser", logger=None, **kwargs) -> StrParser:
        kwargs.update({"ipmi_I": True})
        return self.execute_run(cmd, parser_type=parser_type, logger=logger, **kwargs)

    def invoke_run(self, cmd, parser_type="str_parser", **kwargs):
        """
        交互式运行
        :param cmd: os 系统命令
        :param parser_type: 解析器类型 [str_parser/raw_parser], 默认 str_parser
        :param kwargs: Login.SshConnect.invoke 中的参数 end_with="# ", manual_stop=False, end_invoke=False
        :return: DataBuffer.StrParser/DataBuffer.RawParser 实例对象
        """
        if self.ssh is None:
            raise SSHSessionError("init self.ssh")
        out_data = self.ssh.invoke(cmd, **kwargs)
        if out_data:
            parser = getattr(out_data, parser_type)()
            self.get_logger().info("SSH Execute command ok, Output below: \n%s" % parser.get_origin_data())
            return parser
        return out_data

    @contextlib.contextmanager
    def ssh_connect(self, uut=None, login_retry=3):
        """默认连接bmc 的os"""
        if uut is None:
            uut = self.config["BMC"]
        with SshConnect(ip=uut["ip_address"], user=uut["username"], password=uut["password"],
                        port=uut.get("port", 22), logger=self.logger, login_retry=login_retry) as ssh:
            self.ssh = ssh
            yield

    @contextlib.contextmanager
    def ssh_outband_connect(self, uut=None, bmc=None, login_retry=3):
        if uut is None:
            uut = self.config["LOCAL"]
        if bmc is None:
            bmc = self.config["BMC"]
        bmc_con = BmcConnect(ip=bmc["ip_address"], user=bmc["username"], password=bmc["password"], mac=bmc["mac"],
                             logger=self.get_logger())
        with SshConnect(ip=uut["ip_address"], user=uut["username"], password=uut["password"], port=uut.get("port", 22),
                        logger=self.logger, login_retry=login_retry, bmc_con=bmc_con) as ssh:
            self.ssh = ssh
            yield

    @contextlib.contextmanager
    def action(self, level):
        self.logger.info("=" * 30 + f"start {level} action" + "=" * 30)
        try:
            yield
        except Exception as err:
            raise err
        finally:
            self.logger.info("=" * 30 + f"end {level} action" + "=" * 30)

    def tips_msg(self, msg):
        return f"[编号: {self.options.g_cfg.get_put()}]--{msg}"


class BiosTmepItem(TempItem):

    def setup(self):
        with self.action("check entry os"):
            with self.ssh_outband_connect():
                parser = self.outband_run(Chassis.power_status)
                value = parser.get_value(r"Chassis Power is (on|off)")
                if value == "on":
                    self.outband_run(Chassis.power_reset)
                else:
                    self.outband_run(Chassis.power_on)

                self.check_bios_boot_stage(ipmi_I=True)

    def check_bios_boot_stage(self, count=20, ipmi_I=False):
        cur_count = 0
        while cur_count <= count:
            parser = self.execute_run(build_cmd(get_bios_boot_stage, "0x00 0x4c 0xa5"), parser_type="raw_parser",
                                      desc="get bios boot stage", ipmi_I=ipmi_I)
            val = parser.get_unit8(0)
            if val == 200:
                break
            self.sleep(20)
        else:
            raise TimeoutError("not check bios boot stage")


class TempRun:
    item = None
    suite_name = None
    para_list = []

    @staticmethod
    def set_item(item):
        TempRun.item = item

    @staticmethod
    def main():
        options, optparser = set_options(extend_para=TempRun.para_list)
        # if options.SuiteStop.lower() == "yes":
        #     TempRun.batch_run(options)
        # else:
        #     TempRun.run_one_case(TempRun.item, options)
        setattr(options, "SuiteStop", "no")
        TempRun.run_one_case(TempRun.item, options)

    @staticmethod
    def batch_main():
        options, optparser = set_options(extend_para=TempRun.para_list)
        TempRun.batch_run(options)

    @staticmethod
    def batch_run(options):
        # 获取批量运行文件的内容
        root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # conf_path = options.SuiteConfPath if options.SuiteConfPath else os.path.join(root_path, "Config")
        conf_path = os.path.join(root_path, "Config")
        # conf = options.SuiteConf if options.SuiteConf else "PT.csv"

        if options.CSV.endswith(".csv"):
            conf = options.CSV
        else:
            conf = options.CSV + ".csv"

        file = os.path.join(conf_path, conf)
        # c = CsvLoader(file, ["CaseName", "CaseClassName", "Params", "Path"])
        c = CsvLoader(file, ["CaseName", "Params", "Path"])
        data = c.read_csv()
        print(f"=========csv data {data}=========")
        if len(data) >= 2:
            for row in data[1:]:
                case_file = importlib.import_module(f"{row['Path']}.{row['CaseName']}")
                case_class = getattr(case_file, row["CaseName"])
                # case_name = getattr(case_file, row["CaseName"])
                if row["Params"]:
                    p = TempRun.decode_params(row["Params"])
                    for name, value in p.items():
                        setattr(options, name, value)

                if row['CaseName'] == "InitParams":
                    result = TempRun.run_one_case(case_class, options)
                    TempRun.update_options(result, options)
                else:
                    if row['CaseName'] == "SendTransitInformation":
                        to_format = "%Y-%m-%d %H:%M:%S"
                        end_time = time.strftime(to_format, time.localtime())
                        setattr(options, "END_TIME", end_time)
                    TempRun.run_one_case(case_class, options)
                    time.sleep(10)

    @staticmethod
    def decode_params(params):
        data = {}
        p_list = params.split(":")
        for p in p_list:
            ps = p.split("=")
            data[ps[0]] = ps[1]
        return data

    @staticmethod
    def run_one_case(item, options):
        print(f"=================option is {options}==================")
        suite = Suite()
        if TempRun.suite_name:
            suite.name = TempRun.suite_name
        suite.options = options
        for num in range(options.CaseCycle):
            # for num in range(options.SuiteCycle):
            case = item(options)
            print(f"====================== item is {item} =========================")
            print(f"======================case is {case}==========================")
            case.ID = num
            suite.add_case(case)

        # sub_folder = getattr(options, "SubFolder", "")
        logger_factory = LoggerGet(item.__name__, options.LogFlag, options.LogPath, sub_folder=options.SubLog)
        suite.set_logger(logger_factory)
        result = suite.run()
        logger = logger_factory.logger
        for handler in logger.handlers[:]:  # make a copy of the list
            logger.removeHandler(handler)
        logger.info("------------------------------------------------------")
        return result

    @staticmethod
    def update_options(result, options):
        from_format = "%Y_%m_%d_%H_%M_%S"
        to_format = "%Y-%m-%d %H:%M:%S"
        if options.CSV.endswith(".csv"):
            level = options.CSV[:-4]
        else:
            level = options.CSV

        struct_time = time.strftime(from_format, time.localtime())
        start_time = trans_format(struct_time, from_format, to_format)
        options.SubLog = result.g_cfg.get_put() + "_" + level + "_" + result.g_cfg.get_sn() + "_" + struct_time
        # setattr(options, "RK", result.g_cfg.rk)
        # setattr(options, "SN", result.g_cfg.sn)
        # setattr(options, "START_TIME", start_time)
        result.g_cfg.set_start_time(start_time)
        setattr(options, "g_cfg", result.g_cfg)
