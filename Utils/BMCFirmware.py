#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Author  :   Rex Guo
@Contact :   Rex.Guo@luxshare-ict.com
@Software:   Utils
@File    :   BMCFirmware.py
@Time    :   2022/08/27 10:34:27
@Version :   1.0
@License :   Copyright ©LuxShare  2022 . All Rights Reserved.
@Desc    :   None
"""

import os
import sys
import requests
import subprocess

load_list = ["ancoan"]


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

from Cmd import Firmware
from Utils.DataBuffer import StrParser
from Lib.Config import YamlLoadConfig
from Lib.Error import Error


def has_attrs(*attrs):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            missing_attrs = []
            for attr in attrs:
                if getattr(self, attr) is None:
                    missing_attrs.append(attr)
            if len(missing_attrs) > 0:
                raise AttributeError(
                    "Cannot find required instance attribute: "
                    + " ".join(missing_attrs)
                )
            return func(self, *args, **kwargs)

        return wrapper

    return decorator


class LogChecker:
    def __init__(self, exec_command, logger):
        """
        [Fixed Args]
            exec_method: Template execute_run
        """
        self.exec = exec_command
        self.template_sel = None
        self.logger = logger

    def clear_sel(self):
        self.exec("ipmitool sel clear")

    def get_sel_template(self):
        """Take sel log of the first loop as template"""
        self.template_sel = self.get_sel()

    def get_sel(self):
        """Get Unordered sel log contents"""
        log_lines = self.exec("ipmitool sel list").get_origin_data().splitlines()
        log_mesgs = set(
            map(lambda line: "|".join(line.split("|")[3:]).strip(), log_lines)
        )  # Take the fields after the third vertical line
        return log_mesgs

    @has_attrs("exec")
    def check_sel(self):
        """
        Make comparison aginst first loop
        For any variant it will raise an error
        """
        if self.template_sel is None:
            self.logger.info("Take generated log as template(first loop)")
            self.template_sel = self.get_sel()
        else:
            current_loop_sel = self.get_sel()
            if not current_loop_sel.issubset(self.template_sel):
                unexpected_entries = current_loop_sel - self.template_sel
                raise Error(f"Found unexpected sel entries: {unexpected_entries}", 1)
            self.logger.info("SEL check pass")


class OutbandFwFlasher:
    def __init__(self, ip, user, password, logger):
        self.ip = ip
        self.user = user
        self.password = password
        self.logger = logger

    def get_tool_path(self, tool_name="redfish_upgrade"):
        config = YamlLoadConfig(cfg_name="Firmware.yaml").get_config()
        tool_path = config["tools"][tool_name]["path"]
        if not os.path.exists(tool_path):
            raise FileNotFoundError(f"Cannot find {tool_path}")
        self.tool_path = tool_path

    def flash(self, fw_path) -> StrParser:
        # Check firmware existence
        if not os.path.exists(fw_path):
            raise FileNotFoundError(f"Cannot find firmware: {fw_path}")
        # Check image extension
        if not (fw_path.endswith("tar") or fw_path.endswith("gz")):
            raise Error(f"Wrong image for the flash: {fw_path}", 1)
        with open(
                fw_path,
                "rb",
        ) as f:
            data = f.read()
        self.logger.info(f"Firmware path: {fw_path}")
        self.logger.info(f"Sending Outband Flashing POST request..")
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        response = requests.post(
            f"https://{self.ip}/redfish/v1/UpdateService",
            headers=headers,
            data=data,
            verify=False,
            auth=(self.user, self.password),
        )
        self.logger.info("Request sent. Response:")
        self.logger.info(response.text)
        return StrParser(response.text)

    def script_flash(self, fw_path) -> StrParser:
        """
        flash firmware using redfish-upgrade.pl
        """
        if not os.path.exists(fw_path):
            raise FileNotFoundError(f"Cannot find firmware: {fw_path}")
        # Check image extension
        if not (fw_path.endswith("tar") or fw_path.endswith("gz")):
            raise Error(f"Wrong image for the flash: {fw_path}", 1)
        flash_cmd = Firmware.Outband.script_flash.format(
            ip=self.ip,
            username=self.user,
            password=self.password,
            firmware_path=fw_path,
        )
        self.logger.info("Local Execute command: " + flash_cmd)
        cmd_elements = flash_cmd.split()
        if sys.platform.startswith("win"):
            cmd_elements.insert(0, "perl.exe")
        res = subprocess.run(
            cmd_elements,
            # capture_output=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="UTF-8",
        )
        if res.returncode != 0:
            raise Error(res.stderr, 1)
        output = res.stdout.strip() if len(res.stdout.strip()) > 0 else "Null"
        self.logger.info("Local Execute command ok, Output below: ")
        self.logger.info(output.strip())
        return StrParser(output)


class InbandFwFlasher:
    def __init__(self, logger, **kwargs):
        """
        [Fixed args]
        logger
        [Optional args]
        For redfish.pl Flash
                exec_method: Template execute_run
                bmc_conf: which contains bmc username and password
        For Offline socflash
                exec_ method: Template execute_run
        """
        self.logger = logger
        self.exec = kwargs.get("exec_method")
        self.bmc_conf = kwargs.get("bmc_conf")
        self.uut_conf = kwargs.get("uut_conf")

    @has_attrs("exec", "bmc_conf")
    def flash(self, fw_path: str) -> StrParser:
        # Check image extension
        if not (fw_path.endswith("tar") or fw_path.endswith("gz")):
            raise Error(f"Wrong image for the flash: {fw_path}", 1)
        res = self.exec(
            Firmware.Inband.flash.format(
                username=self.bmc_conf["username"],
                password=self.bmc_conf["password"],
                firmware_path=fw_path,
            ),
            i_exit_code=True,
        )
        return res

    @has_attrs("exec")
    def socflash(self, fw_path: str) -> StrParser:
        # Check image extension
        if not fw_path.endswith("mtd"):
            raise Error(f"Wrong image for the socflash: {fw_path}", 1)
        res = self.exec(
            "yes y | " + Firmware.Inband.socflash.format(firmware_path=fw_path),
            retry_expt=1,
        )
        return res

    @staticmethod
    def check_attribute(self, attr_list: int):
        missing_attrs = []
        for attr in attr_list:
            if getattr(self, attr) is None:
                missing_attrs.append(attr)
        if len(missing_attrs) > 0:
            raise AttributeError(
                "Cannot find required instance attribute: " + " ".join(missing_attrs)
            )


def check_channel(case_obj):
    self = case_obj
    bmc = self.config["BMC"]
    bmc_ip = bmc["ip_address"]
    bmc_user = bmc["username"]
    bmc_password = bmc["password"]
    self.logger.info("Start Test IPMI/Redfish Channel Function".center(50, "-"))
    origin_ssh = self.ssh
    with self.ssh_outband_connect():
        self.execute_run(f"ipmitool -I lanplus -H {bmc_ip} -U {bmc_user} -P {bmc_password} lan print 1")
        self.execute_run("curl -u admin:admin https://10.67.13.29/redfish/v1/Managers/bmc/EthernetInterfaces -k")
    self.ssh = origin_ssh
    self.logger.info("End Test IPMI/Redfish Channel Function".center(50, "-"))
